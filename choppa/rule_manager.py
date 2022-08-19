import regex as re  # type: ignore
from typing import List, Dict, Optional

from choppa.structures import LanguageRule, Rule
from choppa.utils import finitize

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .srx_parser import SrxDocument


# TODO: tests?


class RuleManager:
    def __init__(
        self,
        document: "SrxDocument",
        language_rule_list: List[LanguageRule],
        max_lookbehind_construct_length: int,
    ) -> None:
        """
        Constructor. Responsible for retrieving rules from SRX document for
        given language code, constructing patterns and storing them in
        quick accessible format.
        Adds break rules to break_rule_list and constructs
        corresponding exception patterns in exception_pattern_map
        Uses document cache to store rules and patterns.
        @param document SRX document
        @param language_rule_list list of language rules
        @param max_lookbehind_construct_length Maximum length of regular expression in lookbehind (see util.finitize)
        """
        self.document = document
        self.max_lookbehind_construct_length = max_lookbehind_construct_length

        self.break_rule_list: List[Rule] = []
        self.exception_pattern_map: Dict[Rule, Optional[re.Regex]] = {}

        exception_pattern_builder: str = ""

        for language_rule in language_rule_list:
            for rule in language_rule.rules:
                if rule.is_break:
                    self.break_rule_list.append(rule)

                    exception_pattern: Optional[re.Regex] = None

                    if exception_pattern_builder:
                        exception_pattern = document.compile(exception_pattern_builder)
                    else:
                        exception_pattern = None

                    self.exception_pattern_map[rule] = exception_pattern
                else:
                    if exception_pattern_builder:
                        exception_pattern_builder += "|"

                    pattern_string: str = self.create_exception_pattern_string(rule)
                    exception_pattern_builder += pattern_string

    def get_exception_pattern(self, break_rule: Rule) -> re.Regex:
        """
        @param break_rule
        @return exception pattern corresponding to given break rule
        """

        return self.exception_pattern_map.get(break_rule)

    def create_exception_pattern_string(self, rule: Rule) -> str:
        """
        Creates exception pattern string that can be matched in the place
        where break rule was matched. Both parts of the rule
        (before_pattern and after_pattern) are incorporated
        into one pattern.
        before_pattern is used in lookbehind, therefore it needs to be
        modified so it matches finite string (contains no *, + or {n,}).
        @param rule exception rule
        @return string containing exception pattern
        """

        pattern_builder: str = "(?:"

        # As Java does not allow infinite length patterns
        # in lookbehind, before pattern need to be shortened.
        # TODO: validate if it's still true for Python
        before_pattern: str = finitize(rule.before_pattern, self.max_lookbehind_construct_length)
        after_pattern: str = rule.after_pattern

        if before_pattern:
            pattern_builder += "(?<=" + before_pattern + ")"

        if after_pattern:
            pattern_builder += "(?=" + after_pattern + ")"

        pattern_builder += ")"

        return pattern_builder
