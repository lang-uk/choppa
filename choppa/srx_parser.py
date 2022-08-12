import regex as re
from typing import Union, Dict, List, NamedTuple
from xml.sax.handler import ContentHandler

from .structures import Rule, LanguageRule, LanguageMap


class SrxDocument:
    def __init__(self, cascade: bool = True) -> None:
        """
        Creates empty document.
        cascade True if document is cascading
        """
        self.cascade = cascade
        self.language_map_list: List[LanguageMap] = []
        self.cache: Dict[str, object] = {}

    def add_language_map(self, pattern: str, language_rule: LanguageRule) -> None:
        """
        Add language map to this document.
        """
        self.language_map_list.append(LanguageMap(pattern, language_rule))

    def compile(self, regex: str) -> re.Regex:
        key: str = "PATTERN_" + regex

        pattern: re.Regex = self.cache.get(key, None)

        if pattern is None:
            pattern = re.compile(regex, flags=re.M | re.U)
            self.cache[key] = pattern

        return pattern

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

    SCHEMA: str = "net/loomchild/segment/res/xml/srx20.xsd"

    def __init__(self, document: SrxDocument) -> None:
        self.break_rule: bool = False
        self.before_break: list = []
        self.after_break: list = []
        self.language_rule: Union[LanguageRule, None] = None
        self.language_rule_map: Dict[str, LanguageRule] = {}
        self.element_name: Union[str, None] = None
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


# if __name__ == "__main__":
#     from xml.sax import parse

#     parse("/Users/dchaplinsky/Projects/choppa/data/example1.srx", SRXHandler(document=SrxDocument()))
