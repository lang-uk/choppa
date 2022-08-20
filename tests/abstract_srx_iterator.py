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
    WORD_BOUNDARY_LANGUAGE: str = "en"
    EMPTY_RESULT: List[str] = []
    ALTERNATIVE_RULE_RESULT: List[str] = ["W 59 n. e. Julek nie zrobił nic ciekawego.", " Drugie dn. to: Ja też nie"]
    OVERLAPPING_RULES_RESULT: List[str] = ["W 59 n.e. Julek nie zrobił nic ciekawego.", " Ja też nie"]
    INTERLACED_RULES_RESULT: List[str] = ["a? b? a. b.", " c.", " d."]
    NO_BREAK_RULES_RESULT: List[str] = ["abcab"]
    INFINITE_NEGATIVE_RULE_RESULT: List[str] = ["Abc 99. Def.", " Xyz."]
    ONLY_BREAK_RULES_RESULT: List[str] = ["Abc 99.", " Def.", " Xyz."]
    BREAK_AT_THE_END_RESULT: List[str] = ["a."]
    EMPTY_EXCEPTION_RULE_RESULT: List[str] = ["a. b. c"]
    EMPTY_BREAK_RULE_RESULT: List[str] = ["a", " ", "b", "c"]
    WORD_BOUNDARY_RESULT: List[str] = [
        "Don't split strings like U.S.A. please.",
    ]
    EXCEPTION_RULE_LONGER_THAN_BREAK_RULE_RESULT: List[str] = ["Ala ma kota.", " "]
    MATCHING_END_RESULT: List[str] = ["A.", "."]
    MATCHING_ALL_RESULT: List[str] = ["A", " B.", " C", " "]
    OVERLAPPING_BREAK_RULES_RESULT: List[str] = ["A..", ".B"]
    MIXED_BREAK_RULES_RESULT: List[str] = ["xabc", "d"]
    TICKET_1_RESULT: List[str] = ["This is a sentence. "]
    SPECIFICATION_EXAMPLE_RESULT: List[str] = ["The U.K. Prime Minister, Mr. Blair, was seen out today."]
    TEXT_LONGER_THAN_BUFFER_RESULT: List[str] = [
        "AAAAAAAAA." for _ in range(AbstractTextIterator.DEFAULT_BUFFER_LENGTH // 2 + 20)
    ]

    def perform_test(self, expected_result: List[str], document: SrxDocument, language_code: str = "") -> None:

        text: str = "".join(expected_result)

        text_iterator: AbstractTextIterator = self.get_text_iterator(document, language_code, text)
        segments: List[str] = list(text_iterator)

        self.assertEqual(expected_result, segments)

    def get_text_iterator(self, document: SrxDocument, language_code: str, text: str) -> AbstractTextIterator:
        raise NotImplementedError

    def create_simple_document(self) -> SrxDocument:
        language_rule_pl: LanguageRule = LanguageRule("Polish")
        language_rule_pl.add_rule(Rule(False, r"[Pp]rof\.", r"\s"))

        language_rule_en: LanguageRule = LanguageRule("English")
        language_rule_en.add_rule(Rule(False, r"Mr\.", r"\s"))

        language_rule_def: LanguageRule = LanguageRule("Default")
        language_rule_def.add_rule(Rule(True, r"\.", r"\s"))
        language_rule_def.add_rule(Rule(True, r"", r"\n"))

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

    def create_overlapping_rules_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(False, r"n\.", ""))
        language_rule.add_rule(Rule(False, r"n\.e\.", ""))
        language_rule.add_rule(Rule(True, r"\.", ""))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_interlaced_rules_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(False, r"a[\.\?]", " "))
        language_rule.add_rule(Rule(True, r"\.", " "))
        language_rule.add_rule(Rule(False, r"(b[\.\?])", " "))
        language_rule.add_rule(Rule(True, r"\?", " "))
        language_rule.add_rule(Rule(False, r"c[\.\?]", " "))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_no_break_rules_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(False, "a", " "))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_infinite_negative_rule_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(False, r"([0-9]+\.|[0-9]{1,}\.|[0-9][0-9]*\.)", r"\s"))
        language_rule.add_rule(Rule(True, r"\.", r"\s"))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_only_break_rules_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(True, "\\.", "\\s"))
        language_rule.add_rule(Rule(True, "", "\\n"))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_break_at_the_end_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(True, "\\.", ""))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_empty_exception_rule_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(False, "", ""))
        language_rule.add_rule(Rule(True, r"\.", " "))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_empty_break_rule_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(True, "", ""))
        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_word_boundary_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(False, r"\b\p{L}\.", ""))
        language_rule.add_rule(Rule(True, r"\.", ""))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_exception_rule_longer_than_break_rule_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(False, "\\.", "\\sa"))
        language_rule.add_rule(Rule(True, "\\.", "\\s"))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_matching_end_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(True, "\\.\\.\\.", ""))
        language_rule.add_rule(Rule(True, "\\.", ""))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_matching_all_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(True, "[^\\s]*", "\\s"))
        language_rule.add_rule(Rule(True, "\\.", "\\s"))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_overlapping_break_rules_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(True, "\\.\\.\\.", ""))
        language_rule.add_rule(Rule(True, "\\.\\.", ""))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_mixed_break_rules_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(False, "b", "c"))
        language_rule.add_rule(Rule(True, "b", ""))
        language_rule.add_rule(Rule(True, "abc", ""))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_ticket1_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(False, "[A-Z]\\.\\s", ""))
        language_rule.add_rule(Rule(True, "\\.\\s", ""))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_specification_example_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(False, "\\sU\\.K\\.", "\\s"))
        language_rule.add_rule(Rule(False, "Mr\\.", "\\s"))
        language_rule.add_rule(Rule(True, "[\\.\\?!]+", "\\s"))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def create_text_longer_than_buffer_document(self) -> SrxDocument:
        language_rule: LanguageRule = LanguageRule("")

        language_rule.add_rule(Rule(False, "Mr\\.", ""))
        language_rule.add_rule(Rule(True, "\\.", ""))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        return document

    def test_simple_split(self) -> None:
        self.perform_test(self.SIMPLE_RESULT, self.create_simple_document(), self.SIMPLE_LANGUAGE)

    def test_empty_text(self) -> None:
        self.perform_test(self.EMPTY_RESULT, self.create_empty_document())

    def test_alternative_rule_split(self) -> None:
        self.perform_test(self.ALTERNATIVE_RULE_RESULT, self.create_alternative_rule_document())

    def test_overlapping_rules_split(self) -> None:
        self.perform_test(self.OVERLAPPING_RULES_RESULT, self.create_overlapping_rules_document())

    def test_interlaced_rules_split(self) -> None:
        self.perform_test(self.INTERLACED_RULES_RESULT, self.create_interlaced_rules_document())

    def test_no_break_rules(self) -> None:
        self.perform_test(self.NO_BREAK_RULES_RESULT, self.create_no_break_rules_document())

    def test_infinite_negative_rule(self) -> None:
        self.perform_test(self.INFINITE_NEGATIVE_RULE_RESULT, self.create_infinite_negative_rule_document())

    def test_only_break_rules(self) -> None:
        self.perform_test(self.ONLY_BREAK_RULES_RESULT, self.create_only_break_rules_document())

    def test_break_at_the_end_of_text(self) -> None:
        self.perform_test(self.BREAK_AT_THE_END_RESULT, self.create_break_at_the_end_document())

    def test_empty_exception_rule(self) -> None:
        self.perform_test(self.EMPTY_EXCEPTION_RULE_RESULT, self.create_empty_exception_rule_document())

    def test_empty_break_rule(self) -> None:
        self.perform_test(self.EMPTY_BREAK_RULE_RESULT, self.create_empty_break_rule_document())

    def test_word_boundary(self) -> None:
        self.perform_test(self.WORD_BOUNDARY_RESULT, self.create_word_boundary_document(), self.WORD_BOUNDARY_LANGUAGE)

    def test_exception_rule_longer_than_break_rule(self) -> None:
        self.perform_test(
            self.EXCEPTION_RULE_LONGER_THAN_BREAK_RULE_RESULT,
            self.create_exception_rule_longer_than_break_rule_document(),
        )

    def test_matching_end(self) -> None:
        self.perform_test(self.MATCHING_END_RESULT, self.create_matching_end_document())

    def test_matching_all(self) -> None:
        self.perform_test(self.MATCHING_ALL_RESULT, self.create_matching_all_document())

    def test_overlapping_break_rules(self) -> None:
        self.perform_test(self.OVERLAPPING_BREAK_RULES_RESULT, self.create_overlapping_break_rules_document())

    def test_mixed_break_rules(self) -> None:
        self.perform_test(self.MIXED_BREAK_RULES_RESULT, self.create_mixed_break_rules_document())

    def test_text_longer_than_buffer_rules(self) -> None:
        self.perform_test(self.TEXT_LONGER_THAN_BUFFER_RESULT, self.create_text_longer_than_buffer_document())

    def test_ticket1_rule(self) -> None:
        self.perform_test(self.TICKET_1_RESULT, self.create_ticket1_document())

    def test_specification_example(self) -> None:
        self.perform_test(self.SPECIFICATION_EXAMPLE_RESULT, self.create_specification_example_document())
