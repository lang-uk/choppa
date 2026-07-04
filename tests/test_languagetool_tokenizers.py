"""
LanguageTool sentence-tokenizer test suites, extracted from the Java
tests by scripts/extract_lt_tests.py into tests/data/lt/*.json.

Each case mirrors org.languagetool.TestTools.testSplit: the expected
sentences are concatenated, segmented with the bundled LanguageTool SRX
rules, and the result must equal the expected list. The language key is
"<code>_one" or "<code>_two" depending on the tokenizer's
setSingleLineBreaksMarksParagraph setting in the original Java test.
"""

import functools
import json
import unittest
from pathlib import Path
from typing import List

from choppa import DEFAULT_SRX_RULESET, SrxDocument, SrxTextIterator

DATA_DIR = Path(__file__).parent / "data" / "lt"


@functools.lru_cache(maxsize=1)
def get_document() -> SrxDocument:
    return SrxDocument(ruleset=DEFAULT_SRX_RULESET)


class LanguageToolTokenizerTest(unittest.TestCase):
    maxDiff = None

    def run_language(self, fixture_path: Path) -> None:
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        document = get_document()
        language = fixture["language"]

        for i, case in enumerate(fixture["cases"]):
            expected: List[str] = case["sentences"]
            text = "".join(expected)
            with self.subTest(case=i, text=text[:80]):
                segments = list(
                    SrxTextIterator(document, language + case["mode"], text)
                )
                self.assertEqual(expected, segments)


def _make_test(path: Path):
    def test(self: LanguageToolTokenizerTest) -> None:
        self.run_language(path)

    return test


for _path in sorted(DATA_DIR.glob("*.json")):
    setattr(LanguageToolTokenizerTest, f"test_{_path.stem}", _make_test(_path))
