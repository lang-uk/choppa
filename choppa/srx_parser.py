from typing import Union, Dict, List
from xml.sax.handler import ContentHandler

# from .structures import Rule, LanguageRule
from typing import NamedTuple


class Rule(NamedTuple):
    is_break: bool
    before_pattern: str
    after_pattern: str


class LanguageRule(NamedTuple):
    name: str
    rules: List[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)



class SRXHandler(ContentHandler):
    SCHEMA: str = "net/loomchild/segment/res/xml/srx20.xsd"
    break_rule: bool = False
    before_break: list = []
    after_break: list = []
    language_rule: Union[LanguageRule, None] = None
    language_rule_map: Dict[str, LanguageRule] = {}
    element_name: Union[str, None] = None

    def startDocument(self):
        self.reset_rule()

    def reset_rule(self):
        self.break_rule = False
        self.before_break = []
        self.after_break = []

    def startElement(self, name, attrs):
        self.element_name = name
        print(f"BEGIN: <{name}>, {attrs.keys()}")
        if name == "header":
            # document.setCascade(attrs.get("cascade") == "yes")
            pass
        elif name == "languagerule":
            language_rule_name: str = attrs.get("languagerulename")
            self.language_rule = LanguageRule(language_rule_name)
            self.language_rule_map[language_rule_name] = self.language_rule
        elif name == "languagemap":
            language_pattern: str = attrs.get("languagepattern")
            language_rule_name: str = attrs.get("languagerulename")
            # document.addLanguageMap(language_pattern, languageRuleMap.get(language_rule_name));
        elif name == "rule":
            self.break_rule = attrs.get("break") != "no"

    def endElement(self, name):
        self.element_name = None
        print(f"END: </{name}>")
        if name == "rule":
            rule = Rule(self.break_rule, "".join(self.before_break), "".join(self.after_break))
            self.language_rule.add_rule(rule)
            self.reset_rule()

    def characters(self, content):
        if content.strip() != "":
            print("CONTENT:", repr(content))

        if self.element_name == "beforebreak":
            self.before_break.append(content)
        elif self.element_name == "afterbreak":
            self.after_break.append(content)


if __name__ == "__main__":
    from xml.sax import parse

    parse("/Users/dchaplinsky/Projects/hashek/choppa/data/example1.srx", SRXHandler())
