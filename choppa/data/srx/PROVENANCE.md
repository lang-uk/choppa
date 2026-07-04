# Bundled SRX rules provenance

`languagetool_segment.srx` is an unmodified copy of `segment.srx` from the
[LanguageTool](https://github.com/languagetool-org/languagetool) project:

- Path upstream: `languagetool-core/src/main/resources/org/languagetool/resource/segment.srx`
- Snapshot: the commit recorded in [`LT_COMMIT`](LT_COMMIT) (the
  machine-readable pin; CI asserts the bundled file matches it)
- License: LGPL-2.1 (the file carries no header of its own; it is
  distributed under LanguageTool's license)

To refresh:

```bash
# 1. put the new upstream commit hash (from the drift-watch issue) into
#    choppa/data/srx/LT_COMMIT, then fetch exactly that revision:
curl -sfL -o choppa/data/srx/languagetool_segment.srx \
  "https://raw.githubusercontent.com/languagetool-org/languagetool/$(cat choppa/data/srx/LT_COMMIT)/languagetool-core/src/main/resources/org/languagetool/resource/segment.srx"
```

then update this note and re-run the test suite (including the
LanguageTool tokenizer tests in `tests/test_languagetool_tokenizers.py`).
