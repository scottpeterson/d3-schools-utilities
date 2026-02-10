#!/usr/bin/env python3
"""Validate referential integrity across all d3-schools data files."""

import csv
import sys
from pathlib import Path


def load_ncaa_ids(schools_path: Path) -> set[str]:
    """Load all ncaa_ids from schools.csv."""
    ids = set()
    with open(schools_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ncaa_id = row.get("ncaa_id", "").strip()
            if ncaa_id:
                ids.add(ncaa_id)
    return ids


def validate_schools(schools_path: Path) -> list[str]:
    """Validate schools.csv structure and content."""
    errors = []
    seen_ids = set()

    with open(schools_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required_cols = {"ncaa_id", "display", "conference", "region", "gender"}
        if reader.fieldnames:
            missing = required_cols - set(reader.fieldnames)
            if missing:
                errors.append(f"schools.csv missing columns: {missing}")

        for i, row in enumerate(reader, start=2):
            ncaa_id = row.get("ncaa_id", "").strip()
            if not ncaa_id:
                errors.append(f"schools.csv line {i}: empty ncaa_id")
                continue
            if ncaa_id in seen_ids:
                errors.append(f"schools.csv line {i}: duplicate ncaa_id '{ncaa_id}'")
            seen_ids.add(ncaa_id)

    return errors


def validate_aliases(aliases_path: Path, valid_ids: set[str]) -> list[str]:
    """Validate aliases.csv referential integrity."""
    errors = []
    if not aliases_path.exists():
        return ["aliases.csv not found"]

    with open(aliases_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            alias = row.get("alias_value", "").strip()
            ncaa_id = row.get("ncaa_id", "").strip()
            if not alias:
                errors.append(f"aliases.csv line {i}: empty alias_value")
            if not ncaa_id:
                errors.append(f"aliases.csv line {i}: empty ncaa_id")
            elif ncaa_id not in valid_ids:
                errors.append(f"aliases.csv line {i}: ncaa_id '{ncaa_id}' not in schools.csv")

    return errors


def validate_massey(massey_dir: Path, valid_ids: set[str]) -> list[str]:
    """Validate massey year files (supports flat and sport-scoped layouts)."""
    errors = []
    if not massey_dir.exists():
        return ["massey/ directory not found"]

    # Collect all CSV files: flat (massey/*.csv) and sport-scoped (massey/*/*.csv)
    all_csv_files = list(massey_dir.glob("*.csv")) + list(massey_dir.glob("*/*.csv"))

    for csv_file in sorted(all_csv_files):
        year = csv_file.stem
        seen_massey = set()
        seen_ncaa = set()

        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                massey_id = row.get("massey_id", "").strip()
                ncaa_id = row.get("ncaa_id", "").strip()

                if not massey_id:
                    errors.append(f"massey/{year}.csv line {i}: empty massey_id")
                if not ncaa_id:
                    errors.append(f"massey/{year}.csv line {i}: empty ncaa_id")
                elif ncaa_id not in valid_ids:
                    errors.append(
                        f"massey/{year}.csv line {i}: ncaa_id '{ncaa_id}' not in schools.csv"
                    )

                if massey_id in seen_massey:
                    errors.append(
                        f"massey/{year}.csv line {i}: duplicate massey_id '{massey_id}'"
                    )
                seen_massey.add(massey_id)

                if ncaa_id in seen_ncaa:
                    errors.append(
                        f"massey/{year}.csv line {i}: duplicate ncaa_id '{ncaa_id}'"
                    )
                seen_ncaa.add(ncaa_id)

    return errors


def main():
    data_dir = Path(__file__).parent.parent / "d3_schools" / "data"
    schools_path = data_dir / "schools.csv"

    if not schools_path.exists():
        print("ERROR: schools.csv not found. Run generate_schools_csv.py first.")
        sys.exit(1)

    all_errors = []

    print("Validating schools.csv...")
    errors = validate_schools(schools_path)
    all_errors.extend(errors)
    valid_ids = load_ncaa_ids(schools_path)
    print(f"  {len(valid_ids)} schools loaded, {len(errors)} errors")

    print("Validating aliases.csv...")
    errors = validate_aliases(data_dir / "aliases.csv", valid_ids)
    all_errors.extend(errors)
    print(f"  {len(errors)} errors")

    print("Validating massey year files...")
    errors = validate_massey(data_dir / "massey", valid_ids)
    all_errors.extend(errors)
    print(f"  {len(errors)} errors")

    if all_errors:
        print(f"\n{'='*60}")
        print(f"VALIDATION FAILED: {len(all_errors)} error(s)")
        print(f"{'='*60}")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"\n{'='*60}")
        print("VALIDATION PASSED: All data files are consistent")
        print(f"{'='*60}")
        print(f"  Schools: {len(valid_ids)}")
        aliases_path = data_dir / "aliases.csv"
        if aliases_path.exists():
            with open(aliases_path) as f:
                alias_count = sum(1 for _ in f) - 1
            print(f"  Aliases: {alias_count}")
        massey_dir = data_dir / "massey"
        if massey_dir.exists():
            all_csv = list(massey_dir.glob("*.csv")) + list(massey_dir.glob("*/*.csv"))
            for csv_file in sorted(all_csv):
                with open(csv_file) as f:
                    count = sum(1 for _ in f) - 1
                rel = csv_file.relative_to(massey_dir)
                print(f"  Massey {rel}: {count} mappings")


if __name__ == "__main__":
    main()
