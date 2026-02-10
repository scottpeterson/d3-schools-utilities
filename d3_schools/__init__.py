"""d3-schools — Canonical D3 school identity clearinghouse."""

from .exceptions import AmbiguousMatchError, DataLoadingError, SchoolNotFoundError
from .models import CONFERENCES, Region, School
from .registry import SchoolRegistry

__all__ = [
    "CONFERENCES",
    "Region",
    "School",
    "SchoolRegistry",
    "SchoolNotFoundError",
    "AmbiguousMatchError",
    "DataLoadingError",
]
