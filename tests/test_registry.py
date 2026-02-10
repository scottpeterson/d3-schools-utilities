"""Tests for SchoolRegistry."""

import csv
from pathlib import Path

import pytest

from d3_schools import SchoolNotFoundError, SchoolRegistry
from d3_schools.models import School


class TestRegistryBasics:
    def test_len(self, registry):
        assert len(registry) == 7

    def test_contains(self, registry):
        assert "286" in registry
        assert "999" not in registry

    def test_getitem(self, registry):
        school = registry["286"]
        assert school.ncaa_id == "286"
        assert school.display_name == "Hope"

    def test_getitem_missing_raises(self, registry):
        with pytest.raises(SchoolNotFoundError):
            registry["999"]

    def test_iter(self, registry):
        schools = list(registry)
        assert len(schools) == 7
        assert all(isinstance(s, School) for s in schools)

    def test_repr(self, registry):
        assert "7 schools" in repr(registry)

    def test_variant_types(self, registry):
        vtypes = registry.variant_types
        assert "display" in vtypes
        assert "massey" in vtypes
        assert "d3hoops" in vtypes
        assert "snyder" in vtypes


class TestGet:
    def test_get_by_ncaa_id(self, registry):
        school = registry.get("286")
        assert school is not None
        assert school.display_name == "Hope"

    def test_get_missing(self, registry):
        assert registry.get("999") is None

    def test_get_strips_whitespace(self, registry):
        school = registry.get(" 286 ")
        assert school is not None


class TestGetByMasseyId:
    def test_basic_lookup(self, registry):
        school = registry.get_by_massey_id("148", year="2026")
        assert school is not None
        assert school.display_name == "Hope"

    def test_wbb_scoped_lookup(self, registry):
        school = registry.get_by_massey_id("148", year="wbb:2026")
        assert school is not None
        assert school.display_name == "Hope"

    def test_missing_massey_id(self, registry):
        assert registry.get_by_massey_id("999", year="2026") is None

    def test_missing_year(self, registry):
        assert registry.get_by_massey_id("148", year="2099") is None


class TestFind:
    def test_find_by_display_name(self, registry):
        school = registry.find("Hope")
        assert school is not None
        assert school.ncaa_id == "286"

    def test_find_by_ncaa_id(self, registry):
        school = registry.find("286")
        assert school is not None
        assert school.display_name == "Hope"

    def test_find_by_massey_name(self, registry):
        school = registry.find("Anderson IN")
        assert school is not None
        assert school.display_name == "Anderson"

    def test_find_case_insensitive(self, registry):
        school = registry.find("hope")
        assert school is not None
        assert school.ncaa_id == "286"

    def test_find_unambiguous_variant(self, registry):
        # "Trinity (TX)" has a unique normalized form
        school = registry.find("Trinity (TX)")
        assert school is not None
        assert school.ncaa_id == "715"

    def test_find_scoped_resolves_ambiguity(self, registry):
        school = registry.find("Trinity (Texas)", source="d3hoops")
        assert school is not None
        assert school.ncaa_id == "715"

    def test_find_missing(self, registry):
        assert registry.find("Nonexistent University") is None

    def test_find_all_specific(self, registry):
        # "Trinity (TX)" matches exactly one school
        schools = registry.find_all("Trinity (TX)")
        assert len(schools) == 1
        assert schools[0].ncaa_id == "715"

    def test_find_all_empty(self, registry):
        assert registry.find_all("Nonexistent") == []


class TestResolve:
    def test_resolve_to_display(self, registry):
        result = registry.resolve("Anderson IN", output="display")
        assert result == "Anderson"

    def test_resolve_to_ncaa_id(self, registry):
        result = registry.resolve("Hope", output="ncaa_id")
        assert result == "286"

    def test_resolve_to_snyder(self, registry):
        result = registry.resolve("Hope", output="snyder")
        assert result == "Hope"

    def test_resolve_with_source(self, registry):
        result = registry.resolve("Trinity (Texas)", source="d3hoops", output="ncaa_id")
        assert result == "715"

    def test_resolve_not_found(self, registry):
        result = registry.resolve("Nonexistent")
        assert result is None

    def test_resolve_alias(self, registry):
        result = registry.resolve("wash u", output="display")
        assert result == "WashU"


class TestAliases:
    def test_d3hoops_alias(self, registry):
        school = registry.find("wash. u.")
        assert school is not None
        assert school.ncaa_id == "379"

    def test_shortcode_alias(self, registry):
        school = registry.find("trin")
        assert school is not None
        assert school.ncaa_id == "716"

    def test_alias_find_all(self, registry):
        # "trinity (conn.)" is an alias for Trinity CT
        school = registry.find("trinity (conn.)")
        assert school is not None
        assert school.ncaa_id == "716"


class TestMasseyBridge:
    def test_massey_to_ncaa(self, registry):
        result = registry.massey_id_to_ncaa_id("148", year="2026")
        assert result == "286"

    def test_ncaa_to_massey(self, registry):
        result = registry.ncaa_id_to_massey_id("286", year="2026")
        assert result == "148"

    def test_massey_to_ncaa_missing(self, registry):
        assert registry.massey_id_to_ncaa_id("999", year="2026") is None

    def test_ncaa_to_massey_missing(self, registry):
        assert registry.ncaa_id_to_massey_id("999", year="2026") is None


class TestBackwardCompat:
    def test_id_to_name_massey(self, registry):
        mapping = registry.id_to_name(id_type="massey", year="2026")
        assert mapping["148"] == "Hope"
        assert mapping["1"] == "Adrian"

    def test_name_to_id_massey(self, registry):
        mapping = registry.name_to_id(id_type="massey", year="2026")
        assert mapping["Hope"] == "148"

    def test_id_to_name_ncaa(self, registry):
        mapping = registry.id_to_name(id_type="ncaa")
        assert mapping["286"] == "Hope"
        assert mapping["1"] == "Adrian"

    def test_id_to_name_with_variant(self, registry):
        mapping = registry.id_to_name(id_type="ncaa", variant="snyder")
        assert mapping["286"] == "Hope"


class TestMetadata:
    def test_all_schools(self, registry):
        schools = registry.all_schools()
        assert len(schools) == 7

    def test_schools_in_conference(self, registry):
        miaa = registry.schools_in_conference("MIAA")
        assert len(miaa) == 2
        names = {s.display_name for s in miaa}
        assert "Hope" in names
        assert "Adrian" in names

    def test_schools_in_conference_case_insensitive(self, registry):
        miaa = registry.schools_in_conference("miaa")
        assert len(miaa) == 2

    def test_inactive_school(self, registry):
        ferrum = registry.find("Ferrum")
        assert ferrum is not None
        assert ferrum.is_active is False
        assert ferrum.region == 0
        assert ferrum.conference == ""


class TestOverlay:
    def test_overlay_adds_variant(self, registry, tmp_path):
        overlay_path = tmp_path / "overlay.csv"
        with open(overlay_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ncaa_id", "custom_name"])
            writer.writeheader()
            writer.writerow({"ncaa_id": "286", "custom_name": "The Flying Dutch"})

        registry.load_overlay(str(overlay_path))

        school = registry.get("286")
        assert school.get("custom_name") == "The Flying Dutch"
        # Original variants preserved
        assert school.get("display") == "Hope"

    def test_overlay_findable(self, registry, tmp_path):
        overlay_path = tmp_path / "overlay.csv"
        with open(overlay_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ncaa_id", "nickname"])
            writer.writeheader()
            writer.writerow({"ncaa_id": "286", "nickname": "Flying Dutch"})

        registry.load_overlay(str(overlay_path))
        school = registry.find("Flying Dutch")
        assert school is not None
        assert school.ncaa_id == "286"
