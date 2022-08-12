import regex as re
from typing import NamedTuple, List, Union


class Rule(NamedTuple):
    is_break: bool
    before_pattern: str
    after_pattern: str


class LanguageRule:
    def __init__(self, name: str, rules: Union[List[Rule], None] = None):
        self.name: str = name
        self.rules: List[Rule] = []
        if rules is not None:
            self.rules = rules

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    # TODO: __str__?


class LanguageMap:
    """
    Represents mapping between language code pattern and language rule.
    """

    def __init__(self, pattern: str, language_rule: LanguageRule) -> None:
        """
        Creates mapping.

        pattern language code pattern
        language_rule language rule
        """
        self.language_pattern: re.Regex = re.compile(pattern)
        self.language_rule = language_rule

    def matches(self, language_code: str) -> bool:
        return bool(self.language_pattern.fullmatch(language_code))

    # TODO: __str__?
