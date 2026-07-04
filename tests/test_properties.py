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
    def test_streaming_equals_string_mode(self, text: str, language: str) -> None:
        # Buffer is guaranteed to fit the longest possible segment.
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
