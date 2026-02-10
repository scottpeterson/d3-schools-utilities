"""Shared fixtures for d3-schools tests."""

import csv
import os
import tempfile
from pathlib import Path

import pytest

from d3_schools import SchoolRegistry


@pytest.fixture
def sample_data_dir(tmp_path):
    """Create a minimal data directory with sample school data."""
    # schools.csv
    schools_csv = tmp_path / "schools.csv"
    with open(schools_csv, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ncaa_id", "display", "massey", "d3hoops", "stats_ncaa",
                "ncaa_manual", "snyder", "conference", "region", "gender",
            ],
        )
        writer.writeheader()
        writer.writerows([
            {
                "ncaa_id": "286", "display": "Hope", "massey": "Hope",
                "d3hoops": "Hope", "stats_ncaa": "Hope", "ncaa_manual": "Hope College",
                "snyder": "Hope", "conference": "MIAA", "region": "7", "gender": "Coed",
            },
            {
                "ncaa_id": "1", "display": "Adrian", "massey": "Adrian",
                "d3hoops": "Adrian", "stats_ncaa": "Adrian", "ncaa_manual": "Adrian College",
                "snyder": "Adrian", "conference": "MIAA", "region": "7", "gender": "Coed",
            },
            {
                "ncaa_id": "12", "display": "Anderson", "massey": "Anderson IN",
                "d3hoops": "Anderson", "stats_ncaa": "Anderson",
                "ncaa_manual": "Anderson University", "snyder": "Anderson",
                "conference": "HCAC", "region": "7", "gender": "Coed",
            },
            {
                "ncaa_id": "715", "display": "Trinity (TX)", "massey": "Trinity TX",
                "d3hoops": "Trinity (Texas)", "stats_ncaa": "Trinity (TX)",
                "ncaa_manual": "Trinity University (Texas)", "snyder": "Trinity (Texas)",
                "conference": "SAA", "region": "6", "gender": "Coed",
            },
            {
                "ncaa_id": "716", "display": "Trinity (CT)", "massey": "Trinity CT",
                "d3hoops": "Trinity (Conn.)", "stats_ncaa": "Trinity (CT)",
                "ncaa_manual": "Trinity College (Connecticut)", "snyder": "Trinity (Conn.)",
                "conference": "NESCAC", "region": "1", "gender": "Coed",
            },
            {
                "ncaa_id": "225", "display": "Ferrum", "massey": "Ferrum",
                "d3hoops": "Ferrum", "stats_ncaa": "Ferrum",
                "ncaa_manual": "Ferrum College", "snyder": "",
                "conference": "", "region": "", "gender": "Coed",
            },
            {
                "ncaa_id": "379", "display": "WashU", "massey": "Washington StL",
                "d3hoops": "Washington U.", "stats_ncaa": "Wash. U.",
                "ncaa_manual": "Washington University in St. Louis", "snyder": "Washington U.",
                "conference": "UAA", "region": "8", "gender": "Coed",
            },
        ])

    # aliases.csv
    aliases_csv = tmp_path / "aliases.csv"
    with open(aliases_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["alias_value", "variant_type", "ncaa_id"])
        writer.writeheader()
        writer.writerows([
            {"alias_value": "wash. u.", "variant_type": "d3hoops", "ncaa_id": "379"},
            {"alias_value": "wash u", "variant_type": "d3hoops", "ncaa_id": "379"},
            {"alias_value": "washu", "variant_type": "d3hoops", "ncaa_id": "379"},
            {"alias_value": "trinity (conn.)", "variant_type": "d3hoops", "ncaa_id": "716"},
            {"alias_value": "trinity (texas)", "variant_type": "d3hoops", "ncaa_id": "715"},
            {"alias_value": "trin", "variant_type": "shortcode", "ncaa_id": "716"},
        ])

    # massey/wbb/2026.csv
    massey_dir = tmp_path / "massey" / "wbb"
    massey_dir.mkdir(parents=True)
    with open(massey_dir / "2026.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["massey_id", "ncaa_id"])
        writer.writeheader()
        writer.writerows([
            {"massey_id": "148", "ncaa_id": "286"},
            {"massey_id": "1", "ncaa_id": "1"},
            {"massey_id": "12", "ncaa_id": "12"},
            {"massey_id": "360", "ncaa_id": "715"},
            {"massey_id": "358", "ncaa_id": "716"},
            {"massey_id": "379", "ncaa_id": "379"},
        ])

    return tmp_path


@pytest.fixture
def registry(sample_data_dir):
    """A SchoolRegistry loaded from sample data."""
    return SchoolRegistry(data_dir=sample_data_dir)


@pytest.fixture
def real_registry():
    """A SchoolRegistry loaded from the actual bundled data."""
    return SchoolRegistry()
