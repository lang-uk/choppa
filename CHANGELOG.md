# Changelog

## Unreleased

### Changed

- Bundled `segment.srx` refreshed to the LanguageTool snapshot of
  2026-07-23 (`61bf3ff8`). Upstream removed the inline `(?U)` flags —
  it now compiles every rule with `UNICODE_CHARACTER_CLASS` instead —
  added Catalan sentence-break rules, and rewrote the
  `ByTwoLineBreaks` rule to spell out ASCII whitespace explicitly.
  Ukrainian, English and Russian segmentation is unchanged; Catalan
  gains breaks (`... a X. No és ...`, `... Sargó I. El nom ...`).
- LanguageTool test fixtures re-extracted at the same commit: 851 cases
  (was 848; the three new ones cover the Catalan rules).

### Fixed

- Paragraph breaks no longer fire on Unicode whitespace between two
  newlines (`\n \n`). Python's `\s` is Unicode-aware, so the old
  `\r?\n\s*\r?\n` rule made choppa break where Java did not — a
  divergence that never surfaced on the benchmark corpora. Upstream's
  explicit `[ \t\n\x0B\f\r]*` removes it.

### Added

- `scripts/lt_java_srx.py` — writes the rules with LanguageTool's
  pattern flags spelled out inline, which segment 2.0.3 cannot be told to
  use, so the corpus differential and the CI byte-identity gate compare
  against the semantics LanguageTool actually uses. With it the ground
  truth is JDK-independent (17, 21 and 24 produce identical output; the
  pristine file does not).

## 1.0.0 (2026-07-04)

First feature-complete release, published on PyPI as
[`choppa-srx`](https://pypi.org/project/choppa-srx/) (the import name is
still `choppa`; the bare `choppa` name on PyPI belongs to an unrelated
project).

### Fixed

- **`SrxTextIterator` output is now byte-identical to the original Java
  `segment` library** (verified against segment 2.0.3 on ~136,000
  segments across seven real-world Ukrainian and English corpora; see
  the README's "Performance and verification" section). The former `JavaMatcher`
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
