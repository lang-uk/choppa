# choppa

Python port of the Java [segment](https://github.com/loomchild/segment) SRX
sentence segmenter by [Jarek Lipski](https://github.com/loomchild), shipped
with the multi-language `segment.srx` segmentation rules crafted by the
[LanguageTool](https://github.com/languagetool-org/languagetool) team.

In a nutshell, it splits text into sentences (but it is rule-based, so you
can chop anything textual). It is the same segmentation engine and the same
rules LanguageTool uses — in pure Python.

- **Identical output.** `SrxTextIterator` is byte-identical to the Java
  original: verified on a 100k-line / 11 MB real-world Ukrainian corpus
  (43,569 segments, zero differences) and on 848 test cases ported from
  LanguageTool's 24 language test suites.
- **Fast.** The same corpus segments in ~5 s vs ~30 s for the Java CLI
  (Apple M1); about 25x faster than choppa 0.9.
- **Streaming.** Text can be read incrementally from a file object with a
  fixed-size buffer, so multi-GB corpora do not need to fit in memory.

# Quick Start

```bash
pip install choppa-srx
```

(The import name is `choppa`; the bare `choppa` name on PyPI belongs to an
unrelated project.)

Command line:

```bash
echo "Жоден сучасний електронний прилад не обходиться без мікрочипів. \
Мікрочіп, інакше кажучи, мікросхема - це набір електронних схем." | choppa -l uk_two
```

Python:

```python
from choppa import SrxDocument, SrxTextIterator

document = SrxDocument(ruleset="choppa/data/srx/languagetool_segment.srx")

text = "This is a sentence. And this is another one. Prof. Smith disagrees."
for sentence in SrxTextIterator(document, "en_two", text):
    print(sentence)
```

The language key is matched against the SRX language maps. For the bundled
LanguageTool rules use `<code>_two` (paragraphs end at two line breaks) or
`<code>_one` (every line break ends a paragraph): `uk_two`, `en_two`,
`de_one`, ...

Streaming a large file:

```python
with open("big_corpus.txt", encoding="utf-8") as reader:
    for sentence in SrxTextIterator(document, "uk_two", reader, buffer_length=1024 * 1024):
        ...
```

# Compatibility with the Java original

The port replicates `java.util.regex.Matcher` semantics on top of the
[regex](https://pypi.org/project/regex/) package:

- `find()` advancement (zero-width matches advance by one character,
  adjacent matches are not skipped);
- exception-rule matching with transparent bounds
  (`pattern.match(text, pos)` sees lookbehind context before `pos`, exactly
  like Java's `useTransparentBounds(true)` + `lookingAt()`);
- Java-only constructs in the rules are translated: `\h`/`\v` become
  `\p{H}`/`\p{V}` ([added to regex on our request](https://github.com/mrabarnett/mrab-regex/issues/477)),
  the `(?U)` flag (Java's `UNICODE_CHARACTER_CLASS`) is dropped because
  Python patterns are Unicode-aware by default, and Java character-class
  intersections like `[\p{L}&&[^rwn]]` are compiled in the regex module's
  V1 mode;
- rules are compiled **without** `MULTILINE`, like in Java, so `^` only
  matches at the start of the text. If you want `^`-anchored rules to fire
  at every line start (pre-1.0 choppa behavior, arguably nicer for texts
  with headings), opt in with `SrxDocument(pattern_flags=regex.M)` — the
  analog of segment 2.0.4's `defaultPatternFlags` option.

Two algorithms are provided:

- `SrxTextIterator` — the "ultimate" algorithm from the original library
  and the one LanguageTool uses: finds break-rule matches, then applies
  merged exception patterns at each candidate break. Supports streaming.
  **Use this one.**
- `AccurateSrxTextIterator` — the legacy "accurate" algorithm (all rules
  matched over the whole text, in memory), kept for completeness. It
  incorporates the [2022 overlapping-exception fix](https://github.com/loomchild/segment/commit/783d4e92230e958aa6d867cbff6f8dea404b9e45)
  from upstream.

Only the SRX 2.0 format and the SAX reader are implemented (the same
parser configuration LanguageTool uses). Schema validation via
`xmlschema` is available with `SrxDocument(validate_ruleset=...)` or
`choppa --validate`.

# Segmentation rules

`choppa/data/srx/languagetool_segment.srx` is an unmodified LanguageTool
`segment.srx` snapshot — see
[`choppa/data/srx/PROVENANCE.md`](choppa/data/srx/PROVENANCE.md) for the
exact upstream commit and refresh instructions. You can also pass any SRX
2.0 file of your own via `SrxDocument(ruleset=...)` or `choppa --srx`.

# Development

```bash
git clone https://github.com/lang-uk/choppa && cd choppa
pip install -e .[test]
pytest tests/            # includes 848 LanguageTool cases for 24 languages
```

`scripts/benchmark.py` benchmarks segmentation and byte-diffs the output
against the Java `segment` CLI; `scripts/extract_lt_tests.py` regenerates
the LanguageTool test fixtures from a LanguageTool checkout.

# Copyrights and kudos

- Python port: [Dmytro Chaplynskyi](https://github.com/dchaplinsky),
  [lang-uk](https://lang.org.ua) project
- Original Java implementation and the pure-Python matcher approach:
  [Jarek Lipski](https://github.com/loomchild)
- CLI and packaging contributions: [Volodymyr Kyrylov](https://github.com/proger)
- Segmentation rules: Daniel Naber, Jaume Ortolà, Andriy Rysin et al —
  the [LanguageTool](https://languagetool.org) team
- Special thanks to Andriy Rysin, the driving force behind the Ukrainian
  language in LanguageTool, and to Matthew Barnett for adding `\p{H}`/`\p{V}`
  to the [regex](https://github.com/mrabarnett/mrab-regex) package

The port is MIT-licensed, same as the original segment library. The
bundled `segment.srx` is distributed under LanguageTool's LGPL-2.1.
