"""SchoolRegistry — the D3 school identity clearinghouse."""

import csv
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from ._normalize import normalize
from .exceptions import AmbiguousMatchError, DataLoadingError, SchoolNotFoundError
from .models import School

# Metadata columns that are NOT name variants
_METADATA_COLS = frozenset({"ncaa_id", "conference", "region", "gender"})

# Default bundled data directory
_DATA_DIR = Path(__file__).parent / "data"


class SchoolRegistry:
    """The D3 school identity clearinghouse.

    Loads bundled CSV data, builds O(1) indexes, and resolves any name
    variant to any other.

    Usage:
        >>> registry = SchoolRegistry()
        >>> registry.find("Hope").display_name
        'Hope'
        >>> registry.resolve("Anderson_IN", output="display")
        'Anderson'
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self._data_dir = Path(data_dir) if data_dir else _DATA_DIR
        self._schools: Dict[str, School] = {}  # ncaa_id -> School
        self._massey_index: Dict[str, Dict[str, str]] = {}  # year -> {massey_id -> ncaa_id}
        self._variant_index: Dict[str, Dict[str, School]] = {}  # variant_type -> {norm_name -> School}
        self._global_index: Dict[str, List[School]] = {}  # norm_name -> [School, ...]
        self._variant_types: List[str] = []
        self._load()

    # ── Loading ──────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load all bundled data files and build indexes."""
        self._load_schools()
        self._load_aliases()
        self._load_massey_years()

    def _load_schools(self) -> None:
        """Load schools.csv and build primary indexes."""
        schools_path = self._data_dir / "schools.csv"
        if not schools_path.exists():
            raise DataLoadingError(str(schools_path), "File not found")

        with open(schools_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise DataLoadingError(str(schools_path), "No headers found")

            # Discover variant types from headers (everything not in metadata)
            self._variant_types = [
                h for h in reader.fieldnames if h not in _METADATA_COLS and h.strip()
            ]

            for row in reader:
                ncaa_id = row.get("ncaa_id", "").strip()
                if not ncaa_id:
                    continue

                # Build variants dict from non-empty, non-metadata columns
                variants = {}
                for vtype in self._variant_types:
                    val = row.get(vtype, "").strip()
                    if val and val != "-":
                        variants[vtype] = val

                region_str = row.get("region", "").strip()
                try:
                    region = int(region_str) if region_str else 0
                except ValueError:
                    region = 0

                school = School(
                    ncaa_id=ncaa_id,
                    variants=variants,
                    conference=row.get("conference", "").strip(),
                    region=region,
                    gender=row.get("gender", "").strip(),
                )
                self._schools[ncaa_id] = school
                self._index_school(school)

    def _index_school(self, school: School) -> None:
        """Add a school to all lookup indexes."""
        for vtype, name in school.variants.items():
            norm = normalize(name)
            if not norm:
                continue

            # Variant-scoped index
            if vtype not in self._variant_index:
                self._variant_index[vtype] = {}
            self._variant_index[vtype][norm] = school

            # Global index (list for ambiguity handling)
            if norm not in self._global_index:
                self._global_index[norm] = []
            if school not in self._global_index[norm]:
                self._global_index[norm].append(school)

    def _load_aliases(self) -> None:
        """Load aliases.csv and add to indexes."""
        aliases_path = self._data_dir / "aliases.csv"
        if not aliases_path.exists():
            return  # Aliases are optional

        with open(aliases_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                alias_value = row.get("alias_value", "").strip()
                variant_type = row.get("variant_type", "").strip()
                ncaa_id = row.get("ncaa_id", "").strip()

                if not alias_value or not ncaa_id:
                    continue

                school = self._schools.get(ncaa_id)
                if school is None:
                    continue

                norm = normalize(alias_value)
                if not norm:
                    continue

                # Add to variant-scoped index
                if variant_type:
                    if variant_type not in self._variant_index:
                        self._variant_index[variant_type] = {}
                    self._variant_index[variant_type][norm] = school

                # Add to global index
                if norm not in self._global_index:
                    self._global_index[norm] = []
                if school not in self._global_index[norm]:
                    self._global_index[norm].append(school)

    def _load_massey_years(self) -> None:
        """Load all massey CSV files.

        Supports two directory layouts:
          - massey/{sport}/{year}.csv  (sport-scoped, e.g., massey/wbb/2026.csv)
          - massey/{year}.csv          (legacy flat layout)

        The index key is "{sport}:{year}" for sport-scoped files, or just
        "{year}" for flat files. The public API accepts both forms.
        """
        massey_dir = self._data_dir / "massey"
        if not massey_dir.exists():
            return

        # Sport-scoped: massey/{sport}/{year}.csv
        for sport_dir in sorted(massey_dir.iterdir()):
            if sport_dir.is_dir():
                sport = sport_dir.name
                for csv_file in sorted(sport_dir.glob("*.csv")):
                    year = csv_file.stem
                    key = f"{sport}:{year}"
                    self._massey_index[key] = {}
                    # Also register under bare year if it's the only sport
                    if year not in self._massey_index:
                        self._massey_index[year] = {}
                    with open(csv_file, "r", encoding="utf-8-sig") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            massey_id = row.get("massey_id", "").strip()
                            ncaa_id = row.get("ncaa_id", "").strip()
                            if massey_id and ncaa_id:
                                self._massey_index[key][massey_id] = ncaa_id
                                self._massey_index[year][massey_id] = ncaa_id

        # Flat layout: massey/{year}.csv
        for csv_file in sorted(massey_dir.glob("*.csv")):
            year = csv_file.stem
            if year not in self._massey_index:
                self._massey_index[year] = {}
            with open(csv_file, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    massey_id = row.get("massey_id", "").strip()
                    ncaa_id = row.get("ncaa_id", "").strip()
                    if massey_id and ncaa_id:
                        self._massey_index[year][massey_id] = ncaa_id

    # ── Overlay ──────────────────────────────────────────────────────

    def load_overlay(self, path: str) -> None:
        """Load an overlay CSV with additional name variants.

        The overlay CSV must have an 'ncaa_id' column. All other columns
        are treated as name variants and merged into existing schools.
        """
        overlay_path = Path(path)
        if not overlay_path.exists():
            raise DataLoadingError(str(overlay_path), "File not found")

        with open(overlay_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise DataLoadingError(str(overlay_path), "No headers found")

            overlay_vtypes = [
                h for h in reader.fieldnames if h not in _METADATA_COLS and h.strip()
            ]

            for row in reader:
                ncaa_id = row.get("ncaa_id", "").strip()
                if not ncaa_id or ncaa_id not in self._schools:
                    continue

                old_school = self._schools[ncaa_id]
                # Merge new variants into existing
                new_variants = dict(old_school.variants)
                for vtype in overlay_vtypes:
                    val = row.get(vtype, "").strip()
                    if val and val != "-":
                        new_variants[vtype] = val

                updated = School(
                    ncaa_id=ncaa_id,
                    variants=new_variants,
                    conference=old_school.conference,
                    region=old_school.region,  # preserved from original
                    gender=old_school.gender,
                )
                self._schools[ncaa_id] = updated
                self._index_school(updated)

            # Track new variant types
            for vtype in overlay_vtypes:
                if vtype not in self._variant_types:
                    self._variant_types.append(vtype)

    # ── Core Lookups ─────────────────────────────────────────────────

    def get(self, ncaa_id: str) -> Optional[School]:
        """Look up a school by NCAA ID (primary key)."""
        return self._schools.get(ncaa_id.strip())

    def get_by_massey_id(self, massey_id: str, year: str) -> Optional[School]:
        """Look up a school by Massey ID for a given year."""
        year_map = self._massey_index.get(year, {})
        ncaa_id = year_map.get(massey_id.strip())
        if ncaa_id:
            return self._schools.get(ncaa_id)
        return None

    # ── Find ─────────────────────────────────────────────────────────

    def find(self, name: str, source: str = "") -> Optional[School]:
        """Find a school by any name variant. Returns None if ambiguous.

        Args:
            name: The name to search for.
            source: Optional variant type to restrict the search
                    (e.g., "d3hoops", "snyder").
        """
        norm = normalize(name)
        if not norm:
            return None

        # Try NCAA ID first
        if name.strip() in self._schools:
            return self._schools[name.strip()]

        # Scoped search
        if source:
            idx = self._variant_index.get(source, {})
            return idx.get(norm)

        # Global search — return only if unambiguous
        matches = self._global_index.get(norm, [])
        if len(matches) == 1:
            return matches[0]
        return None

    def find_all(self, name: str) -> List[School]:
        """Find all schools matching a name variant."""
        norm = normalize(name)
        if not norm:
            return []
        return list(self._global_index.get(norm, []))

    # ── Resolve ──────────────────────────────────────────────────────

    def resolve(
        self, name: str, output: str = "display", source: str = ""
    ) -> Optional[str]:
        """Resolve any name variant to a desired output format.

        Args:
            name: Input name (any variant).
            output: Desired output variant type (e.g., "display", "d3hoops",
                    "ncaa_id", "massey").
            source: Optional source variant type to narrow search.

        Returns:
            The name in the requested format, or None if not found.
        """
        school = self.find(name, source=source)
        if school is None:
            return None

        if output == "ncaa_id":
            return school.ncaa_id
        return school.get(output) or school.display_name

    # ── Massey ID Bridge ─────────────────────────────────────────────

    def massey_id_to_ncaa_id(self, massey_id: str, year: str) -> Optional[str]:
        """Convert a Massey ID to an NCAA ID for a given year."""
        year_map = self._massey_index.get(year, {})
        return year_map.get(massey_id.strip())

    def ncaa_id_to_massey_id(self, ncaa_id: str, year: str) -> Optional[str]:
        """Convert an NCAA ID to a Massey ID for a given year."""
        year_map = self._massey_index.get(year, {})
        ncaa_id = ncaa_id.strip()
        for mid, nid in year_map.items():
            if nid == ncaa_id:
                return mid
        return None

    # ── Backward-Compatible Dicts ────────────────────────────────────

    def id_to_name(
        self, id_type: str = "massey", year: str = "", variant: str = "display"
    ) -> Dict[str, str]:
        """Build a {id: name} dictionary.

        For id_type="massey", requires a year. Returns Massey ID -> display name.
        For id_type="ncaa", returns NCAA ID -> display name.
        """
        result: Dict[str, str] = {}
        if id_type == "massey":
            year_map = self._massey_index.get(year, {})
            for massey_id, ncaa_id in year_map.items():
                school = self._schools.get(ncaa_id)
                if school:
                    name = school.get(variant) or school.display_name
                    result[massey_id] = name
        elif id_type == "ncaa":
            for ncaa_id, school in self._schools.items():
                name = school.get(variant) or school.display_name
                result[ncaa_id] = name
        return result

    def name_to_id(
        self, id_type: str = "massey", year: str = "", variant: str = "display"
    ) -> Dict[str, str]:
        """Build a {name: id} dictionary (inverse of id_to_name)."""
        forward = self.id_to_name(id_type=id_type, year=year, variant=variant)
        return {name: id_ for id_, name in forward.items()}

    # ── Metadata Queries ─────────────────────────────────────────────

    def all_schools(self) -> List[School]:
        """Return all schools in the registry."""
        return list(self._schools.values())

    def schools_in_conference(self, conference: str) -> List[School]:
        """Return all schools in a given conference."""
        conf = conference.strip().upper()
        return [s for s in self._schools.values() if s.conference.upper() == conf]

    @property
    def variant_types(self) -> List[str]:
        """Return all known variant types."""
        return list(self._variant_types)

    # ── Dunder Methods ───────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._schools)

    def __contains__(self, ncaa_id: str) -> bool:
        return ncaa_id in self._schools

    def __getitem__(self, ncaa_id: str) -> School:
        school = self._schools.get(ncaa_id)
        if school is None:
            raise SchoolNotFoundError(ncaa_id)
        return school

    def __iter__(self) -> Iterator[School]:
        return iter(self._schools.values())

    def __repr__(self) -> str:
        return f"SchoolRegistry({len(self._schools)} schools)"
