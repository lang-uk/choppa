import io
import regex as re  # type: ignore
from typing import List, Union, Optional

from .structures import LanguageRule, Rule
from .srx_parser import SrxDocument
from .rule_matcher import RuleMatcher, JavaMatcher
from .text_manager import TextManager
from .rule_manager import RuleManager
from .utils import create_lookbehind_pattern


MAX_INT_VALUE: int = 2 ** 31 - 1


class AbstractTextIterator:
    """
    Represents abstract text iterator. Responsible for implementing remove
    operation.
    """

    DEFAULT_BUFFER_LENGTH: int = 1024 * 1024
    # Maximum length of a regular expression construct that occurs in lookbehind.
    # Default max lookbehind construct length parameter.
    DEFAULT_MAX_LOOKBEHIND_CONSTRUCT_LENGTH: int = 100

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
    def __init__(
        self,
        document: SrxDocument,
        language_code: str,
        text: str,
        max_lookbehind_construct_length: int = AbstractTextIterator.DEFAULT_MAX_LOOKBEHIND_CONSTRUCT_LENGTH,
    ) -> None:
        """
        Legacy alert: this is the implementation of the legacy accurate iterator
        from the original segment package. It's been known for slow speed on a large
        texts and doesn't allow to work on streams. Use SrxTextIterator instead

        Creates text iterator that obtains language rules form given document
        using given language code. To retrieve language rules calls
        SrxDocument.getLanguageRuleList(String).

        document document containing language rules
        language_code language code to select the rules
        text
        """

        self.language_rule_list: List[LanguageRule] = document.get_language_rule_list(language_code)
        self.text: str = text
        self.segment: Optional[str] = None
        self.start_position: int = 0
        self.end_position: int = 0

        self.rule_matcher_list: List[RuleMatcher] = []
        for language_rule in self.language_rule_list:
            for rule in language_rule.rules:
                if not rule.is_break:
                    rule = Rule(
                        is_break=rule.is_break,
                        before_pattern=create_lookbehind_pattern(rule.before_pattern, max_lookbehind_construct_length),
                        after_pattern=rule.after_pattern,
                    )

                matcher: RuleMatcher = RuleMatcher(
                    document=document, rule=rule, text=text, max_lookaround_len=max_lookbehind_construct_length
                )

                if not rule.is_break:
                    matcher.before_matcher.use_transparent_bounds = True

                self.rule_matcher_list.append(matcher)

    def __next__(self) -> str:
        """
        Finds the next match.
        Returns the next segment, or null if it does not exist
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

    def get_min_matcher(self) -> Optional[RuleMatcher]:
        """
        Returns an iterator of the first match hit
        """

        min_position: int = MAX_INT_VALUE
        min_matcher: Optional[RuleMatcher] = None
        for matcher in self.rule_matcher_list:
            if matcher.get_break_position() < min_position:
                min_position = matcher.get_break_position()
                min_matcher = matcher
        return min_matcher


class SrxTextIterator(AbstractTextIterator):
    """
    Represents text iterator splitting text according to rules in SRX file.

    The algorithm idea is as follows:

    <pre>
    1. Rule matcher list is created based on SRX file and language. Each rule
       matcher is responsible for matching before break and after break regular
       expressions of one break rule.
    2. Each rule matcher is matched to the text. If the rule was not found the
       rule matcher is removed from the list.
    3. First rule matcher in terms of its break position in text is selected.
    4. List of exception rules corresponding to break rule is retrieved.
    5. If none of exception rules is matching in break position then
       the text is marked as split and new segment is created. In addition
       all rule matchers are moved so they start after the end of new segment
       (which is the same as break position of the matched rule).
    6. All the rules that have break position behind last matched rule
       break position are moved until they pass it.
    7. If segment was not found the whole process is repeated.
    </pre>

    In streaming version of this algorithm character buffer is searched.
    When the end of it is reached or break position is in the margin
    (break position &gt; buffer size - margin) and there is more text,
    the buffer is moved in the text until it starts after last found segment.
    If this happens rule matchers are reinitialized and the text is searched again.
    Streaming version has a limitation that read buffer must be at least as long
    as any segment in the text.

    As this algorithm uses lookbehind extensively but Java does not permit
    infinite regular expressions in lookbehind, so some patterns are finitized.
    For example a* pattern will be changed to something like a{0,100}.

    @author loomchild, Dmytro Chaplynskyi
    """

    #  Margin size. Used in streaming splitter.
    #  If rule is matched but its position is in the margin
    #  (position &gt; buffer_length - margin) then the matching is ignored,
    #  and more text is read and rule is matched again.
    # Default margin size.
    DEFAULT_MARGIN: int = 128

    def __init__(
        self,
        document: SrxDocument,
        language_code: str,
        text: Union[str, io.TextIOBase],
        buffer_length: int = AbstractTextIterator.DEFAULT_BUFFER_LENGTH,
        max_lookbehind_construct_length: int = AbstractTextIterator.DEFAULT_MAX_LOOKBEHIND_CONSTRUCT_LENGTH,
        margin: int = DEFAULT_MARGIN,
    ) -> None:
        """
        Creates text iterator that obtains language rules from given document
        using given language code. This is streaming constructor - it reads
        text from reader using buffer with given size and margin. Single
        segment cannot be longer than buffer size.
        If rule is matched but its position is in the margin
        (position &gt; buffer_length - margin) then the matching is ignored,
        and more text is read and rule is matched again.
        This is needed because incomplete rule can be located at the end of the
        buffer and never matched.
        """

        self.buffer_length: int = buffer_length
        self.max_lookbehind_construct_length: int = max_lookbehind_construct_length
        self.margin: int = margin

        if isinstance(text, str):
            self.text_manager: TextManager = TextManager(text=text)
            self.margin = 0
        else:
            self.text_manager = TextManager(reader=text, buffer_length=self.buffer_length)

        self.document: SrxDocument = document
        self.language_rule_list: List[LanguageRule] = document.get_language_rule_list(language_code)
        self.segment: Optional[str] = None
        self.start_position: int = 0
        self.end_position: int = 0
        self.rule_manager: RuleManager = self.document.get_rule_manager(
            self.language_rule_list, self.max_lookbehind_construct_length
        )

    def init_matchers(self) -> None:
        # Initializes matcher list according to rules from rule_manager and
        # text from text_manager.

        self.rule_matcher_list: List[RuleMatcher] = []
        for rule in self.rule_manager.break_rule_list:
            matcher: RuleMatcher = RuleMatcher(
                document=self.document,
                rule=rule,
                text=self.text_manager.get_text(),
                max_lookaround_len=self.max_lookbehind_construct_length,
            )
            matcher.find()
            if not matcher.hit_end():
                self.rule_matcher_list.append(matcher)

    # TODO: here and below DRY
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

    def get_min_matcher(self) -> Optional[RuleMatcher]:
        """
        Returns an iterator of the first match hit
        """

        min_position: int = MAX_INT_VALUE
        min_matcher: Optional[RuleMatcher] = None
        for matcher in self.rule_matcher_list:
            if matcher.get_break_position() < min_position:
                min_position = matcher.get_break_position()
                min_matcher = matcher

        return min_matcher

    def is_exception(self, rule_matcher: RuleMatcher) -> bool:
        """
        Returns true if there are no exception rules preventing given
        rule matcher from breaking the text.
        @param ruleMatcher rule matcher
        @return true if rule matcher breaks the text
        """

        pattern: re.Regex = self.rule_manager.get_exception_pattern(rule_matcher.rule)
        if pattern is not None:
            matcher = JavaMatcher(
                pattern=pattern,
                text=self.text_manager.get_text(),
                max_lookaround_len=self.max_lookbehind_construct_length,
            )

            matcher.use_transparent_bounds = True
            matcher.region(rule_matcher.get_break_position())
            res: bool = bool(matcher.looking_at())
            return not res
        else:
            return True

    def __next__(self) -> str:
        """
        Finds the next match.
        Returns the next segment, or null if it does not exist
        """

        # TODO: replace with an iterator/generator
        if self.has_next():
            # Initialize matchers before first search.
            if self.segment is None:
                self.init_matchers()

            found: bool = False

            while not found:
                min_matcher: Optional[RuleMatcher] = self.get_min_matcher()

                if min_matcher is None and not self.text_manager.has_more_text():
                    found = True
                    self.end_position = len(self.text_manager.get_text())
                else:
                    if self.text_manager.has_more_text() and (
                        min_matcher is None
                        or min_matcher.get_break_position() > self.text_manager.buffer_length - self.margin
                    ):
                        if self.start_position == 0:
                            # TODO: proper exceptions
                            raise Exception(
                                "Buffer too short"
                                + " - it must be at least as long as the"
                                + " longest segment in the text; "
                                + "try using the bufferLength option"
                            )

                        self.text_manager.read_text(self.start_position)
                        self.init_matchers()
                        min_matcher = self.get_min_matcher()

                    self.end_position = min_matcher.get_break_position()

                    if self.end_position > self.start_position:
                        found = self.is_exception(min_matcher)

                        if found:
                            self.cut_matchers()

                self.move_matchers()

            self.segment = self.text_manager.get_text()[self.start_position : self.end_position]
            self.start_position = self.end_position

            return self.segment
        else:
            raise StopIteration

    def has_next(self) -> bool:
        return self.text_manager.has_more_text() or self.start_position < len(self.text_manager.get_text())
