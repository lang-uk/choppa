import unittest
from choppa.rule_matcher import RuleMatcher
from choppa.srx_parser import SrxDocument, Rule


class RuleMatcherTest(unittest.TestCase):
    def test_rule_matcher(self):
        document: SrxDocument = SrxDocument()
        rule: Rule = Rule(True, "ab+", "ca+")
        text: text = "abaabbcabcabcaa"
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
