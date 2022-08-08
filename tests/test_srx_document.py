import unittest
from choppa.srx_parser import SrxDocument
from choppa.structures import LanguageRule


class SrxDocumentTest(unittest.TestCase):
    def test_document(self):
        document: SrxDocument = SrxDocument()

        language_rule1: LanguageRule = LanguageRule("1")
        language_rule2: LanguageRule = LanguageRule("2")
        language_rule3: LanguageRule = LanguageRule("3")

        document.add_language_map("aaa", language_rule1)
        document.add_language_map("ab", language_rule2)
        document.add_language_map("a+", language_rule3)

        document.cascade = True

        language_rule_list: List[LanguageRule] = document.get_language_rule_list("aaa")
        self.assertEqual(2, len(language_rule_list))
        self.assertEqual(language_rule1, language_rule_list[0])
        self.assertEqual(language_rule3, language_rule_list[1])

        language_rule_list = document.get_language_rule_list("xxx")
        self.assertEqual(0, len(language_rule_list))

        document.cascade = False

        language_rule_list = document.get_language_rule_list("aaa")
        self.assertEqual(1, len(language_rule_list))
        self.assertEqual(language_rule1, language_rule_list[0])
