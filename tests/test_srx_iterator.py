from choppa.iterators import SrxTextIterator, AbstractTextIterator
from choppa.srx_parser import SrxDocument

from .abstract_srx_iterator import AbstractSrxTextIterator


class SrxTextIteratorTest(AbstractSrxTextIterator):
    __test__ = True

    def get_text_iterator(self, document: SrxDocument, language_code: str, text: str) -> AbstractTextIterator:
        return SrxTextIterator(document, language_code, text)
