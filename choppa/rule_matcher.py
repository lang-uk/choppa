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
        self._start: int = 0
        self._end: int = self._text_len
        self.start: int = 0
        self.end: int = 0

        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        else:
            self.pattern = pattern

    def region(self, start: int, end: Union[int, None] = None) -> None:
        self._start = start
        if end is None:
            self._end = self._text_len
        else:
            self._end = end

    def _find_and_move_region(self, method: Callable) -> re.Match:
        # Special case for empty matchers
        if self._start > self._text_len:
            return None

        # Gosh, this shit is slow on big texts but it's the only
        # way I found to emulate ^ matching working together with the
        # Java's Matcher.region
        match = method(self._text[self._start:self._end])

        if match is not None:
            # Moving to the remainder
            # Also special case for empty matchers

            self.start = self._start + match.start()
            self.end = self._start + match.end()

            self.region(self._start + match.end() + (1 if match.start() == match.end() else 0))

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
        return f"{self.pattern}: <{self._start}, {self._end}>"


# class JavaMatcher:
#     """
#     Partial implementation of java's matcher class
#     """

#     def __init__(self, pattern: Union[str, re.Regex], text: str) -> None:
#         self._text: str = text
#         self._text_len: int = len(self._text)
#         self._start: int = 0
#         self._end: int = self._text_len
#         self.start: int = 0
#         self.end: int = 0
#         self.pseudo_caret_pattern: Union[re.Regex, None] = None

#         if isinstance(pattern, str):
#             self.pattern = re.compile(pattern)
#         else:
#             self.pattern = pattern

#         if "^" in self.pattern.pattern:
#             # print(self.pattern.pattern.replace("^|", "").replace("^", ""))
#             self.pseudo_caret_pattern = re.compile(self.pattern.pattern.replace("[^", "[[[").replace("^|", "").replace("^", "").replace("[[[", "[^"), self.pattern.flags)

#     def region(self, start: int, end: Union[int, None] = None) -> None:
#         self._start = start
#         if end is None:
#             self._end = self._text_len
#         else:
#             self._end = end

#     def _find_and_move_region(self, method: Callable) -> re.Match:
#         # Special case for empty matchers
#         if self._start > self._text_len:
#             return None

#         match = method(self._text, self._start, self._end)

#         if match is not None:
#             # Moving to the remainder
#             # Also special case for empty matchers
#             self.region(match.end() + (1 if match.start() == match.end() else 0))

#             self.start = match.start()
#             self.end = match.end()

#         return match

#     def search(self) -> re.Match:
#         if self.pseudo_caret_pattern is not None:
#             return self._find_and_move_region(self.pseudo_caret_pattern.match)
#         else:
#             return self._find_and_move_region(self.pattern.search)

#     def find(self) -> re.Match:
#         return self.search()

#     def match(self) -> re.Match:
#         return self._find_and_move_region(self.pattern.match)

#     def looking_at(self) -> re.Match:
#         return self.match()


#     def __str__(self) -> str:
#         return f"{self.pattern}: <{self._start}, {self._end}>"

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
        self.before_matcher: JavaMatcher = JavaMatcher(self.before_pattern, self.text)
        self.after_matcher: JavaMatcher = JavaMatcher(self.after_pattern, self.text)

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
            self.before_matcher.region(start)

        self.found = False

        while not self.found and self.before_matcher.search():
            self.after_matcher.region(self.before_matcher.end)
            self.found = self.after_matcher.looking_at() is not None


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

        return self.before_matcher.start

    def get_break_position(self) -> int:
        """
        @return position in text where text should be splitted according to last matching
        """
        return self.after_matcher.start

    def get_end_position(self) -> int:
        """
        @return position in text where the last matching ends
        """
        return self.after_matcher.end
