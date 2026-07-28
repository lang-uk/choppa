#!/usr/bin/env python3
r"""
Write out the bundled SRX with LanguageTool's pattern flags baked in, for
use as ground truth in the corpus differential.

LanguageTool compiles every SRX pattern with Java's
`UNICODE_CHARACTER_CLASS`: `SrxTools` hands segment's
`DEFAULT_PATTERN_FLAGS_PARAMETER` to `SrxTextIterator`. That is the
semantics the rules are written against, and Python gives it to us for
free -- `str` patterns are Unicode-aware by default.

The reference binary cannot be told the same thing: `defaultPatternFlags`
arrived in segment 2.0.4, and the 2.0.3 CLI from the releases page
exposes neither the parameter nor an option for it. Prefixing each
pattern with `(?U)`, the inline spelling of that flag, compiles to the
same thing -- so that is what this script does. Feed the CLI the pristine
file instead and it compiles under the JDK's own defaults, which since
JDK 19 means an ASCII-only `\b`: Cyrillic abbreviation exceptions stop
firing and the differential fills with phantom breaks.

Usage:

    python scripts/lt_java_srx.py java_ref.srx
    segment-2.0.3/bin/segment -a ultimate -s java_ref.srx -l uk_two \
        -r -i corpus.txt -o java.txt -e $'\x01'
    python scripts/benchmark.py corpus.txt --language uk_two --java java.txt

The output is for the Java side only: choppa always reads the pristine
bundled file.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from choppa import DEFAULT_SRX_RULESET

# `(?!</)` keeps empty elements (<beforebreak></beforebreak>) untouched:
# an empty pattern matches everything, and `(?U)` would not change that.
PATTERN_ELEMENT = re.compile(r"<(beforebreak|afterbreak)>(?!</)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("out", type=Path, help="where to write the SRX copy")
    parser.add_argument("--srx", type=Path, default=DEFAULT_SRX_RULESET)
    args = parser.parse_args()

    patched, injected = PATTERN_ELEMENT.subn(
        r"<\1>(?U)", args.srx.read_text(encoding="utf-8")
    )
    args.out.write_text(patched, encoding="utf-8")
    print(f"{args.out}: (?U) added to {injected} patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
