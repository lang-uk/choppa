# Design decisions

The prime directive of this port: **given the same rules and text,
produce byte-identical output to the Java
[segment](https://github.com/loomchild/segment) library** (the `ultimate`
algorithm, which LanguageTool uses). Every decision below follows from
that. Where Python and Java regex semantics genuinely differ, we either
bridge the gap exactly or document the divergence and make it opt-in.

## Why the `regex` package, not stdlib `re`

- LanguageTool's rules use Java's `\h`/`\v` (horizontal/vertical
  whitespace classes). Stdlib `re` rejects `\h` outright, and `\v` in any
  Python pattern means the literal LINE TABULATION character. The `regex`
  package added `\p{HorizSpace}`/`\p{VertSpace}` (`\p{H}`/`\p{V}`) in
  2022.8.17 [at this project's request](https://github.com/mrabarnett/mrab-regex/issues/477),
  and they match Java's classes *exactly* (the package's own `\h` misses
  U+180E). Hence the version floor `regex>=2022.8.17`.
- The rules use Java character-class intersections like
  `[\p{L}&&[^rwn]]`; `regex`'s V1 mode supports them, `re` does not.
- Variable-length lookbehind — which the merged exception patterns rely
  on — is native in `regex` and forbidden in `re`.
- It is also simply fast: large rule alternations are dramatically
  quicker than in `re` thanks to better literal prefiltering.

## The rule translator

Rule patterns pass through `choppa.utils.translate_java_regex` before
compilation (once per unique pattern; results are cached on the
document):

| Java construct | translated to | why |
|---|---|---|
| `\h`, `\v` | `\p{H}`, `\p{V}` | exact Java code point sets (see above) |
| `(?U)` | *(removed)* | Java's `UNICODE_CHARACTER_CLASS` flag; Python `str` patterns are Unicode-aware by default |
| `\\h`, `\(?U\)` etc. | *(untouched)* | escape pairs are consumed first, so escaped text is never rewritten |

`(?U)` deserves a note: JDK 19 changed `\b`/`\w`/`\d` to be ASCII-only by
default ([JDK-8264160](https://bugs.openjdk.org/browse/JDK-8264160)), and
LanguageTool patched its rules with `(?U)` prefixes to restore Unicode
behavior. Python was never affected — its default equals pre-JDK-19 (and
`(?U)`-patched) Java behavior. We verified the JDK question is moot for
real corpora: JDK 17 and JDK 24 ground truth outputs were identical on
every corpus we tested.

## The matcher: Java `Matcher` semantics on Python positional matching

The heart of the port. The original library drives everything through
`java.util.regex.Matcher`; Python has no `Matcher`, but its positional
matching primitives map onto the exact subset segment uses:

| Java (as used by segment) | Python equivalent | notes |
|---|---|---|
| `beforeMatcher.find()` | `before_pattern.search(text, pos)` with `pos` maintained by `RuleMatcher` | Java restarts at the previous match's **end**, advancing one extra char only after a **zero-width** match. We replicate that bump exactly — exception rules wrapped in lookbehind produce *only* zero-width matches, so the whole algorithm's termination depends on it. |
| `find(start)` / `region(start, len)` | `search(text, start)` | resets the search position |
| `afterMatcher.region(break, len); lookingAt()` | `after_pattern.match(text, break)` | anchored at `break`, unanchored at the end |
| `useTransparentBounds(true); region(break, len); lookingAt()` (exception check) | `exception_pattern.match(text, break)` | **Python's `pos` is natively transparent on the left**: lookbehind (and `\b`) see the text before `pos`. This is precisely Java's transparent-bounds `lookingAt()` — the exception check needs zero emulation. |

What does *not* map, and how we handle it:

- **`^` anchoring at a region start.** In Java, `^` matches at
  `region(start, …)` boundaries (anchoring bounds default to on); in
  Python, `^` never matches at `pos`. The SRX rules contain a handful of
  `^`-anchored rules; under Java semantics they only ever fire at the
  start of the text, and that is the behavior we reproduce. See below.
- **Opaque bounds.** Java's `RuleMatcher` uses default (opaque) region
  bounds, so lookbehind in a *break* rule's pattern cannot see before a
  region start right after a segment cut; Python's is transparent there.
  This can only matter for break rules containing lookbehind evaluated
  exactly at a cut point — no such divergence appeared anywhere in
  ~136,000 verified segments, and where it could appear, the transparent
  reading is the less surprising one.

### The old approach, for the record

choppa 0.9 emulated `Matcher` with a `JavaMatcher` class that sliced
100-character windows out of the text. That both crippled performance
(string copies on the hot path) and — the real killer — **silently
dropped any break located more than 100 characters from the region
start**, which is why 0.9 disagreed with Java on real-world texts. The
positional design above was proposed by Jarek Lipski himself in
[lang-uk/choppa#4](https://github.com/lang-uk/choppa/pull/4); 1.0 adopts
it with the `find()` advancement corrected to Java's rule (his prototype
advanced +1 unconditionally, which can skip adjacent matches).

## `^` and MULTILINE

choppa 0.9 compiled all rules with `re.M`, so `^`-anchored rules fired at
every line start. Java does not use MULTILINE, so those rules effectively
fire only at the start of the text. On real corpora this produced about
one divergence per ~2,300 segments (e.g. a Roman-numeral heading `V. `
kept attached to its heading line under MULTILINE — arguably *nicer*
output, but not Java's).

1.0 compiles **without MULTILINE** — byte-compatibility wins, and the
LanguageTool test suites encode Java behavior. The old behavior is one
argument away: `SrxDocument(pattern_flags=regex.M)` (the analog of
segment 2.0.4's `defaultPatternFlags`).

## Finitization and lookbehind length

Java forbids unbounded lookbehind, so the original library rewrites
before-patterns used inside lookbehind: `a*` → `a{0,100}`, `a+` →
`a{1,100}`, `{n,}` → `{n,100}` (`max_lookbehind_construct_length`,
default 100). The `regex` package would allow unbounded lookbehind — but
we finitize anyway, with the same rewriting rules, because the goal is
identical match results, not maximal expressiveness.

## Two algorithms, one default

- **`SrxTextIterator`** ("ultimate") — matches break rules first, then
  applies a merged exception pattern (an alternation of
  `(?<=before)(?=after)` for every exception rule preceding the break
  rule in the SRX file — SRX is first-match-wins) at each candidate
  break. Supports streaming: fixed buffer, margin-deferred matches near
  the buffer edge, buffer shift after each emitted segment. This is what
  LanguageTool runs and what the byte-compatibility guarantee covers.
- **`AccurateSrxTextIterator`** ("accurate") — the legacy design:
  every rule (break and exception) is a live matcher over the whole
  text. Kept because the Java library keeps it, with the 2022 upstream
  fix (exception before-patterns wrapped in finitized lookbehind so
  overlapping exceptions work). It is much slower on rule-heavy SRX
  files and does not stream.

## Performance model

No algorithmic cleverness beyond the original design — the speed comes
from removing waste: positional matching instead of window slicing (zero
string copies on the hot path), per-document compiled-pattern and
rule-manager caches, memoized language-map resolution. Runtime is
regex-bound; see the README's
[Performance and verification](../README.md#performance-and-verification)
table for numbers and reproduction steps.

## Testing philosophy

Three independent layers, because each catches what the others miss:

1. **Ported upstream unit tests** (21 segmentation scenarios × string /
   accurate / streaming harnesses, matcher-level tests) — catches
   algorithm-structure regressions; the streaming harness found a real
   port bug (missing position reset after buffer shift) the day it was
   added.
2. **LanguageTool's 24 language suites** (848 cases, auto-extracted from
   the Java sources by `scripts/extract_lt_tests.py`) — catches rule
   semantics regressions against the rules' authors' intent.
3. **Corpus-level byte-diff against the Java binary**
   (`scripts/benchmark.py --java`) — catches everything else, including
   divergences no one thought to write a test for. ~136,000 segments,
   uk + en, zero diffs.
