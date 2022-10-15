import argparse
import sys
from pathlib import Path

from choppa.srx_parser import SrxDocument
import choppa.iterators


def make_iterator(name: str):
    return getattr(choppa.iterators, name)


parser = argparse.ArgumentParser("choppa")
parser.add_argument("-i", "--iterator", type=str,
                    choices=["AccurateSrxTextIterator", "SrxTextIterator"],
                    default="AccurateSrxTextIterator")
parser.add_argument("--max-lookbehind-construct-length", type=int, default=100,
                    help="Maximum length of a regular expression construct that occurs in lookbehind.")
parser.add_argument("-l", "--line-by-line", action="store_true",
                    help="Run a separate segmenter on each line of input. "
                    + "Faster if your sentences definitely do not span multiple lines.")
args = parser.parse_args()
args.iterator = make_iterator(args.iterator)

ruleset = Path(__file__).parent / "data/srx/languagetool_segment.srx"
SRX_2_XSD = Path(__file__).parent / "data/xsd/srx20.xsd"

document = SrxDocument(ruleset=ruleset, validate_ruleset=SRX_2_XSD)

if sys.stdin.isatty():
    print("reading from stdin...", file=sys.stderr)

if args.line_by_line:
    for line in sys.stdin:
        for sentence in args.iterator(document, "uk_two", line.strip(),
                                                max_lookbehind_construct_length=args.max_lookbehind_construct_length):
            print(sentence)
else:
    whole_input = sys.stdin.read().replace("\n", " ").strip()
    for sentence in args.iterator(document, "uk_two", whole_input,
                                  max_lookbehind_construct_length=args.max_lookbehind_construct_length):
        print(sentence)
