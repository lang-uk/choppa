import unittest

from choppa.rule_manager import RuleManager
from choppa.structures import Rule, LanguageRule
from choppa.srx_parser import SrxDocument

from typing import List


class RuleManagerTest(unittest.TestCase):
    def test_simple_rule(self) -> None:
        language_rule_pl: LanguageRule = LanguageRule("Polish")

        rule1: Rule = Rule(False, r"[Pp]rof\.", r"\s")
        language_rule_pl.add_rule(rule1)

        language_rule_en: LanguageRule = LanguageRule("English")

        rule2: Rule = Rule(False, r"Mr\.", r"\s")
        language_rule_en.add_rule(rule2)

        language_rule_def: LanguageRule = LanguageRule("Default")

        break_rule1 = Rule(True, r"\.", r"\s")
        language_rule_def.add_rule(break_rule1)
        break_rule2 = Rule(True, r"", r"\n")
        language_rule_def.add_rule(break_rule2)

        document: SrxDocument = SrxDocument()
        document.add_language_map("pl.*", language_rule_pl)
        document.add_language_map("en.*", language_rule_en)
        document.add_language_map(".*", language_rule_def)

        language_rule_list: List[LanguageRule] = document.get_language_rule_list("pl")
        rule_manager: RuleManager = document.get_rule_manager(language_rule_list, 100)

        self.assertEqual(rule_manager.exception_pattern_map[break_rule1].pattern, r"(?:(?<=[Pp]rof\.)(?=\s))")
        self.assertEqual(rule_manager.exception_pattern_map[break_rule2].pattern, r"(?:(?<=[Pp]rof\.)(?=\s))")

        language_rule_list = document.get_language_rule_list("en")
        rule_manager: RuleManager = document.get_rule_manager(language_rule_list, 100)

        self.assertEqual(rule_manager.exception_pattern_map[break_rule1].pattern, r"(?:(?<=Mr\.)(?=\s))")
        self.assertEqual(rule_manager.exception_pattern_map[break_rule2].pattern, r"(?:(?<=Mr\.)(?=\s))")
