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

        if start is not None:
            self.bm_region_start = start
            self.bm_region_end = self.text_len


        # public boolean find() {
        #     found = false;
        #     while ((!found) && beforeMatcher.find()) {
        #         afterMatcher.region(beforeMatcher.end(), text.length());
        #         found = afterMatcher.lookingAt();
        #     }
        #     return found;
        # }

        # print("here", start)
        self.found = False
        bm_match = self.before_pattern.search(self.text, self.bm_region_start, self.bm_region_end)

        while bm_match and not self.found:
            self.bm_start = bm_match.start()
            self.bm_region_start = bm_match.end() + 1
            self.am_region_start = bm_match.end()
            self.am_region_end = self.text_len

            am_match = self.after_pattern.match(self.text, self.am_region_start, self.am_region_end)
            if am_match:
                self.found = True
                self.am_start = am_match.start()
                self.am_region_start = am_match.end()
                self.am_end = am_match.end()

            if self.bm_region_start == self.text_len:
                break

            bm_match = self.before_pattern.search(self.text, self.bm_region_start, self.bm_region_end)

        # print(bm_match, self.found)
        # raise Exception("Fuck you")

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
