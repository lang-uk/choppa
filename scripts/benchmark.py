#!/usr/bin/env python3
"""
Benchmark choppa and (optionally) diff its output against the original
Java segment implementation.

Segment a corpus:

    python scripts/benchmark.py corpus.txt --language uk_two --out segments.txt

Compare against Java ground truth (one \\x01-separated file, produced by
the segment CLI: https://github.com/loomchild/segment/releases):

    segment/bin/segment -a ultimate -s choppa/data/srx/languagetool_segment.srx \\
        -l uk_two -r -i corpus.txt -o java.txt -e $'\\x01'
    python scripts/benchmark.py corpus.txt --language uk_two --java java.txt

Reference numbers for six corpora (uk news x3, English novels x3,
~136,000 segments, all byte-identical to Java) are in the README's
"Performance and verification" section. Corpus files must use LF line
endings: Java does not normalize CRLF, Python's read_text does.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from choppa import DEFAULT_SRX_RULESET, SrxDocument
from choppa.iterators import ITERATORS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--language", default="uk_two")
    parser.add_argument("--srx", type=Path, default=DEFAULT_SRX_RULESET)
    parser.add_argument("--iterator", choices=sorted(ITERATORS), default="SrxTextIterator")
    parser.add_argument("--out", type=Path, help="write segments separated by \\x01")
    parser.add_argument("--java", type=Path, help="Java segment output (\\x01-separated) to diff against")
    args = parser.parse_args()

    document = SrxDocument(ruleset=args.srx)
    text = args.corpus.read_text(encoding="utf-8")

    started = time.perf_counter()
    segments = list(ITERATORS[args.iterator](document, args.language, text))
    elapsed = time.perf_counter() - started

    mb = len(text.encode("utf-8")) / 1e6
    print(f"{len(segments)} segments in {elapsed:.2f}s ({mb / elapsed:.2f} MB/s)")

    if args.out:
        args.out.write_text("\x01".join(segments) + "\x01", encoding="utf-8")

    if args.java:
        expected = args.java.read_text(encoding="utf-8").split("\x01")
        if expected and expected[-1] in ("", "\n"):
            expected = expected[:-1]
        if expected == segments:
            print(f"IDENTICAL to Java ({len(expected)} segments)")
            return 0
        print(f"DIFFERS from Java: java={len(expected)}, choppa={len(segments)}")
        import difflib

        matcher = difflib.SequenceMatcher(None, expected, segments, autojunk=False)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            print(f"--- {tag}")
            for segment in expected[i1:i2][:3]:
                print(f"  java   | {segment!r}")
            for segment in segments[j1:j2][:3]:
                print(f"  choppa | {segment!r}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
