#!/usr/bin/env python3
"""Generate d3_schools/data/schools.csv by merging data from d3-bball-npi sources.

Sources:
  1. D3 Schools Name Mapping.csv — master list of ~997 schools with NCAA IDs
  2. teams_mapping.txt — Massey names + display names (per-year, used for massey variant)
  3. snyder_team_mapping.txt — Snyder efficiency rating names

The master file (D3 Schools Name Mapping.csv) provides:
  - ncaa_id (NCAA ID column)
  - massey (Massey column — the massey-style name used in the master file)
  - d3hoops (d3hoops column)
  - stats_ncaa (stats.NCAA.org column)
  - ncaa_manual (NCAA Championship Manual column)
  - conference, region, gender

The teams_mapping.txt provides a year-specific "display" name (team_name column).
The snyder_team_mapping.txt provides the "snyder" variant.

Strategy:
  - Primary key: ncaa_id from "D3 Schools Name Mapping.csv"
  - Join teams_mapping.txt by matching display names to find massey_id -> ncaa_id link
  - Join snyder_team_mapping.txt by matching the "NAME NEEDED" column to display names
"""

import csv
import sys
from pathlib import Path


def load_master_mapping(path: Path) -> list[dict]:
    """Load D3 Schools Name Mapping.csv."""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ncaa_id = row.get("NCAA ID", "").strip()
            if not ncaa_id:
                continue
            rows.append(
                {
                    "ncaa_id": ncaa_id,
                    "massey": row.get("Massey", "").strip(),
                    "d3hoops": row.get("d3hoops", "").strip(),
                    "stats_ncaa": row.get("stats.NCAA.org", "").strip(),
                    "ncaa_manual": row.get("NCAA Championship Manual", "").strip(),
                    "conference": row.get("Conference", "").strip(),
                    "region": row.get("Region", "").strip(),
                    "gender": row.get("Gender", "").strip(),
                }
            )
    return rows


def load_teams_mapping(path: Path) -> dict[str, dict]:
    """Load teams_mapping.txt -> {display_name: {massey_name, team_id}}."""
    mapping = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            display = row.get("team_name", "").strip()
            massey = row.get("massey_name", "").strip()
            if display:
                mapping[display] = {
                    "massey_name": massey,
                    "team_id": row.get("team_id", "").strip(),
                }
    return mapping


def load_snyder_mapping(path: Path) -> dict[str, str]:
    """Load snyder_team_mapping.txt -> {name_needed: snyder_name}."""
    mapping = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            snyder = row.get("SNYDER NAME", "").strip()
            needed = row.get("NAME NEEDED", "").strip()
            if needed and snyder:
                mapping[needed] = snyder
    return mapping


def _normalize_massey(name: str) -> str:
    """Normalize a massey name for matching: lowercase, underscores/hyphens to spaces."""
    return name.lower().replace("_", " ").replace("-", " ").strip()


def build_display_to_ncaa(master_rows: list[dict], teams_mapping: dict) -> dict[str, str]:
    """Build display_name -> ncaa_id mapping by matching massey names.

    The master file has 'massey' names like "J&W RI", "SW Univ TX".
    The teams_mapping has massey names like "J&W_RI", "SW_Univ_TX".
    We normalize both sides (underscores/hyphens to spaces, lowercase) to match.
    """
    # Build normalized massey_name -> ncaa_id from master
    massey_to_ncaa = {}
    for row in master_rows:
        massey = row["massey"]
        if massey and massey != "-":
            massey_to_ncaa[_normalize_massey(massey)] = row["ncaa_id"]

    display_to_ncaa = {}
    for display, info in teams_mapping.items():
        massey = info["massey_name"]
        ncaa_id = massey_to_ncaa.get(_normalize_massey(massey))
        if ncaa_id:
            display_to_ncaa[display] = ncaa_id
    return display_to_ncaa


def main():
    npi_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "projects" / "d3-bball-npi"
    output_dir = Path(__file__).parent.parent / "d3_schools" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load sources
    master_path = npi_root / "myapp" / "data" / "D3 Schools Name Mapping.csv"
    teams_mapping_path = npi_root / "myapp" / "data" / "2026" / "teams_mapping.txt"
    snyder_path = npi_root / "myapp" / "data" / "2026" / "snyder_team_mapping.txt"

    print(f"Loading master mapping from {master_path}...")
    master_rows = load_master_mapping(master_path)
    print(f"  Loaded {len(master_rows)} schools")

    print(f"Loading teams_mapping from {teams_mapping_path}...")
    teams_mapping = load_teams_mapping(teams_mapping_path)
    print(f"  Loaded {len(teams_mapping)} team mappings")

    print(f"Loading snyder mapping from {snyder_path}...")
    snyder_mapping = load_snyder_mapping(snyder_path)
    print(f"  Loaded {len(snyder_mapping)} snyder mappings")

    # Build display_name -> ncaa_id bridge
    display_to_ncaa = build_display_to_ncaa(master_rows, teams_mapping)
    print(f"  Matched {len(display_to_ncaa)} display names to NCAA IDs")

    # Build ncaa_id -> display_name and ncaa_id -> snyder_name
    ncaa_to_display = {}
    for display, ncaa_id in display_to_ncaa.items():
        ncaa_to_display[ncaa_id] = display

    # Build a comprehensive name -> ncaa_id lookup for snyder matching
    # Include display names, d3hoops, stats_ncaa, massey (all forms)
    all_names_to_ncaa = dict(display_to_ncaa)  # display -> ncaa_id
    for row in master_rows:
        ncaa_id = row["ncaa_id"]
        for col in ["massey", "d3hoops", "stats_ncaa"]:
            val = row[col]
            if val and val != "-":
                all_names_to_ncaa[val] = ncaa_id
                all_names_to_ncaa[val.replace("_", " ")] = ncaa_id

    ncaa_to_snyder = {}
    for needed, snyder in snyder_mapping.items():
        ncaa_id = all_names_to_ncaa.get(needed)
        if ncaa_id:
            ncaa_to_snyder[ncaa_id] = snyder

    # Build output rows
    fieldnames = [
        "ncaa_id",
        "display",
        "massey",
        "d3hoops",
        "stats_ncaa",
        "ncaa_manual",
        "snyder",
        "conference",
        "region",
        "gender",
    ]

    output_rows = []
    for row in master_rows:
        ncaa_id = row["ncaa_id"]
        display = ncaa_to_display.get(ncaa_id, "")
        # If no display from teams_mapping, use massey name with underscores replaced
        if not display and row["massey"] and row["massey"] != "-":
            display = row["massey"].replace("_", " ")

        snyder = ncaa_to_snyder.get(ncaa_id, "")

        # Clean up dash placeholders
        conference = row["conference"] if row["conference"] != "-" else ""
        region = row["region"] if row["region"] != "-" else ""
        ncaa_manual = row["ncaa_manual"] if row["ncaa_manual"] != "-" else ""

        out = {
            "ncaa_id": ncaa_id,
            "display": display,
            "massey": row["massey"] if row["massey"] != "-" else "",
            "d3hoops": row["d3hoops"] if row["d3hoops"] != "-" else "",
            "stats_ncaa": row["stats_ncaa"] if row["stats_ncaa"] != "-" else "",
            "ncaa_manual": ncaa_manual,
            "snyder": snyder,
            "conference": conference,
            "region": region,
            "gender": row["gender"],
        }
        output_rows.append(out)

    # Write schools.csv
    output_path = output_dir / "schools.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nWrote {len(output_rows)} schools to {output_path}")

    # Stats
    with_display = sum(1 for r in output_rows if r["display"])
    with_snyder = sum(1 for r in output_rows if r["snyder"])
    with_d3hoops = sum(1 for r in output_rows if r["d3hoops"])
    print(f"  With display name: {with_display}")
    print(f"  With snyder name: {with_snyder}")
    print(f"  With d3hoops name: {with_d3hoops}")


if __name__ == "__main__":
    main()
