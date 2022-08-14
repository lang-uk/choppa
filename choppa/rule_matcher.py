import regex as re  # type: ignore
from typing import Union, Callable
from .srx_parser import SrxDocument
from .structures import Rule


class JavaMatcher:
    """
    Partial implementation of java's matcher class
    """

    def __init__(self, pattern: Union[str, re.Regex], text: str) -> None:
        self._text: str = text
        self._text_len: int = len(self._text)
        self.start: int = 0
        self.end: int = self._text_len

        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        else:
            self.pattern = pattern

    def region(self, start: int, end: Union[int, None] = None) -> None:
        self.start = start
        if end is None:
            self.end = self._text_len
        else:
            self.end = end

    def _find_and_move_region(self, method: Callable) -> re.Match:
        # Special case for empty matchers
        if self.start > self._text_len:
            return None

        match = method(self._text, self.start, self.end)

        if match is not None:
            # Moving to the remainder
            # Also special case for empty matchers
            self.region(match.end() + (1 if match.start() == match.end() else 0))

        return match

    def search(self) -> re.Match:
        return self._find_and_move_region(self.pattern.search)

    def find(self) -> re.Match:
        return self.search()

    def match(self) -> re.Match:
        return self._find_and_move_region(self.pattern.match)

    def looking_at(self) -> re.Match:
        return self.match()

    def __str__(self) -> str:
        return f"{self.pattern}: <{self.start}, {self.end}>"


class RuleMatcher:
    """
    Represents matcher finding subsequent occurrences of one rule.
    """

    def __init__(self, document: SrxDocument, rule: Rule, text: str) -> None:
        """
        Creates matcher.
        rule rule which will be searched in the text
        text text
        """

        self.document: SrxDocument = document
        self.rule: Rule = rule
        self.text: str = text
        self.text_len: int = len(text)
        self.before_pattern: re.Regex = document.compile(rule.before_pattern)
        self.after_pattern: re.Regex = document.compile(rule.after_pattern)

        # Adding aux variables to match the behavior of start/end regions
        # of java matcher
        self.bm_region_start: int = 0
        self.bm_region_end: int = self.text_len
        self.am_region_start: int = 0
        self.am_region_end: int = self.text_len
        self.bm_start: int = 0
        self.am_start: int = 0
        self.am_end: int = 0
        self.found = True

    def find(self, start: Union[int, None] = None) -> bool:
        """
        Finds next rule match after previously found.
        param start start position
        return true if rule has been matched
        """

        print(
            self.after_pattern,
            self.am_region_start,
            self.am_region_end,
            self.text[self.am_region_start : self.am_region_end],
        )

        if start is not None:
            self.bm_region_start = start
            self.bm_region_end = self.text_len

        self.found = False
        bm_match = self.before_pattern.search(self.text, self.bm_region_start, self.bm_region_end)

        while bm_match and not self.found:
            self.bm_start = bm_match.start()
            self.bm_region_start = bm_match.end() + 1
            self.am_region_start = bm_match.end()

            am_match = self.after_pattern.match(self.text, self.am_region_start, self.am_region_end)
            if am_match:
                self.found = True
                self.am_start = am_match.start()
                self.am_region_start = am_match.end()
                self.am_end = am_match.end()

            if self.bm_region_start == self.text_len:
                break

            if self.am_region_start == self.text_len:
                break

            bm_match = self.before_pattern.search(self.text, self.bm_region_start, self.bm_region_end)

        return self.found

    def hit_end(self) -> bool:
        """
        @return true if end of text has been reached while searching
        """
        return not self.found

    def get_start_position(self) -> int:
        """
        @return position in text where the last matching starts
        """

        return self.bm_start

    def get_break_position(self) -> int:
        """
        @return position in text where text should be splitted according to last matching
        """
        return self.am_start

    def get_end_position(self) -> int:
        """
        @return position in text where the last matching ends
        """
        return self.am_end
