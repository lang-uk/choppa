import unittest
from choppa.rule_matcher import RuleMatcher
from choppa.srx_parser import SrxDocument, Rule


class RuleMatcherTest(unittest.TestCase):
    def test_rule_matcher(self):
        # Port of net.loomchild.segment.srx.RuleMatcherTest.testFind
        document: SrxDocument = SrxDocument()
        rule: Rule = Rule(True, "ab+", "ca+")
        text: str = "abaabbcabcabcaa"
        matcher: RuleMatcher = RuleMatcher(document, rule, text)
        self.assertFalse(matcher.hit_end())
        self.assertTrue(matcher.find())
        self.assertFalse(matcher.hit_end())
        self.assertEqual(3, matcher.get_start_position())
        self.assertEqual(6, matcher.get_break_position())
        self.assertEqual(8, matcher.get_end_position())
        self.assertTrue(matcher.find())
        self.assertFalse(matcher.hit_end())
        self.assertEqual(7, matcher.get_start_position())
        self.assertEqual(9, matcher.get_break_position())
        self.assertEqual(11, matcher.get_end_position())
        self.assertTrue(matcher.find())
        self.assertFalse(matcher.hit_end())
        self.assertEqual(10, matcher.get_start_position())
        self.assertEqual(12, matcher.get_break_position())
        self.assertEqual(15, matcher.get_end_position())
        self.assertFalse(matcher.find())
        self.assertTrue(matcher.hit_end())
        self.assertTrue(matcher.find(6))
        self.assertEqual(7, matcher.get_start_position())
        self.assertEqual(9, matcher.get_break_position())
        self.assertEqual(11, matcher.get_end_position())

    def test_zero_length_matches(self):
        # An exception rule wrapped in lookbehind (as done by both
        # iterators) produces zero-width before-matches; the matcher must
        # advance past them the way java.util.regex.Matcher.find() does.
        document: SrxDocument = SrxDocument()
        rule: Rule = Rule(True, r"(?<=[A-Z]\.\s?)", "")
        text: str = "XA. B."
        matcher: RuleMatcher = RuleMatcher(document, rule, text)

        self.assertFalse(matcher.hit_end())

        self.assertTrue(matcher.find())
        self.assertFalse(matcher.hit_end())
        self.assertEqual(3, matcher.get_start_position())
        self.assertEqual(3, matcher.get_break_position())
        self.assertEqual(3, matcher.get_end_position())

        self.assertTrue(matcher.find())
        self.assertFalse(matcher.hit_end())
        self.assertEqual(4, matcher.get_start_position())
        self.assertEqual(4, matcher.get_break_position())
        self.assertEqual(4, matcher.get_end_position())

        self.assertTrue(matcher.find())
        self.assertFalse(matcher.hit_end())
        self.assertEqual(6, matcher.get_start_position())
        self.assertEqual(6, matcher.get_break_position())
        self.assertEqual(6, matcher.get_end_position())

        self.assertFalse(matcher.find())
        self.assertTrue(matcher.hit_end())

        self.assertTrue(matcher.find(2))
        self.assertEqual(3, matcher.get_start_position())
        self.assertEqual(3, matcher.get_break_position())
        self.assertEqual(3, matcher.get_end_position())

    def test_adjacent_matches(self):
        # java.util.regex.Matcher.find() restarts at the END of the
        # previous match (not end + 1), so a following match starting
        # exactly at the previous end must be found. Guards against the
        # unconditional +1 advancement bug.
        document: SrxDocument = SrxDocument()
        rule: Rule = Rule(True, r"\.", "")
        text: str = "a..b"
        matcher: RuleMatcher = RuleMatcher(document, rule, text)

        self.assertTrue(matcher.find())
        self.assertEqual(1, matcher.get_start_position())
        self.assertEqual(2, matcher.get_break_position())

        self.assertTrue(matcher.find())
        self.assertEqual(2, matcher.get_start_position())
        self.assertEqual(3, matcher.get_break_position())

        self.assertFalse(matcher.find())

    def test_empty_pattern_walks_every_position(self):
        # Java: an empty pattern matches at every position 0..len(text).
        document: SrxDocument = SrxDocument()
        rule: Rule = Rule(True, "", "")
        text: str = "123"
        matcher: RuleMatcher = RuleMatcher(document, rule, text)

        for expected in range(len(text) + 1):
            self.assertTrue(matcher.find())
            self.assertEqual(expected, matcher.get_break_position())

        self.assertFalse(matcher.find())
        self.assertTrue(matcher.hit_end())

    def test_lookbehind_sees_before_start(self):
        # pattern.match(text, pos) keeps the left bound transparent, the
        # same as Java's useTransparentBounds(true) + lookingAt() used for
        # exception-rule matching.
        document: SrxDocument = SrxDocument()
        rule: Rule = Rule(True, r"(?:(?<=[Pp]rof\.)(?=\s))", "")
        text: str = "12345 Prof. foobar"
        matcher: RuleMatcher = RuleMatcher(document, rule, text)

        self.assertTrue(matcher.find())
        self.assertEqual(11, matcher.get_start_position())
        self.assertEqual(11, matcher.get_break_position())

        self.assertTrue(matcher.find(11))
        self.assertEqual(11, matcher.get_break_position())

        self.assertFalse(matcher.find(12))
