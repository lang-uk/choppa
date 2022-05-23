from typing import NamedTuple, List


class Rule(NamedTuple):
    is_break: bool
    before_pattern: str
    after_pattern: str


class LanguageRule(NamedTuple):
    name: str
    rules: List[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
