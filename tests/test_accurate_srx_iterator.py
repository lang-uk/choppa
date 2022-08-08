import unittest

from typing import List

from choppa.iterators import AccurateSrxTextIterator, AbstractTextIterator
from choppa.srx_parser import SrxDocument

from .abstract_srx_iterator import AbstractSrxTextIterator


class AccurateSrxTextIteratorTest(AbstractSrxTextIterator):
    __test__ = True

    def get_text_iterator(self, document: SrxDocument, language_code: str, text: str) -> AbstractTextIterator:
        return AccurateSrxTextIterator(document, language_code, text)
