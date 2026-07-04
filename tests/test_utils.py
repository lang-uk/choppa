import unittest

import regex as re

from choppa.utils import remove_block_quotes, finitize, translate_java_regex


class UtilsTest(unittest.TestCase):
    def test_remove_block_quotes(self) -> None:
        QUOTED_PATTERN: str = "\\Q\\a\\Qaa\\\\Ebb\\Q\\E\\Qcc\\Edd"
        EXPECTED_UNQUOTED_PATTERN: str = "\\\\\\a\\\\\\Q\\a\\a\\\\bb\\c\\cdd"

        self.assertEqual(EXPECTED_UNQUOTED_PATTERN, remove_block_quotes(QUOTED_PATTERN))

    def testFinitize(self) -> None:
        INFINITE_PATTERN: str = "a*b\\*\\\\+c+d\\+\\\\\\\\*e++f{1,4}+g{3,}+h{1}+\\Qa+\\E"
        EXPECTED_FINITE_PATTERN: str = (
            "a{0,100}b\\*\\\\{1,100}c{1,100}d\\+\\\\\\\\{0,100}e{1,100}+f{1,4}+g{3,100}+h{1}+\\a\\+"
        )
        self.assertEqual(EXPECTED_FINITE_PATTERN, finitize(INFINITE_PATTERN, 100))


class TranslateJavaRegexTest(unittest.TestCase):
    def test_whitespace_classes(self) -> None:
        self.assertEqual(r"\p{H}", translate_java_regex(r"\h"))
        self.assertEqual(r"\p{V}", translate_java_regex(r"\v"))
        self.assertEqual(r"[\p{H}\p{V}]*,", translate_java_regex(r"[\h\v]*,"))

    def test_unicode_flag_dropped(self) -> None:
        self.assertEqual(r"\bС\.", translate_java_regex(r"(?U)\bС\."))
        self.assertEqual("ab", translate_java_regex("a(?U)b"))

    def test_escaped_constructs_untouched(self) -> None:
        # A literal backslash (\\) followed by h/v is not the \h/\v class.
        self.assertEqual("\\\\h", translate_java_regex("\\\\h"))
        self.assertEqual("\\\\v", translate_java_regex("\\\\v"))
        # Odd backslash runs: \\\h is an escaped backslash + the \h class.
        self.assertEqual("\\\\\\p{H}", translate_java_regex("\\\\\\h"))
        # An escaped parenthesis does not start a (?U) group.
        self.assertEqual(r"\(?U\)", translate_java_regex(r"\(?U\)"))

    def test_other_escapes_passed_through(self) -> None:
        pattern = r"\b[\p{Lu}]\.\s+(?=\d)"
        self.assertEqual(pattern, translate_java_regex(pattern))

    def test_translated_patterns_match_java_classes(self) -> None:
        # \p{H} / \p{V} cover exactly the code points of Java's \h and \v
        # (javadoc of java.util.regex.Pattern), including U+180E which the
        # regex package's own \h misses.
        horizontal = re.compile(translate_java_regex(r"\h"))
        vertical = re.compile(translate_java_regex(r"\v"))
        java_h = [0x9, 0x20, 0xA0, 0x1680, 0x180E, *range(0x2000, 0x200B), 0x202F, 0x205F, 0x3000]
        java_v = [0xA, 0xB, 0xC, 0xD, 0x85, 0x2028, 0x2029]
        for code in java_h:
            self.assertTrue(horizontal.fullmatch(chr(code)), hex(code))
            self.assertFalse(vertical.fullmatch(chr(code)), hex(code))
        for code in java_v:
            self.assertTrue(vertical.fullmatch(chr(code)), hex(code))
            self.assertFalse(horizontal.fullmatch(chr(code)), hex(code))
