#!/usr/bin/env python3
"""Generate d3_schools/data/massey/mbb/2026.csv from MBB_2026_Massey_Teams.csv.

MBB Massey IDs are sport-specific (different from WBB). This script reads
the MBB teams CSV and matches Team_Name -> ncaa_id via schools.csv massey column.
"""

import csv
from pathlib import Path


def _normalize(name: str) -> str:
    """Normalize a massey name for matching."""
    return name.lower().replace("_", " ").replace("-", " ").strip()


def load_massey_lookup(schools_path: Path) -> dict[str, str]:
    """Load schools.csv -> {normalized_massey_name: ncaa_id}."""
    massey_to_ncaa = {}
    with open(schools_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ncaa_id = row["ncaa_id"].strip()
            massey = row.get("massey", "").strip()
            if massey and massey != "-":
                massey_to_ncaa[_normalize(massey)] = ncaa_id
    return massey_to_ncaa


def main():
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "d3_schools" / "data"
    schools_path = data_dir / "schools.csv"
    mbb_csv = project_root / "MBB_2026_Massey_Teams.csv"
    output_path = data_dir / "massey" / "mbb" / "2026.csv"

    print(f"Loading schools.csv from {schools_path}...")
    massey_to_ncaa = load_massey_lookup(schools_path)
    print(f"  Built massey name lookup with {len(massey_to_ncaa)} entries")

    print(f"\nReading MBB teams from {mbb_csv}...")
    rows = []
    unmatched = []

    with open(mbb_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            massey_id = row["Team_ID"].strip()
            team_name = row["Team_Name"].strip()
            ncaa_id = massey_to_ncaa.get(_normalize(team_name))
            if ncaa_id:
                rows.append({"massey_id": massey_id, "ncaa_id": ncaa_id})
            else:
                unmatched.append((massey_id, team_name))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["massey_id", "ncaa_id"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults:")
    print(f"  Matched: {len(rows)}")
    print(f"  Unmatched: {len(unmatched)}")
    if unmatched:
        print(f"\nUnmatched teams:")
        for mid, name in unmatched:
            print(f"  {mid}: {name}")
    print(f"\nWrote to {output_path}")


if __name__ == "__main__":
    main()
