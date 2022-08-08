import regex as re
from typing import Union
from .srx_parser import SrxDocument
from .structures import Rule


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
        self.before_pattern: re.Regex = document.compile(rule.before_pattern)
        self.after_pattern: re.Regex = document.compile(rule.after_pattern)
        # self.before_matcher = self.before_pattern.matcher(text)
        # self.after_matcher = self.after_pattern.matcher(text)

        # Adding aux variables to match the behavior of start/end regions
        # of java matcher
        self.bm_region_start: int = 0
        self.bm_region_end: int = len(self.text)
        self.am_region_start: int = 0
        self.am_region_end: int = len(self.text)
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

        if start is not None:
            self.bm_region_start = start
            self.bm_region_end = len(self.text)

        self.found = False
        for bm_match in self.before_pattern.finditer(self.text, self.bm_region_start, self.bm_region_end):
            self.bm_start = bm_match.start()
            self.bm_region_start = bm_match.end()
            self.am_region_start = bm_match.end()
            self.am_region_end = len(self.text)

            am_match = self.after_pattern.match(self.text, self.am_region_start, self.am_region_end)
            if am_match:
                self.found = True
                self.am_start = am_match.start()
                self.am_region_start = am_match.end()
                self.am_end = am_match.end()
            if self.found:
                break

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
