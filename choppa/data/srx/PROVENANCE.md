# Bundled SRX rules provenance

`languagetool_segment.srx` is an unmodified copy of `segment.srx` from the
[LanguageTool](https://github.com/languagetool-org/languagetool) project:

- Path upstream: `languagetool-core/src/main/resources/org/languagetool/resource/segment.srx`
- Snapshot: the commit recorded in [`LT_COMMIT`](LT_COMMIT) (the
  machine-readable pin; CI asserts the bundled file matches it)
- License: LGPL-2.1 (the file carries no header of its own; it is
  distributed under LanguageTool's license)

LanguageTool compiles these rules with `UNICODE_CHARACTER_CLASS` set
(`SrxTools` passes segment's `DEFAULT_PATTERN_FLAGS_PARAMETER`). choppa
needs no equivalent — Python patterns are Unicode-aware by default — but
the Java side of the corpus differential does; see
[`docs/design.md`](../../../docs/design.md).

To refresh:

```bash
# 1. Pin. Take the newest upstream commit that touches segment.srx --
#    NOT necessarily the hash quoted in the drift-watch issue, which is
#    however old that issue is. Check first:
curl -s "https://api.github.com/repos/languagetool-org/languagetool/commits\
?path=languagetool-core/src/main/resources/org/languagetool/resource/segment.srx&per_page=1" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['sha'])"

# 2. Put that hash in choppa/data/srx/LT_COMMIT, then fetch exactly it:
curl -sfL -o choppa/data/srx/languagetool_segment.srx \
  "https://raw.githubusercontent.com/languagetool-org/languagetool/$(cat choppa/data/srx/LT_COMMIT)/languagetool-core/src/main/resources/org/languagetool/resource/segment.srx"

# 3. Re-extract the LanguageTool test fixtures from the SAME commit, so
#    the expectations match the rules (upstream ships rule changes and
#    test changes together):
python scripts/extract_lt_tests.py <languagetool-checkout>

# 4. Test suite, then the corpus differential (see the README's
#    "Performance and verification" for the Java ground-truth commands).
pytest tests/
```

Read the upstream diff before trusting a green run: rule changes can come
with *code* changes on the LanguageTool side that alter how the rules are
compiled, and those do not show up in the `.srx` alone.
