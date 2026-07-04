#!/usr/bin/env python3
"""
Extract sentence-tokenization test cases from LanguageTool's Java test
suites into JSON fixtures consumed by tests/test_languagetool_tokenizers.py.

Usage:

    python scripts/extract_lt_tests.py <dir-with-java-tests> [<dir> ...]

Each input directory is scanned for *SentenceTokenizerTest.java files
(e.g. languagetool-language-modules/*/src/test/java/**/tokenizers/ in a
LanguageTool checkout). For every file the script:

* resolves which tokenizer field the local testSplit(...) helper delegates
  to and whether that field is configured with
  setSingleLineBreaksMarksParagraph(true) ("_one" paragraph mode) or the
  default false ("_two");
* collects every testSplit(...) call site, concatenating adjacent Java
  string literals and unescaping them;
* writes tests/data/lt/<code>.json with the expected segment lists.

Calls whose arguments are not pure string literals are skipped and
reported, so the port of the suite is auditable.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

OUTPUT_DIR = Path(__file__).parent.parent / "tests" / "data" / "lt"

# org.languagetool.language.<ClassName> -> LanguageTool short code
LANGUAGE_CODES: Dict[str, str] = {
    "Arabic": "ar",
    "Asturian": "ast",
    "Belarusian": "be",
    "Breton": "br",
    "Catalan": "ca",
    "Chinese": "zh",
    "CrimeanTatar": "crh",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Esperanto": "eo",
    "French": "fr",
    "Galician": "gl",
    "German": "de",
    "Greek": "el",
    "Icelandic": "is",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Khmer": "km",
    "Lithuanian": "lt",
    "Malayalam": "ml",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Serbian": "sr",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Spanish": "es",
    "Swedish": "sv",
    "Tagalog": "tl",
    "Tamil": "ta",
    "Ukrainian": "uk",
}

JAVA_SIMPLE_ESCAPES = {
    "b": "\b",
    "t": "\t",
    "n": "\n",
    "f": "\f",
    "r": "\r",
    '"': '"',
    "'": "'",
    "\\": "\\",
}


def strip_comments(source: str) -> str:
    """Removes // and /* */ comments, preserving string literals."""
    out: List[str] = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch == '"':
            j = i + 1
            while j < n and source[j] != '"':
                if source[j] == "\\":
                    j += 1
                j += 1
            out.append(source[i : j + 1])
            i = j + 1
        elif ch == "'":
            j = i + 1
            while j < n and source[j] != "'":
                if source[j] == "\\":
                    j += 1
                j += 1
            out.append(source[i : j + 1])
            i = j + 1
        elif source.startswith("//", i):
            j = source.find("\n", i)
            i = n if j == -1 else j
        elif source.startswith("/*", i):
            j = source.find("*/", i + 2)
            i = n if j == -1 else j + 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def unescape_java(literal: str) -> str:
    """Unescapes the inside of a Java string literal."""
    out: List[str] = []
    i = 0
    n = len(literal)
    while i < n:
        ch = literal[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        esc = literal[i + 1]
        if esc == "u":
            j = i + 2
            # Java allows multiple u's: \uuXXXX
            while literal[j] == "u":
                j += 1
            out.append(chr(int(literal[j : j + 4], 16)))
            i = j + 4
        elif esc in JAVA_SIMPLE_ESCAPES:
            out.append(JAVA_SIMPLE_ESCAPES[esc])
            i += 2
        elif esc.isdigit():
            j = i + 1
            digits = ""
            while j < n and literal[j].isdigit() and len(digits) < 3:
                digits += literal[j]
                j += 1
            out.append(chr(int(digits, 8)))
            i = j
        else:
            raise ValueError(f"Unknown escape \\{esc} in {literal!r}")
    return "".join(out)


def split_top_level_args(arglist: str) -> List[str]:
    """Splits an argument list on commas outside strings and parens."""
    args: List[str] = []
    depth = 0
    current: List[str] = []
    i = 0
    n = len(arglist)
    while i < n:
        ch = arglist[i]
        if ch == '"':
            j = i + 1
            while j < n and arglist[j] != '"':
                if arglist[j] == "\\":
                    j += 1
                j += 1
            current.append(arglist[i : j + 1])
            i = j + 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1
    if current:
        args.append("".join(current).strip())
    return [a for a in args if a]


LITERAL_CONCAT = re.compile(
    r'^\s*"((?:[^"\\]|\\.)*)"(?:\s*\+\s*"((?:[^"\\]|\\.)*)")*\s*$'
)
LITERAL_PIECE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def parse_literal_arg(arg: str) -> Optional[str]:
    """Parses an argument that is a concatenation of string literals;
    returns None if it contains anything else."""
    if not LITERAL_CONCAT.match(arg):
        return None
    return "".join(unescape_java(piece) for piece in LITERAL_PIECE.findall(arg))


def find_call_sites(source: str, name: str) -> List[Tuple[int, str]]:
    """Returns (offset, arglist) for every call of `name`(...) that is not
    a method definition."""
    sites: List[Tuple[int, str]] = []
    for match in re.finditer(rf"(?<![\w.]){re.escape(name)}\s*\(", source):
        prefix = source[: match.start()].rstrip()
        if prefix.endswith(("void", "private", "public", "static", "final")):
            continue
        depth = 1
        i = match.end()
        start = i
        while i < len(source) and depth:
            ch = source[i]
            if ch == '"':
                i += 1
                while i < len(source) and source[i] != '"':
                    if source[i] == "\\":
                        i += 1
                    i += 1
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            i += 1
        sites.append((match.start(), source[start : i - 1]))
    return sites


def detect_language(source: str, filename: str) -> Optional[str]:
    for match in re.finditer(r"import org\.languagetool\.language\.(\w+);", source):
        code = LANGUAGE_CODES.get(match.group(1))
        if code:
            return code
    match = re.match(r"(\w+?)(?:SRX)?SentenceTokenizerTest", filename)
    if match:
        return LANGUAGE_CODES.get(match.group(1))
    return None


def detect_base_modes(source: str) -> Dict[str, str]:
    """Maps tokenizer field name -> '_one' or '_two' as configured at
    field declaration / in the @Before setup method."""
    modes: Dict[str, str] = {}
    for match in re.finditer(
        r"(?:SentenceTokenizer|SRXSentenceTokenizer)\s+(\w+)\s*=", source
    ):
        modes[match.group(1)] = "_two"  # LT default
    before = re.search(r"@Before\s+public\s+void\s+\w+\(\)\s*\{(.*?)\n\s*\}", source, re.S)
    if before:
        for match in re.finditer(
            r"(\w+)\.setSingleLineBreaksMarksParagraph\((true|false)\)", before.group(1)
        ):
            modes[match.group(1)] = "_one" if match.group(2) == "true" else "_two"
    return modes


def modes_at(source: str, offset: int, base_modes: Dict[str, str]) -> Dict[str, str]:
    """Field modes in effect at `offset`: base modes, overridden by any
    setSingleLineBreaksMarksParagraph calls between the start of the
    enclosing test method and the offset (some suites flip the mode
    mid-method, e.g. AsturianSRXSentenceTokenizerTest)."""
    method_starts = [
        m.start() for m in re.finditer(r"\bvoid\s+\w+\s*\(", source) if m.start() < offset
    ]
    method_start = method_starts[-1] if method_starts else 0
    modes = dict(base_modes)
    for match in re.finditer(
        r"(\w+)\.setSingleLineBreaksMarksParagraph\((true|false)\)",
        source[method_start:offset],
    ):
        modes[match.group(1)] = "_one" if match.group(2) == "true" else "_two"
    return modes


def detect_helper_field(source: str) -> Optional[str]:
    match = re.search(
        r"void\s+testSplit\s*\(\s*(?:final\s+)?String\.\.\.\s*\w+\s*\)\s*\{\s*"
        r"TestTools\.testSplit\(\s*\w+\s*,\s*(\w+)\s*\)",
        source,
    )
    return match.group(1) if match else None


def extract_file(path: Path) -> Optional[dict]:
    source = strip_comments(path.read_text(encoding="utf-8"))

    if "new SRXSentenceTokenizer" not in source:
        print(f"  SKIP {path.name}: does not test the SRX tokenizer")
        return None

    language = detect_language(source, path.name)
    if language is None:
        print(f"  SKIP {path.name}: cannot determine language")
        return None

    base_modes = detect_base_modes(source)
    helper_field = detect_helper_field(source)

    cases: List[dict] = []
    skipped = 0

    # Local testSplit(...) helper calls.
    for offset, arglist in find_call_sites(source, "testSplit"):
        modes = modes_at(source, offset, base_modes)
        args = split_top_level_args(arglist)
        # Direct TestTools.testSplit(sentences-array, tokenizer) calls are
        # handled too; the local helper takes only string varargs.
        if args and args[-1] in modes:
            array_args = args[0]
            mode = modes[args[-1]]
            inner = re.search(r"\{(.*)\}", array_args, re.S)
            if not inner:
                skipped += 1
                continue
            args = split_top_level_args(inner.group(1))
        else:
            mode = modes.get(helper_field, "_two") if helper_field else "_two"
        sentences = [parse_literal_arg(a) for a in args]
        if not sentences or any(s is None for s in sentences):
            skipped += 1
            continue
        cases.append({"mode": mode, "sentences": sentences})

    if skipped:
        print(f"  {path.name}: skipped {skipped} non-literal call(s)")
    if not cases:
        print(f"  SKIP {path.name}: no extractable cases")
        return None

    return {
        "language": language,
        "source": path.name,
        "cases": cases,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for directory in sys.argv[1:]:
        for path in sorted(Path(directory).rglob("*SentenceTokenizerTest.java")):
            if path.name == "SRXSentenceTokenizerTest.java":
                continue  # generic smoke test, no testSplit cases
            result = extract_file(path)
            if result is None:
                continue
            out_path = OUTPUT_DIR / f"{result['language']}.json"
            out_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8",
            )
            total += len(result["cases"])
            print(
                f"  {result['language']}.json: {len(result['cases'])} cases "
                f"({result['source']})"
            )
    print(f"Total: {total} cases")


if __name__ == "__main__":
    main()
