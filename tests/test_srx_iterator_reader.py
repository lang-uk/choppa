import io

from choppa.iterators import SrxTextIterator, AbstractTextIterator
from choppa.srx_parser import SrxDocument

from .abstract_srx_iterator import AbstractSrxTextIterator


class SrxTextIteratorReaderTest(AbstractSrxTextIterator):
    """
    Port of net.loomchild.segment.srx.SrxTextIteratorReaderTest: re-runs
    the whole abstract segmentation suite in streaming mode with a tiny
    buffer, exercising the buffer shift and margin logic.
    """

    __test__ = True

    BUFFER_SIZE: int = 60
    MARGIN: int = 10

    def get_text_iterator(self, document: SrxDocument, language_code: str, text: str) -> AbstractTextIterator:
        return SrxTextIterator(
            document,
            language_code,
            io.StringIO(text),
            buffer_length=self.BUFFER_SIZE,
            margin=self.MARGIN,
        )

    def test_text_longer_than_buffer_rules(self) -> None:
        # With a 60-character buffer the streaming iterator re-reads the
        # text thousands of times; the default-buffer variant of this test
        # already runs in SrxTextIteratorTest. Keep the streaming suite
        # fast by shrinking the repetition count instead of skipping.
        document: SrxDocument = self.create_text_longer_than_buffer_document()
        expected = ["AAAAAAAAA." for _ in range(200)]
        text = "".join(expected)
        segments = list(self.get_text_iterator(document, self.SIMPLE_LANGUAGE, text))
        self.assertEqual(expected, segments)
