import sys
from pathlib import Path

from choppa.srx_parser import SrxDocument
from choppa.iterators import SrxTextIterator


ruleset = Path(__file__).parent / "data/srx/segment_new.srx"
SRX_2_XSD = Path(__file__).parent / "data/xsd/srx20.xsd"

document: SrxDocument = SrxDocument(ruleset=ruleset, validate_ruleset=SRX_2_XSD)

if sys.stdin.isatty():
    print('reading from stdin...', file=sys.stderr)

for text in SrxTextIterator(document, "uk_two", sys.stdin.read()):
    print(text)
