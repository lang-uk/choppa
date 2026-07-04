import regex as re  # type: ignore
from typing import Optional
from .srx_parser import SrxDocument
from .structures import Rule


class RuleMatcher:
    """
    Represents matcher finding subsequent occurrences of one rule.

    Pure position-based implementation on top of the regex package.
    It replicates java.util.regex.Matcher semantics that the original
    net.loomchild.segment RuleMatcher relies on:

    * ``Matcher.find()`` continues from the end of the previous match,
      advancing one extra character if the previous match was zero-width
      (Java's implicit empty-match bump — load-bearing for the whole
      algorithm, since exception rules wrapped in lookbehind produce
      zero-width matches only);
    * ``Matcher.region(start, len); Matcher.lookingAt()`` for the after
      pattern is equivalent to ``pattern.match(text, start)`` in Python:
      the match is anchored at ``start`` while lookbehind constructs can
      still inspect the text before it.

    Verified byte-identical to segment 2.0.3 (ultimate algorithm) on a
    100k-line real-world corpus.
    """

    __slots__ = (
        "document",
        "rule",
        "text",
        "text_len",
        "before_pattern",
        "after_pattern",
        "found",
        "_position",
        "_start_position",
        "_break_position",
        "_end_position",
    )

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
        self.found: bool = True

        self._position: int = 0
        self._start_position: int = 0
        self._break_position: int = 0
        self._end_position: int = 0

    def find(self, start: Optional[int] = None) -> bool:
        """
        Finds next rule match after previously found.
        param start start position
        return true if rule has been matched
        """

        if start is not None:
            self._position = start

        self.found = False

        text = self.text
        search_before = self.before_pattern.search
        match_after = self.after_pattern.match
        position = self._position

        while position <= self.text_len:
            before_match = search_before(text, position)
            if before_match is None:
                break

            break_position: int = before_match.end()
            # Java Matcher.find(): restart at the end of the previous
            # match, one character further if the match was zero-width.
            if break_position == before_match.start():
                position = break_position + 1
            else:
                position = break_position

            after_match = match_after(text, break_position)
            if after_match is not None:
                self.found = True
                self._start_position = before_match.start()
                self._break_position = break_position
                self._end_position = after_match.end()
                break

        self._position = position
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
        return self._start_position

    def get_break_position(self) -> int:
        """
        @return position in text where text should be splitted according to last matching
        """
        return self._break_position

    def get_end_position(self) -> int:
        """
        @return position in text where the last matching ends
        """
        return self._end_position

    def __str__(self) -> str:
        return f"{self.before_pattern.pattern}: {self.after_pattern.pattern} <{self._position}>"
