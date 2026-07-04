# Draft close-out comments (post manually or ask Claude to post after review)

## lang-uk/choppa PR #4 (loomchild's SimpleRuleMatcher) — comment & close

> Closing the loop at last — and with good news. PR #6 finishes the port
> using exactly this approach: `RuleMatcher` is now pure positional
> matching, applied to the ultimate algorithm (`SrxTextIterator`) as well.
> The one adjustment was the advancement rule: this PR moved on from
> `break_position + 1` unconditionally, while Java's `Matcher.find()`
> restarts at the previous match end and only bumps +1 after zero-width
> matches — the unconditional +1 could skip adjacent matches.
>
> The real culprit behind the discrepancies I saw in 2022 turned out to be
> elsewhere: my `JavaMatcher` only searched a 100-character window from the
> region start, so any break further away was silently dropped. With your
> approach (and no window), the output is now byte-identical to segment
> 2.0.3 on a 100k-line Ukrainian corpus (43,569 segments, zero diffs) and
> ~5x faster than the Java CLI. You were right all along that JavaMatcher
> emulation was unnecessary — thank you for the patience and for both
> prototypes. Credited in the changelog and AUTHORS.

## lang-uk/choppa PR #5 (proger's benchmark) — comment & close

> Superseded by `scripts/benchmark.py` on main (which also byte-diffs
> against the Java segment output), and the CLI improvements from this PR
> (line-by-line mode, iterator selection) landed as part of the `choppa`
> console script in #6. Fresh numbers on 100k lines / 11 MB: 4.7s for
> `SrxTextIterator` (vs 141.8s for the best 2022 configuration and ~55s
> for nlp_uk), output byte-identical to Java. Thanks for the benchmark —
> the sentence-count gap it exposed (84,018 vs 84,452) was the thread that
> led to the 100-char window bug.

## loomchild/segment issue #22 — courtesy note

> An epilogue, three and a half years later: the Python port is finished
> and released as [choppa-srx](https://pypi.org/project/choppa-srx/).
> `SrxTextIterator` output is byte-identical to segment 2.0.3 on a
> 100k-line real-world corpus, all 848 sentence-tokenization cases from
> LanguageTool's 24 language test suites pass, and it runs ~5x faster than
> the Java CLI thanks to your SimpleRuleMatcher idea (Python's
> `pattern.match(text, pos)` turns out to be exactly
> `useTransparentBounds(true) + lookingAt()`, so the exception check needs
> no emulation at all). Dziękuję bardzo once more, Jarek!
