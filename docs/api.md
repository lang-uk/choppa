# API contract

The public API is small and deliberately stable: everything importable
from the top-level `choppa` package, the two iterator constructors, and
the `choppa` command line. Everything else (`choppa.rule_matcher`,
`choppa.rule_manager`, `choppa.text_manager`, `choppa.utils`,
`choppa.structures`) is internal machinery that mirrors the Java
library's layout; it may change between minor versions.

**The core behavioral contract: given the same SRX rules, the same
language key, and the same text, `SrxTextIterator` produces byte-identical
output to the Java [segment](https://github.com/loomchild/segment)
library's `ultimate` algorithm** — the engine LanguageTool uses. See
[design.md](design.md) for how that is achieved and
[the README](../README.md#performance-and-verification) for the evidence.

## Package exports

```python
from choppa import (
    SrxDocument,              # rules container + pattern compiler
    SrxTextIterator,          # the segmenter you want
    AccurateSrxTextIterator,  # legacy algorithm, kept for completeness
    DEFAULT_SRX_RULESET,      # Path to the bundled LanguageTool segment.srx
    SRX_2_XSD,                # Path to the bundled SRX 2.0 XML schema
)
from choppa.iterators import ITERATORS  # {"SrxTextIterator": ..., "AccurateSrxTextIterator": ...}
```

## SrxDocument

```python
SrxDocument(
    cascade=True,           # apply ALL matching <languagemap> rule sets, in order
    ruleset=None,           # str/Path to an SRX 2.0 file; None = empty document
    validate_ruleset=None,  # str/Path to an XSD (e.g. SRX_2_XSD); None = no validation
    pattern_flags=0,        # extra regex-module flags OR-ed into every compiled rule
)
```

- Parses SRX 2.0 with a SAX parser (the same configuration LanguageTool
  uses). SRX 1.0 is not supported.
- Compiled rule patterns and rule managers are cached on the document, so
  reuse one `SrxDocument` across texts — construction parses and caching
  warms up on first segmentation.
- `pattern_flags` is the analog of segment 2.0.4's `defaultPatternFlags`
  option. The flags are OR-ed on top of the required base
  (`regex.U | regex.V1`). The main use case is `regex.M` — see
  [design.md](design.md#-and-multiline) before reaching for it.
- Java-only constructs in rules (`\h`, `\v`, `(?U)`, `[a&&[^b]]`
  intersections) are translated/handled automatically.

Useful members: `get_language_rule_list(language_code)` returns the
matching rule sets (memoized), `compile(pattern)` compiles a rule pattern
through the translation layer and cache.

## SrxTextIterator

```python
SrxTextIterator(
    document,                             # SrxDocument
    language_code,                        # matched against <languagemap> patterns
    text,                                 # str, or a file-like reader for streaming
    buffer_length=1024 * 1024,            # streaming read buffer (characters)
    max_lookbehind_construct_length=100,  # finitization bound for lookbehind
    margin=128,                           # streaming margin (0 when text is a str)
)
```

A standard Python iterator: `for sentence in SrxTextIterator(...)`.
Segments concatenate back to the exact input text — no characters are
added, dropped, or trimmed (trailing whitespace stays with the segment
that contains it).

- **Language keys.** For the bundled LanguageTool rules the key is
  `<code>_two` (paragraphs end at two consecutive line breaks — the
  LanguageTool default) or `<code>_one` (every line break ends a
  paragraph): `uk_two`, `en_two`, `de_one`, ... Any string works; it is
  regex-matched against the `<languagemap>` patterns in the SRX file.
- **Streaming.** Pass a file-like object instead of a `str` and text is
  read incrementally with a fixed `buffer_length`. Memory use is
  O(buffer), not O(input). Hard constraint inherited from the original
  design: **no single segment may be longer than the buffer**; if that
  happens, `Exception("Buffer too short ...")` is raised. The margin
  defers matches near the buffer's end until more text is read, so rules
  never match across a truncated boundary.
- Iterators are single-use and not thread-safe; the shared `SrxDocument`
  is safe to reuse across iterators once warmed (its caches are only
  appended to).

## AccurateSrxTextIterator

Same constructor shape (no `buffer_length`/`margin` — string input only).
The legacy "accurate" algorithm from the original library: every rule is
matched over the whole text. Includes the upstream
[2022 overlapping-exception fix](https://github.com/loomchild/segment/commit/783d4e92230e958aa6d867cbff6f8dea404b9e45).
Slower on rule-heavy SRX files and kept mainly for parity with the Java
library; prefer `SrxTextIterator`.

## Command line

```
choppa [input-file] [-l LANG] [-s RULES.srx] [-i ITERATOR]
       [--line-by-line] [--buffer-length N]
       [--max-lookbehind-construct-length N] [--validate]
```

Reads a file or stdin, writes one segment per line. The default mode
streams the input through `SrxTextIterator`'s buffer (constant memory);
`--line-by-line` segments each line independently (faster when sentences
never span lines, e.g. one-paragraph-per-line corpora). `python -m choppa`
is equivalent.

## Exceptions

- Invalid SRX + `validate_ruleset` → `xmlschema` validation error.
- Streaming with a segment longer than the buffer → `Exception("Buffer
  too short ...")` (message suggests `buffer_length`).
- Unknown `language_code` is not an error: only the `<languagemap>`
  entries whose patterns match contribute rules (Java behaves the same
  way). With the bundled LanguageTool rules an unknown key like
  `xx_two` still matches the paragraph-break and cross-language maps but
  no language-specific sentence rules — `"One sentence. And another
  one."` comes back as a single segment. If your language has no rule
  set of its own, an existing key with similar punctuation conventions
  (e.g. `en_two`) usually splits better than the fallback.

## Versioning

The distribution is `choppa-srx` (PyPI), the import name is `choppa`.
Semantic versioning from 1.0.0: byte-compatibility with Java segment and
the exports above are the contract; internal modules are not.
