import unittest
from choppa.rule_matcher import RuleMatcher, JavaMatcher
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

    def test_java_matcher_find(self):
        matcher: JavaMatcher = JavaMatcher(pattern=r"foo", text="foobarfoo")

        match = matcher.find()
        self.assertEqual(matcher.start, 0)
        self.assertEqual(matcher.end, 3)

        match = matcher.find()
        self.assertEqual(matcher.start, 6)
        self.assertEqual(matcher.end, 9)

        match = matcher.find()
        self.assertEqual(match, None)
        self.assertEqual(matcher._start, 9)
        self.assertEqual(matcher._end, 9)

    def test_java_matcher_looking_at(self):
        matcher: JavaMatcher = JavaMatcher(pattern=r"foo", text="foobarfoo")

        match = matcher.looking_at()
        self.assertEqual(matcher.start, 0)
        self.assertEqual(matcher.end, 3)

        match = matcher.looking_at()
        self.assertEqual(match, None)
        self.assertEqual(matcher._start, 3)
        self.assertEqual(matcher._end, 9)

        match = matcher.find()
        self.assertEqual(matcher.start, 6)
        self.assertEqual(matcher.end, 9)

    def test_java_matcher_empty(self):
        # Emulates following behavior
        # Pattern EMPTY_PATTERN = Pattern.compile("");
        # Matcher beforeMatcher = EMPTY_PATTERN.matcher("123");

        # while (beforeMatcher.find()) {
        #     System.out.println(beforeMatcher.start());
        #     System.out.println(beforeMatcher.end());
        # }

        matcher: JavaMatcher = JavaMatcher(pattern=r"", text="123")

        match = matcher.find()
        self.assertEqual(matcher.start, 0)
        self.assertEqual(matcher.end, 0)

        match = matcher.find()
        self.assertEqual(matcher.start, 1)
        self.assertEqual(matcher.end, 1)

        match = matcher.find()
        self.assertEqual(matcher.start, 2)
        self.assertEqual(matcher.end, 2)

        match = matcher.find()
        self.assertEqual(matcher.start, 3)
        self.assertEqual(matcher.end, 3)

        match = matcher.find()
        self.assertEqual(match, None)

    def test_caret_matcher(self):
        # Emulates behavior of the Java matcher, when
        # caret matcher can match the beginning of the region

        matcher: JavaMatcher = JavaMatcher(pattern=r"^\d", text="123")

        match = matcher.find()
        self.assertEqual(matcher.start, 0)
        self.assertEqual(matcher.end, 1)

        match = matcher.find()
        self.assertEqual(matcher.start, 1)
        self.assertEqual(matcher.end, 2)

        match = matcher.find()
        self.assertEqual(matcher.start, 2)
        self.assertEqual(matcher.end, 3)

        match = matcher.find()
        self.assertEqual(match, None)

    def test_caret_alt_matcher(self):
        matcher: JavaMatcher = JavaMatcher(pattern=r"(^foo)|(bar)", text="foobarfoo")

        match = matcher.find()
        self.assertEqual(matcher.start, 0)
        self.assertEqual(matcher.end, 3)

        match = matcher.find()
        self.assertEqual(matcher.start, 3)
        self.assertEqual(matcher.end, 6)

        match = matcher.find()
        self.assertEqual(matcher.start, 6)
        self.assertEqual(matcher.end, 9)

        match = matcher.find()
        self.assertEqual(match, None)

    def test_transparent_bound(self):
        matcher: JavaMatcher = JavaMatcher(pattern=r"(?:(?<=[Pp]rof\.)(?=\s))", text="12345 Prof. foobar")
        matcher.use_transparent_bounds = True

        match = matcher.find()
        self.assertEqual(matcher.start, 11)
        self.assertEqual(matcher.end, 11)

        matcher.region(11)
        match = matcher.find()
        self.assertEqual(matcher.start, 11)
        self.assertEqual(matcher.end, 11)

        matcher.region(12)
        match = matcher.find()
        self.assertIsNone(match)

        matcher.region(0)
        match = matcher.looking_at()
        self.assertIsNone(match)

        matcher.region(11)
        match = matcher.find()
        self.assertEqual(matcher.start, 11)
        self.assertEqual(matcher.end, 11)

        matcher.region(12)
        match = matcher.find()
        self.assertIsNone(match)
