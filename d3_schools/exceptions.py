"""Custom exceptions for d3-schools."""


class D3SchoolsError(Exception):
    """Base exception for d3-schools package."""


class SchoolNotFoundError(D3SchoolsError):
    """Raised when a school cannot be found by any lookup method."""

    def __init__(self, query: str, source: str = ""):
        self.query = query
        self.source = source
        detail = f" in source '{source}'" if source else ""
        super().__init__(f"School not found: '{query}'{detail}")


class AmbiguousMatchError(D3SchoolsError):
    """Raised when a lookup matches multiple schools."""

    def __init__(self, query: str, matches: list):
        self.query = query
        self.matches = matches
        names = ", ".join(str(m) for m in matches[:5])
        super().__init__(
            f"Ambiguous match for '{query}': {len(matches)} schools match ({names})"
        )


class DataLoadingError(D3SchoolsError):
    """Raised when bundled data files cannot be loaded."""

    def __init__(self, file_path: str, reason: str = ""):
        self.file_path = file_path
        self.reason = reason
        detail = f": {reason}" if reason else ""
        super().__init__(f"Failed to load data from '{file_path}'{detail}")
