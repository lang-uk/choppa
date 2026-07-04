from pathlib import Path

from .srx_parser import SrxDocument
from .iterators import AccurateSrxTextIterator, SrxTextIterator

__author__ = "Dmytro Chaplynskyi, Jarek Lipski"
__email__ = "chaplinsky.dmitry@gmail.com"
__version__ = "1.0.0"

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_SRX_RULESET = DATA_DIR / "srx" / "languagetool_segment.srx"
SRX_2_XSD = DATA_DIR / "xsd" / "srx20.xsd"

__all__ = [
    "SrxDocument",
    "SrxTextIterator",
    "AccurateSrxTextIterator",
    "DEFAULT_SRX_RULESET",
    "SRX_2_XSD",
]
