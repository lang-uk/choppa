import regex as re
from typing import List, Union

from .structures import LanguageRule
from .srx_parser import SrxDocument
from .rule_matcher import RuleMatcher


MAX_INT_VALUE: int = 2 ** 31 - 1


class AbstractTextIterator:
    """
    Represents abstract text iterator. Responsible for implementing remove
    operation.
    """

    DEFAULT_BUFFER_LENGTH: int = 1024 * 1024
    def to_string(self, language_rule_list: List[LanguageRule]) -> str:
        result = []

        for language_rule in language_rule_list:
            result.append(language_rule.name)

        return "".join(result)  # ??

    def __iter__(self):
        return self

    def __next__(self) -> str:
        raise StopIteration


class AccurateSrxTextIterator(AbstractTextIterator):
    def __init__(self, document: SrxDocument, language_code: str, text: str) -> None:
        """
        Creates text iterator that obtains language rules form given document
        using given language code. To retrieve language rules calls
        SrxDocument.getLanguageRuleList(String).

        document document containing language rules
        language_code language code to select the rules
        text
        """

        self.language_rule_list: List[LanguageRule] = document.get_language_rule_list(language_code)
        self.text: str = text
        self.segment: Union[str, None] = None
        self.start_position: int = 0
        self.end_position: int = 0

        self.rule_matcher_list: List[RuleMatcher] = []
        for language_rule in self.language_rule_list:
            for rule in language_rule.rules:
                matcher: RuleMatcher = RuleMatcher(document, rule, text)
                self.rule_matcher_list.append(matcher)

    def __next__(self) -> str:
        """
        Finds the next match.
        Returns the next segment, or null if it does not exist
        IOSRuntimeException Thrown when an error occurs while reading the stream
        """

        # TODO: replace with an iterator/generator
        if self.has_next():
            # Initialize matchers before first search.
            if self.segment is None:
                self.init_matchers()

            found: bool = False

            while len(self.rule_matcher_list) and not found:
                min_matcher: RuleMatcher = self.get_min_matcher()
                self.end_position = min_matcher.get_break_position()
                if min_matcher.rule.is_break and self.end_position > self.start_position:
                    found = True
                    self.cut_matchers()

                self.move_matchers()

            if not found:
                self.end_position = len(self.text)

            self.segment = self.text[self.start_position : self.end_position]
            self.start_position = self.end_position

            return self.segment
        else:
            raise StopIteration

    def has_next(self) -> bool:
        """
        Returns true when more segments are available
        """
        return self.start_position < len(self.text)

    def init_matchers(self) -> None:
        for matcher in self.rule_matcher_list[:]:
            matcher.find()
            if matcher.hit_end():
                # TODO: More optimal removal of rules
                self.rule_matcher_list.remove(matcher)

    def move_matchers(self) -> None:
        """
        Moves iterators to the next position if necessary.

        """
        for matcher in self.rule_matcher_list[:]:
            while matcher.get_break_position() <= self.end_position:
                matcher.find()
                if matcher.hit_end():
                    # TODO: More optimal removal of rules
                    self.rule_matcher_list.remove(matcher)
                    break

    def cut_matchers(self) -> None:
        """
        Move matchers that start before previous segment end.
        """

        for matcher in self.rule_matcher_list[:]:
            if matcher.get_start_position() < self.end_position:
                matcher.find(self.end_position)
                if matcher.hit_end():
                    # TODO: More optimal removal of rules
                    self.rule_matcher_list.remove(matcher)

    def get_min_matcher(self) -> Union[RuleMatcher, None]:
        """
        Returns an iterator of the first match hit
        """

        min_position: int = MAX_INT_VALUE
        min_matcher: Union[RuleMatcher, None] = None
        for matcher in self.rule_matcher_list:
            if matcher.get_break_position() < min_position:
                min_position = matcher.get_break_position()
                min_matcher = matcher
        return min_matcher
