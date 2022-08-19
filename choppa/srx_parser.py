import pathlib
import regex as re  # type: ignore
from xml.sax.handler import ContentHandler
from xml.sax import parse as sax_parse

from typing import Union, Dict, List, Optional
import xmlschema  # type: ignore

from .structures import Rule, LanguageRule, LanguageMap
from .rule_manager import RuleManager


class SrxDocument:
    def __init__(
        self,
        cascade: bool = True,
        ruleset: Union[pathlib.Path, None, str] = None,
        validate_ruleset: Union[pathlib.Path, None, str] = None,
    ) -> None:
        """
        Creates empty document.
        cascade True if document is cascading
        ruleset a path to the srx xml file to be loaded (supply None to start with an empty doc)
        validate_ruleset a filepath to xsd (or None, to disable validation) to validate against DTD
        """
        self.cascade = cascade
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
            # Fixing irregularities in \h\v behavior
            # Both \p{H} and \p{V} were added in regex 2022.8.17
            # More details can be found here:
            # https://github.com/mrabarnett/mrab-regex/issues/477#issuecomment-1218409217
            regex = regex.replace(r"\h", r"\p{H}").replace(r"\v", r"\p{V}")

            pattern = re.compile(regex, flags=re.M | re.U | re.V1)
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
