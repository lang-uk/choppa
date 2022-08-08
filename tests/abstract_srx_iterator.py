import unittest

from typing import List

from choppa.srx_parser import SrxDocument
from choppa.structures import LanguageRule, Rule
from choppa.iterators import AbstractTextIterator


class AbstractSrxTextIterator(unittest.TestCase):
    """
    Segmentation text used in all text iterator tests. 
    Inheriting tests must implement get_text_iterator abstract method
    """
    __test__ = False

    SIMPLE_RESULT: List[str] = [
        "Ala ma kota.",
        " Prof. Kot nie wie kim jest.",
        " Ech.",
        "\nA inny prof. to już w ogole.",
        " Uch",
    ]

    SIMPLE_LANGUAGE: str = "pl"
    EMPTY_RESULT: List[str] = []
    ALTERNATIVE_RULE_RESULT: List[str] = ["W 59 n. e. Julek nie zrobił nic ciekawego.", " Drugie dn. to: Ja też nie"]

    def create_simple_document(self) -> SrxDocument:
        language_rule_pl: LanguageRule = LanguageRule("Polish")
        language_rule_pl.add_rule(Rule(False, r"[Pp]rof\.", r"\s"))

        language_rule_en: LanguageRule = LanguageRule("English")
        language_rule_en.add_rule(Rule(False, r"Mr\.", r"\s"))

        language_rule_def: LanguageRule = LanguageRule("Default")
        language_rule_def.add_rule(Rule(True, r"\.", r"\s"))
        # language_rule_def.add_rule(Rule(True, "", r"\n"))

        document: SrxDocument = SrxDocument()
        document.add_language_map("pl.*", language_rule_pl)
        document.add_language_map("en.*", language_rule_en)
        document.add_language_map(".*", language_rule_def)

        return document

    def create_empty_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(True, ".", " "))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_alternative_rule_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("Default")
        language_rule.add_rule(Rule(False, r"(n\.)|(e\.)|(dn\.)", " "))
        language_rule.add_rule(Rule(True, r"\.", " "))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document


    def test_simple_split(self) -> None:
        self.perform_test(self.SIMPLE_RESULT, self.create_simple_document(), self.SIMPLE_LANGUAGE)

    # def test_empty_text(self) -> None:
    #     self.perform_test(self.EMPTY_RESULT, self.create_empty_document())

    # def test_alternative_rule_split(self) -> None:
    #     self.perform_test(self.ALTERNATIVE_RULE_RESULT, self.create_alternative_rule_document())


    def perform_test(self, expected_result: List[str], 
            document: SrxDocument, language_code: str="") -> None:
        
        text: str = "".join(expected_result)
        
        
        text_iterator: AbstractTextIterator = self.get_text_iterator(document, language_code, text)
        segments: List[str] = list(text_iterator)
    
        self.assertEqual(expected_result, segments)
    

    def get_text_iterator(self, document: SrxDocument, 
            language_code: str, text:str) -> AbstractTextIterator:
        raise NotImplementedError
