import argparse
import sys
from pathlib import Path

from choppa.srx_parser import SrxDocument
from choppa.iterators import AbstractTextIterator, AccurateSrxTextIterator, SrxTextIterator

DEFAULT_RULESET = Path(__file__).parent / "data/srx/languagetool_segment.srx"
SRX_2_XSD = Path(__file__).parent / "data/xsd/srx20.xsd"

ITERATORS = {
    "SrxTextIterator": SrxTextIterator,
    "AccurateSrxTextIterator": AccurateSrxTextIterator,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        "choppa",
        description="Split text into sentences using SRX rules "
        "(reads text from a file or stdin, writes one segment per line).",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="input file (default: stdin)",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="uk_two",
        help="language key matched against the SRX language maps; "
        "for the bundled LanguageTool rules use e.g. uk_two, en_two, de_one "
        "(_two: paragraphs end at two line breaks, _one: at every line break). "
        "Default: %(default)s",
    )
    parser.add_argument(
        "-s",
        "--srx",
        type=Path,
        default=DEFAULT_RULESET,
        help="SRX 2.0 rules file (default: bundled LanguageTool segment.srx)",
    )
    parser.add_argument(
        "-i",
        "--iterator",
        choices=sorted(ITERATORS),
        default="SrxTextIterator",
        help="segmentation algorithm (default: %(default)s)",
    )
    parser.add_argument(
        "--max-lookbehind-construct-length",
        type=int,
        default=AbstractTextIterator.DEFAULT_MAX_LOOKBEHIND_CONSTRUCT_LENGTH,
        help="maximum length of a regular expression construct that occurs "
        "in lookbehind (default: %(default)s)",
    )
    parser.add_argument(
        "--line-by-line",
        action="store_true",
        help="run a separate segmenter on each input line; faster if your "
        "sentences never span multiple lines",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="validate the SRX file against the SRX 2.0 XML schema first",
    )
    args = parser.parse_args()

    document = SrxDocument(
        ruleset=args.srx,
        validate_ruleset=SRX_2_XSD if args.validate else None,
    )
    iterator_class = ITERATORS[args.iterator]

    if sys.stdin.isatty() and args.input is sys.stdin:
        print("reading from stdin...", file=sys.stderr)

    def segment(text: str) -> None:
        iterator = iterator_class(
            document,
            args.language,
            text,
            max_lookbehind_construct_length=args.max_lookbehind_construct_length,
        )
        for sentence in iterator:
            print(sentence)

    if args.line_by_line:
        for line in args.input:
            segment(line.strip())
    else:
        segment(args.input.read())


if __name__ == "__main__":
    main()
