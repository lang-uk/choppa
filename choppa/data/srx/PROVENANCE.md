# Bundled SRX rules provenance

`languagetool_segment.srx` is an unmodified copy of `segment.srx` from the
[LanguageTool](https://github.com/languagetool-org/languagetool) project:

- Path upstream: `languagetool-core/src/main/resources/org/languagetool/resource/segment.srx`
- Snapshot: commit `d24cd528a777df04b2ea0e5e0ad6990e9a2e9d3a` (2026-05-16)
- License: LGPL-2.1 (the file carries no header of its own; it is
  distributed under LanguageTool's license)

To refresh:

```bash
curl -sL -o choppa/data/srx/languagetool_segment.srx \
  https://raw.githubusercontent.com/languagetool-org/languagetool/master/languagetool-core/src/main/resources/org/languagetool/resource/segment.srx
```

then update this note and re-run the test suite (including the
LanguageTool tokenizer tests in `tests/test_languagetool_tokenizers.py`).
