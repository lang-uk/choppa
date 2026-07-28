r"""
Paragraph breaks fire on ASCII whitespace only.

LanguageTool's ByTwoLineBreaks rule spells out what it accepts between
the two newlines -- `\r?\n[ \t\n\x0B\f\r]*\r?\n[\t]*` -- instead of
writing `\s`, because it compiles every rule with `(?U)` and Unicode
`\s` would let a paragraph break span an NBSP.

Python's `\s` is Unicode-aware as well, so while the rule still said
`\r?\n\s*\r?\n` choppa broke paragraphs that the Java original kept
whole. No benchmark corpus ever hit it. Every expectation below is
byte-verified against the Java segment CLI.
"""

import unittest
from typing import List

from choppa import SrxTextIterator

from .conftest import get_document


# Between two newlines, runs of these end a paragraph.
ASCII_SEPARATORS = ["", " ", "  ", "\t", "\x0b", "\x0c", "\r", " \t "]

# Whitespace outside that set does not, however space-like it looks.
UNICODE_SEPARATORS = [
    "\xa0",  # NO-BREAK SPACE
    "\x85",  # NEXT LINE
    " ",  # OGHAM SPACE MARK
    " ",  # FIGURE SPACE
    " ",  # LINE SEPARATOR
    " ",  # NARROW NO-BREAK SPACE
    "　",  # IDEOGRAPHIC SPACE
]

# Neither half carries sentence-final punctuation, so a paragraph rule is
# the only thing that can split these.
PARAGRAPHS = [
    ("uk_two", "Заголовок", "Перший абзац"),
    ("en_two", "Heading", "First paragraph"),
]


class ParagraphBreakTest(unittest.TestCase):
    maxDiff = None

    def segments(self, language: str, text: str) -> List[str]:
        return list(SrxTextIterator(get_document(), language, text))

    def test_ascii_whitespace_ends_a_paragraph(self) -> None:
        for language, head, tail in PARAGRAPHS:
            for separator in ASCII_SEPARATORS:
                with self.subTest(language=language, separator=separator):
                    self.assertEqual(
                        [f"{head}\n{separator}\n", tail],
                        self.segments(language, f"{head}\n{separator}\n{tail}"),
                    )

    def test_unicode_whitespace_does_not(self) -> None:
        for language, head, tail in PARAGRAPHS:
            for separator in UNICODE_SEPARATORS:
                with self.subTest(language=language, separator=separator):
                    text = f"{head}\n{separator}\n{tail}"
                    self.assertEqual([text], self.segments(language, text))

    def test_paragraph_separator_is_a_language_rule_not_a_paragraph_one(self) -> None:
        # U+2029 is outside ByTwoLineBreaks' character class too, but the
        # Ukrainian rules match `\v` (`\p{V}` covers it) and do break
        # here, where English has no such rule. Java agrees on both.
        self.assertEqual(
            ["Заголовок\n ", "\nПерший абзац"],
            self.segments("uk_two", "Заголовок\n \nПерший абзац"),
        )
        self.assertEqual(
            ["Heading\n \nFirst paragraph"],
            self.segments("en_two", "Heading\n \nFirst paragraph"),
        )
