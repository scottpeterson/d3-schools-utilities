#!/usr/bin/env python3
"""Generate d3_schools/data/massey/wbb/{year}.csv from teams.txt files.

Massey IDs are sport+gender specific. The teams.txt files in d3-bball-npi
are for Women's Basketball (WBB), so we place them under massey/wbb/.

teams.txt comes in two formats:
  - With headers: team_id,massey_name
  - Without headers: "   1, Adrian" (space-separated, no header)

We detect which format and parse accordingly, then match massey_name -> ncaa_id
via schools.csv massey column (normalized).
"""

import csv
import sys
from pathlib import Path


def _normalize(name: str) -> str:
    """Normalize a massey name for matching."""
    return name.lower().replace("_", " ").replace("-", " ").strip()


def load_schools_csv(path: Path) -> dict[str, str]:
    """Load schools.csv -> {normalized_massey_name: ncaa_id}."""
    massey_to_ncaa = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ncaa_id = row["ncaa_id"].strip()
            massey = row.get("massey", "").strip()
            if massey and massey != "-":
                massey_to_ncaa[_normalize(massey)] = ncaa_id
    return massey_to_ncaa


def parse_teams_txt(teams_txt: Path) -> list[tuple[str, str]]:
    """Parse teams.txt, handling both with-header and without-header formats.

    Returns list of (massey_id, massey_name) tuples.
    """
    entries = []
    with open(teams_txt, "r", encoding="utf-8-sig") as f:
        first_line = f.readline().strip()
        f.seek(0)

        if first_line.startswith("team_id"):
            # Has headers — use DictReader
            reader = csv.DictReader(f)
            for row in reader:
                mid = row.get("team_id", "").strip()
                mname = row.get("massey_name", "").strip()
                if mid and mname:
                    entries.append((mid, mname))
        else:
            # No headers — parse "  id, name" format
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",", 1)
                if len(parts) == 2:
                    mid = parts[0].strip()
                    mname = parts[1].strip()
                    if mid and mname:
                        entries.append((mid, mname))
    return entries


def generate_for_year(
    teams_txt: Path, massey_to_ncaa: dict, output_path: Path
) -> tuple[int, int]:
    """Generate massey/wbb/{year}.csv from a teams.txt file."""
    entries = parse_teams_txt(teams_txt)
    rows = []
    unmatched = []

    seen_ids = set()
    for massey_id, massey_name in entries:
        if massey_id in seen_ids:
            continue  # Skip duplicate massey IDs in source
        seen_ids.add(massey_id)
        ncaa_id = massey_to_ncaa.get(_normalize(massey_name))
        if ncaa_id:
            rows.append({"massey_id": massey_id, "ncaa_id": ncaa_id})
        else:
            unmatched.append((massey_id, massey_name))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["massey_id", "ncaa_id"])
        writer.writeheader()
        writer.writerows(rows)

    return len(rows), len(unmatched)


def main():
    npi_root = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path.home() / "projects" / "d3-bball-npi"
    )
    data_dir = Path(__file__).parent.parent / "d3_schools" / "data"
    schools_path = data_dir / "schools.csv"

    if not schools_path.exists():
        print("ERROR: Run generate_schools_csv.py first to create schools.csv")
        sys.exit(1)

    print(f"Loading schools.csv from {schools_path}...")
    massey_to_ncaa = load_schools_csv(schools_path)
    print(f"  Built massey name lookup with {len(massey_to_ncaa)} entries")

    data_root = npi_root / "myapp" / "data"
    years_found = []
    for year_dir in sorted(data_root.iterdir()):
        teams_txt = year_dir / "teams.txt"
        if year_dir.is_dir() and teams_txt.exists():
            years_found.append((year_dir.name, teams_txt))

    if not years_found:
        print("ERROR: No teams.txt files found")
        sys.exit(1)

    print(f"\nFound {len(years_found)} year(s): {', '.join(y for y, _ in years_found)}")

    for year, teams_txt in years_found:
        output_path = data_dir / "massey" / "wbb" / f"{year}.csv"
        matched, unmatched = generate_for_year(teams_txt, massey_to_ncaa, output_path)
        status = f"  {year}: {matched} matched"
        if unmatched:
            status += f", {unmatched} unmatched"
        print(status)
        print(f"    Wrote to {output_path}")


if __name__ == "__main__":
    main()
