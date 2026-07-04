import pathlib
import regex as re  # type: ignore
from xml.sax.handler import ContentHandler
from xml.sax import parse as sax_parse

from typing import Union, Dict, List, Optional
import xmlschema  # type: ignore

from .structures import Rule, LanguageRule, LanguageMap
from .rule_manager import RuleManager


# Java-only regex constructs that have to be translated before the pattern
# can be compiled by the regex package. The lookbehind guard (same idiom as
# in utils.py) makes sure we only touch constructs preceded by an even
# number of backslashes, i.e. we never rewrite an escaped literal backslash
# followed by "h"/"v".
#
# \h and \v are Java's horizontal/vertical whitespace classes; in Python
# patterns \v is the literal LINE TABULATION escape, so both are mapped to
# the equivalent \p{H}/\p{V} properties added to the regex package in
# 2022.8.17 (https://github.com/mrabarnett/mrab-regex/issues/477).
# \p{H}/\p{V} match Java's classes exactly, while the regex package's own
# \h misses U+180E.
#
# (?U) is Java's UNICODE_CHARACTER_CLASS inline flag (used by LanguageTool
# rules to fix the JDK >= 19 \b regression); Python character classes are
# Unicode-aware by default for str patterns, so the flag is dropped.
JAVA_CONSTRUCT_PATTERN: re.Regex = re.compile(
    r"(?<=(?<!\\)(?:\\\\){0,100})(?:\\h|\\v)|\(\?U\)"
)
JAVA_CONSTRUCT_REPLACEMENTS: Dict[str, str] = {
    r"\h": r"\p{H}",
    r"\v": r"\p{V}",
    "(?U)": "",
}


def translate_java_regex(pattern: str) -> str:
    """
    Translates Java-only regex constructs (\\h, \\v, (?U)) into their
    Python regex-package equivalents. See JAVA_CONSTRUCT_PATTERN above.
    """
    return JAVA_CONSTRUCT_PATTERN.sub(
        lambda match: JAVA_CONSTRUCT_REPLACEMENTS[match.group()], pattern
    )


class SrxDocument:
    # V1 enables Java-style character class operations like
    # [\p{L}&&[^rwn]] used by the LanguageTool rules. MULTILINE is
    # deliberately NOT set: java.util.regex does not use it, so with it
    # the ^-anchored rules would fire at every line start and the output
    # would diverge from the original segment/LanguageTool behavior.
    BASE_PATTERN_FLAGS: int = re.U | re.V1

    def __init__(
        self,
        cascade: bool = True,
        ruleset: Union[pathlib.Path, None, str] = None,
        validate_ruleset: Union[pathlib.Path, None, str] = None,
        pattern_flags: int = 0,
    ) -> None:
        """
        Creates empty document.
        cascade True if document is cascading
        ruleset a path to the srx xml file to be loaded (supply None to start with an empty doc)
        validate_ruleset a filepath to xsd (or None, to disable validation) to validate against DTD
        pattern_flags extra regex flags OR-ed into every compiled rule
            (analog of segment 2.0.4 defaultPatternFlags). For example,
            pass regex.M to make ^-anchored rules match at line starts
            (pre-1.0 choppa behavior, diverges from Java).
        """
        self.cascade = cascade
        self.pattern_flags: int = self.BASE_PATTERN_FLAGS | pattern_flags
        self.language_map_list: List[LanguageMap] = []
        self.regex_cache: Dict[str, re.Regex] = {}
        self.rule_manager_cache: Dict[str, RuleManager] = {}

        if ruleset is not None:
            if validate_ruleset is not None:
                schema: xmlschema.XMLSchema = xmlschema.XMLSchema(str(validate_ruleset))

                schema.validate(str(ruleset))

            sax_parse(str(ruleset), SRXHandler(document=self))

    def add_language_map(self, pattern: str, language_rule: LanguageRule) -> None:
        """
        Add language map to this document.
        """
        self.language_map_list.append(LanguageMap(pattern, language_rule))

    def compile(self, regex: str) -> re.Regex:
        """
        Compiles given pattern as regex.Regex (V1), caches it
        """
        key: str = "PATTERN_" + regex

        pattern: Optional[re.Regex] = self.regex_cache.get(key, None)

        if pattern is None:
            pattern = re.compile(translate_java_regex(regex), flags=self.pattern_flags)
            self.regex_cache[key] = pattern

        return pattern

    def get_rule_manager(
        self, language_rule_list: List[LanguageRule], max_lookbehind_construct_length: int
    ) -> RuleManager:
        key: str = f"RULE_MANAGER_{language_rule_list}_{max_lookbehind_construct_length}"

        rule_manager: Optional[RuleManager] = self.rule_manager_cache.get(key, None)

        if rule_manager is None:
            rule_manager = RuleManager(self, language_rule_list, max_lookbehind_construct_length)
            self.rule_manager_cache[key] = rule_manager

        return rule_manager

    def get_language_rule_list(self, language_code: str) -> List[LanguageRule]:
        """
        If cascade is true then returns all language rules matching given
        language code. If cascade is false returns first language rule matching
        given language code. If no matching language rules are found returns
        empty list.

        language_code language code, for example en_US
        matching language rules

        """

        matching_language_rule_list: List[LanguageRule] = []
        for language_map in self.language_map_list:
            if language_map.matches(language_code):
                matching_language_rule_list.append(language_map.language_rule)
                if not self.cascade:
                    break
        return matching_language_rule_list


class SRXHandler(ContentHandler):
    """
    Represents SRX 2.0 document parser. Responsible for creating and initializing
    Document according to given SRX. Uses SAX.
    """

    def __init__(self, document: SrxDocument) -> None:
        self.break_rule: bool = False
        self.before_break: list = []
        self.after_break: list = []
        self.language_rule: Optional[LanguageRule] = None
        self.language_rule_map: Dict[str, LanguageRule] = {}
        self.element_name: Optional[str] = None
        self.document = document

    def startDocument(self):
        self.reset_rule()

    def reset_rule(self):
        self.break_rule = False
        self.before_break = []
        self.after_break = []

    def startElement(self, name, attrs):
        self.element_name = name

        if name == "header":
            self.document.cascade = attrs.get("cascade") == "yes"
        elif name == "languagerule":
            language_rule_name: str = attrs.get("languagerulename")
            self.language_rule = LanguageRule(language_rule_name)
            self.language_rule_map[language_rule_name] = self.language_rule
        elif name == "languagemap":
            language_pattern: str = attrs.get("languagepattern")
            language_rule_name: str = attrs.get("languagerulename")
            self.document.add_language_map(language_pattern, self.language_rule_map.get(language_rule_name))
        elif name == "rule":
            self.break_rule = attrs.get("break") != "no"

    def endElement(self, name):
        self.element_name = None

        if name == "rule":
            rule = Rule(self.break_rule, "".join(self.before_break), "".join(self.after_break))
            self.language_rule.add_rule(rule)
            self.reset_rule()

    def characters(self, content):
        if self.element_name == "beforebreak":
            self.before_break.append(content)
        elif self.element_name == "afterbreak":
            self.after_break.append(content)
