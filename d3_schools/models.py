"""Data models for d3-schools."""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Optional


class Region(IntEnum):
    """NCAA Division III regions (1-10)."""

    REGION_1 = 1
    REGION_2 = 2
    REGION_3 = 3
    REGION_4 = 4
    REGION_5 = 5
    REGION_6 = 6
    REGION_7 = 7
    REGION_8 = 8
    REGION_9 = 9
    REGION_10 = 10


# All known D3 conferences (as of 2025-26 season)
CONFERENCES = frozenset(
    {
        "AEC",
        "AMCC",
        "ARC",
        "ASC",
        "CC",
        "CCS",
        "CCIW",
        "CGSC",
        "CNE",
        "CUNYAC",
        "E8",
        "GNAC",
        "HCAC",
        "IIAC",
        "INDEP",
        "KCAC",
        "LAX",
        "MACC",
        "MAC-NJ",
        "MASCAC",
        "MWC",
        "MIAA",
        "MIAC",
        "NACC",
        "NCAC",
        "NEAC",
        "NESCAC",
        "NEWMAC",
        "NJAC",
        "NWC",
        "OAC",
        "ODAC",
        "PAC",
        "SAA",
        "SCAC",
        "SCIAC",
        "SKY",
        "SLIAC",
        "SUNYAC",
        "USA South",
        "UAA",
        "WIAC",
    }
)


@dataclass(frozen=True)
class School:
    """Represents a single D3 school with all known name variants.

    Attributes:
        ncaa_id: Stable NCAA ID (primary key, persists across years).
        variants: Open namespace of name variants.
            Keys are variant types:
              - "display": Scott Peterson Display format
              - "massey": Massey Ratings format
              - "d3hoops": D3hoops.com format
              - "stats_ncaa": stats.NCAA.org format
              - "ncaa_manual": NCAA Championship Manual (full official name)
              - "snyder": Matt Snyder Display format
            Values are the school's name in that variant's format.
        conference: Conference abbreviation (e.g., "MIAA", "HCAC").
            Empty string for schools no longer in D3.
        region: NCAA region (1-10). 0 for schools no longer in D3.
        gender: School type — "Coed", "Women", or "Men".
    """

    ncaa_id: str
    variants: Dict[str, str] = field(default_factory=dict)
    conference: str = ""
    region: int = 0
    gender: str = ""

    @property
    def display_name(self) -> str:
        """Human-readable display name (Scott Peterson format).

        Fallback chain: display -> massey cleanup -> "School {ncaa_id}"
        """
        if "display" in self.variants:
            return self.variants["display"]
        if "massey" in self.variants:
            return self.variants["massey"].replace("_", " ")
        return f"School {self.ncaa_id}"

    @property
    def name(self) -> str:
        """Alias for display_name."""
        return self.display_name

    @property
    def is_active(self) -> bool:
        """Whether this school is currently an active D3 member.

        Schools with region=0 and no conference are no longer in D3.
        """
        return self.region > 0

    def get(self, variant: str) -> Optional[str]:
        """Get a specific name variant, or None if not present."""
        return self.variants.get(variant)

    def __repr__(self) -> str:
        status = "" if self.is_active else ", inactive"
        return f"School(ncaa_id={self.ncaa_id!r}, name={self.display_name!r}{status})"
