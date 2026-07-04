"""Shared test helpers."""

import functools

from choppa import DEFAULT_SRX_RULESET, SrxDocument


@functools.lru_cache(maxsize=1)
def get_document() -> SrxDocument:
    """The bundled-ruleset document, parsed once per test run."""
    return SrxDocument(ruleset=DEFAULT_SRX_RULESET)
