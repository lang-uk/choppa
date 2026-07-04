"""
Property-based tests: structural invariants that must hold for ANY
input, not just the example cases.
"""

import io
import unittest

from hypothesis import given, settings, strategies as st

from choppa import SrxTextIterator

from .conftest import get_document


# Surrogates cannot appear in well-formed str input.
TEXTS = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)), max_size=300
)
LANGUAGES = st.sampled_from(["uk_two", "en_two", "de_one", "pl_two", "xx_two"])


class SegmentationPropertiesTest(unittest.TestCase):
    @settings(deadline=None)
    @given(text=TEXTS, language=LANGUAGES)
    def test_segments_concatenate_to_input(self, text: str, language: str) -> None:
        segments = list(SrxTextIterator(get_document(), language, text))
        self.assertEqual(text, "".join(segments))

    @settings(deadline=None)
    @given(text=TEXTS, language=LANGUAGES)
    def test_no_empty_segments(self, text: str, language: str) -> None:
        for segment in SrxTextIterator(get_document(), language, text):
            self.assertNotEqual("", segment)

    @settings(deadline=None, max_examples=50)
    @given(text=TEXTS, language=LANGUAGES)
    def test_reader_mode_equals_string_mode(self, text: str, language: str) -> None:
        # Buffer fits the whole text: verifies the reader constructor
        # itself; the buffer-shift path is exercised by the test below.
        string_segments = list(SrxTextIterator(get_document(), language, text))
        reader_segments = list(
            SrxTextIterator(
                get_document(),
                language,
                io.StringIO(text),
                buffer_length=max(32, len(text) + 16),
            )
        )
        self.assertEqual(string_segments, reader_segments)

    @settings(deadline=None, max_examples=50)
    @given(text=TEXTS, language=LANGUAGES)
    def test_streaming_buffer_shifts_equal_string_mode(self, text: str, language: str) -> None:
        # Join copies with paragraph breaks so segments stay bounded by
        # ~len(text) while the total exceeds the buffer several times
        # over - forcing the buffer-shift/margin path (with the default
        # margin of 128, buffer - margin still exceeds any segment).
        stream_text = "\n\n".join([text] * 6)
        buffer_length = max(256, len(text) + 160)
        string_segments = list(SrxTextIterator(get_document(), language, stream_text))
        reader_segments = list(
            SrxTextIterator(
                get_document(),
                language,
                io.StringIO(stream_text),
                buffer_length=buffer_length,
            )
        )
        self.assertEqual(string_segments, reader_segments)
