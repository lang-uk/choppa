from typing import List

from choppa.iterators import SrxTextIterator, AbstractTextIterator
from choppa.srx_parser import SrxDocument
from choppa.structures import LanguageRule, Rule

from .abstract_srx_iterator import AbstractSrxTextIterator


class SrxTextIteratorTest(AbstractSrxTextIterator):
    __test__ = True

    def get_text_iterator(self, document: SrxDocument, language_code: str, text: str) -> AbstractTextIterator:
        return SrxTextIterator(document, language_code, text)

    def test_max_lookbehind_construct_length(self) -> None:
        # Port of SrxTextIteratorStringTest.testMaxLookbehindConstructLength
        language_rule: LanguageRule = LanguageRule("")
        language_rule.add_rule(Rule(False, r"XA+\.", ""))
        language_rule.add_rule(Rule(False, r"XB+\.", ""))
        language_rule.add_rule(Rule(True, r"\.", ""))

        document: SrxDocument = SrxDocument()
        document.add_language_map(".*", language_rule)

        expected: List[str] = ["XAAA.", "XBB.XC"]
        text: str = "".join(expected)

        segments: List[str] = list(
            SrxTextIterator(document, "", text, max_lookbehind_construct_length=2)
        )
        self.assertEqual(expected, segments)
