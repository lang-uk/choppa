# Project heritage

choppa stands on three older projects, and its history is mostly the
story of getting them to agree.

## The ancestry

- **SRX** (Segmentation Rules eXchange) — a LISA/OSCAR standard: an XML
  format of cascading break/no-break regex rule pairs for splitting text
  into segments, language-selectable via regex language maps.
- **[segment](https://github.com/loomchild/segment)** — the reference
  Java implementation by [Jarek Lipski](https://github.com/loomchild)
  (loomchild), written mostly in 2007–2008, MIT-licensed, published on
  Maven Central as `net.loomchild:segment`. Described in Miłkowski &
  Lipski (2011), *Using SRX Standard for Sentence Segmentation*, LTC
  2009, LNAI 6562. It ships three algorithms; the streaming `ultimate`
  one (`SrxTextIterator`) is the modern default, `accurate` and `fast`
  are legacy.
- **[LanguageTool](https://github.com/languagetool-org/languagetool)** —
  maintains the de-facto standard multi-language rule file
  (`segment.srx`, ~30 languages, 150+ contributors) and drives segment
  in production for sentence splitting. The Ukrainian rules — the reason
  this port exists — are largely Andriy Rysin's work.

## 2022: the port and the bug hunt

Dmytro Chaplynskyi ([lang-uk](https://lang.org.ua)) ported the library to
Python to bring LanguageTool-quality Ukrainian sentence splitting to the
Python world. The port surfaced a genuine upstream bug — the accurate
algorithm mishandled overlapping exception rules
([loomchild/segment#22](https://github.com/loomchild/segment/issues/22)) —
which Jarek fixed in Java
([`783d4e9`](https://github.com/loomchild/segment/commit/783d4e92230e958aa6d867cbff6f8dea404b9e45))
along with contributing two alternative fixes to choppa itself (PRs
[#3](https://github.com/lang-uk/choppa/pull/3) and
[#4](https://github.com/lang-uk/choppa/pull/4)). Volodymyr Kyrylov
(proger) contributed packaging, the first CLI, and the benchmark that
recorded the port disagreeing with the Java engine on real corpora
([#5](https://github.com/lang-uk/choppa/pull/5)). The disagreement went
undiagnosed and the project stalled at 0.9 — correct on every unit test,
subtly wrong on real text.

## 2026: completion

The 1.0 effort found the actual culprit — the `JavaMatcher` emulation
layer searched only a 100-character window, silently dropping distant
breaks (plus a second, independent bug that truncated streaming output) —
and replaced the emulation with direct positional matching, adopting the
approach Jarek had proposed in PR #4 with the `find()` advancement
corrected to Java semantics. The result is byte-identical to the Java
engine on every corpus tested and several times faster. The rules were
refreshed to the current LanguageTool snapshot, all 24 of LanguageTool's
sentence-tokenizer test suites were ported, and the project shipped to
PyPI as `choppa-srx`.

Full technical detail: [design.md](design.md). Names and credit:
[AUTHORS.md](../AUTHORS.md) and the README's kudos section.
