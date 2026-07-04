# Changelog

## 1.0.0 (2026-07-04)

First feature-complete release, published on PyPI as
[`choppa-srx`](https://pypi.org/project/choppa-srx/) (the import name is
still `choppa`; the bare `choppa` name on PyPI belongs to an unrelated
project).

### Fixed

- **`SrxTextIterator` output is now byte-identical to the original Java
  `segment` library** (verified against segment 2.0.3 on a 100k-line
  real-world Ukrainian corpus, 43,569 segments). The former `JavaMatcher`
  emulation layer searched only a 100-character window from the region
  start, silently missing any break located further away — long
  sentences were never split.
- The streaming mode (reading from a file object) truncated output after
  the first internal buffer shift; the whole upstream streaming test
  suite is now ported and passing.
- Rules are compiled without `MULTILINE`, matching `java.util.regex`
  semantics for `^`-anchored rules. Pass
  `SrxDocument(pattern_flags=regex.M)` to restore the old behavior
  (equivalent of segment 2.0.4's `defaultPatternFlags` option).

### Changed

- `JavaMatcher` is gone. `RuleMatcher` now maps directly onto
  `regex` positional matching, following the `SimpleRuleMatcher`
  approach proposed by Jarek Lipski, with `find()` advancement matching
  Java exactly (zero-width matches advance by one, adjacent matches are
  not skipped). Segmentation is ~5x faster than the Java original and
  ~25x faster than choppa 0.9.
- Bundled `segment.srx` updated to the LanguageTool snapshot of
  2026-05-16 (142 upstream commits, including 13 Ukrainian rule
  updates). Java-only inline flags `(?U)` are now understood by the
  rule translator.
- Modern packaging (`pyproject.toml`), a `choppa` console script, and
  Python 3.9+ support.

### Added

- All 24 LanguageTool SRX sentence-tokenizer test suites ported (848
  cases), regenerable with `scripts/extract_lt_tests.py`.
- Upstream `segment` test-suite ports: streaming iterator suite
  (buffer 60 / margin 10) and `maxLookbehindConstructLength` test.
- `scripts/benchmark.py` — benchmark and byte-level diff against Java
  `segment` output.

## 0.9.0 (2022)

Initial public version: SRX 2.0 SAX parser, accurate and ultimate
iterators, Ukrainian LanguageTool tests, CLI (`python -m choppa`).
