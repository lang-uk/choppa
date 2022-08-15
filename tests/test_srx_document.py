import unittest
from typing import List

from xmlschema.validators.exceptions import XMLSchemaValidationError

from choppa.srx_parser import SrxDocument
from choppa.structures import LanguageRule, Rule


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

        document2: SrxDocument = SrxDocument()

        language_rule4: LanguageRule = LanguageRule("4")
        document2.add_language_map("aaa", language_rule4)

        language_rule_list = document.get_language_rule_list("aaa")
        self.assertEqual(1, len(language_rule_list))

        language_rule_list = document2.get_language_rule_list("aaa")
        self.assertEqual(1, len(language_rule_list))
        self.assertEqual(language_rule4, language_rule_list[0])


class SrxParserTest(unittest.TestCase):
    TICKET_1_DOCUMENT_NAME: str = "data/srx/test/ticket1.srx"
    SRX_1_DOCUMENT_NAME: str = "data/srx/test/example1.srx"
    SRX_2_DOCUMENT_NAME: str = "data/srx/test/example.srx"
    INVALID_DOCUMENT_NAME: str = "data/srx/test/invalid.srx"
    SRX_1_XSD: str = "data/xsd/srx10.xsd"
    SRX_2_XSD: str = "data/xsd/srx20.xsd"

    def test_srx2(self) -> None:
        document: SrxDocument = SrxDocument(ruleset=self.SRX_2_DOCUMENT_NAME, validate_ruleset=self.SRX_2_XSD)

        self.assertTrue(document.cascade)

        language_rule_list: List[LanguageRule] = document.get_language_rule_list("fr_FR")
        self.assertEqual(2, len(language_rule_list))
        self.assertEqual("French", language_rule_list[0].name)

        rule_list: List[Rule] = language_rule_list[0].rules
        self.assertEqual(4, len(rule_list))

        rule0: Rule = rule_list[0]
        self.assertEqual(r" [Mm]lle\.", rule0.before_pattern)
        self.assertEqual(r"\s", rule0.after_pattern)

        rule1: Rule = rule_list[1]
        self.assertEqual(r"\s[Mm]lles\.", rule1.before_pattern)
        self.assertEqual(r"\s", rule1.after_pattern)

    def test_srx2_invalid(self) -> None:
        with self.assertRaises(XMLSchemaValidationError):
            document: SrxDocument = SrxDocument(ruleset=self.INVALID_DOCUMENT_NAME, validate_ruleset=self.SRX_2_XSD)


    def test_srx2_ticket1(self)-> None:
        document: SrxDocument = SrxDocument(ruleset=self.TICKET_1_DOCUMENT_NAME, validate_ruleset=self.SRX_2_XSD)

        self.assertTrue(document.cascade)

        language_rule_list: List[LanguageRule] = document.get_language_rule_list("en")

        self.assertEqual("Default", language_rule_list[0].name)

        rule_list: List[Rule] = language_rule_list[0].rules
        self.assertEqual(1, len(rule_list))

        rule: Rule = rule_list[0]
        self.assertEqual("[\\.!?…]['»\"”\\)\\]\\}]?\\u0002?\\s", rule.before_pattern)
        self.assertEqual(r"", rule.after_pattern)
