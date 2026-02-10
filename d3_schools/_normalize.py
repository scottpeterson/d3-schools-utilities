"""Name normalization for consistent lookups."""

import re

# Characters to replace with spaces during normalization
_STRIP_CHARS = re.compile(r"[()._\-]")
# Collapse multiple whitespace to single space
_COLLAPSE_WS = re.compile(r"\s+")


def normalize(name: str) -> str:
    """Normalize a school name for index lookups.

    Lowercases, strips, replaces ()._- with spaces, collapses whitespace.

    Examples:
        >>> normalize("Alfred_St")
        'alfred st'
        >>> normalize("  Hope  ")
        'hope'
        >>> normalize("St. Mary's (MD)")
        "st mary's md"
        >>> normalize("Claremont-M-S")
        'claremont m s'
    """
    s = name.strip().lower()
    s = _STRIP_CHARS.sub(" ", s)
    s = _COLLAPSE_WS.sub(" ", s)
    return s.strip()
