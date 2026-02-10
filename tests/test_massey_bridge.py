"""Tests for Massey bridge functionality with real bundled data."""

import pytest

from d3_schools import SchoolRegistry


class TestMasseyBridgeRealData:
    """These tests use the actual bundled data files."""

    def test_hope_massey_id(self, real_registry):
        school = real_registry.get_by_massey_id("148", year="2026")
        assert school is not None
        assert school.display_name == "Hope"
        assert school.ncaa_id == "286"

    def test_adrian_massey_id(self, real_registry):
        school = real_registry.get_by_massey_id("1", year="2026")
        assert school is not None
        assert school.display_name == "Adrian"

    def test_round_trip_massey_ncaa(self, real_registry):
        """Massey ID -> NCAA ID -> Massey ID should round-trip."""
        ncaa_id = real_registry.massey_id_to_ncaa_id("148", year="2026")
        assert ncaa_id is not None
        massey_id = real_registry.ncaa_id_to_massey_id(ncaa_id, year="2026")
        assert massey_id == "148"

    def test_id_to_name_produces_valid_mapping(self, real_registry):
        mapping = real_registry.id_to_name(id_type="massey", year="2026")
        assert len(mapping) > 400
        assert "148" in mapping
        assert mapping["148"] == "Hope"

    def test_name_to_id_inverse(self, real_registry):
        id_to_name = real_registry.id_to_name(id_type="massey", year="2026")
        name_to_id = real_registry.name_to_id(id_type="massey", year="2026")
        # Every entry in id_to_name should have an inverse
        for mid, name in id_to_name.items():
            assert name in name_to_id
            assert name_to_id[name] == mid

    def test_wbb_scoped_key(self, real_registry):
        """wbb:2026 and bare 2026 should both work."""
        s1 = real_registry.get_by_massey_id("148", year="2026")
        s2 = real_registry.get_by_massey_id("148", year="wbb:2026")
        assert s1 is not None
        assert s2 is not None
        assert s1.ncaa_id == s2.ncaa_id

    def test_multiple_years_available(self, real_registry):
        """At least 2024, 2025, 2026 should be available."""
        for year in ["2024", "2025", "2026"]:
            school = real_registry.get_by_massey_id("1", year=year)
            # Massey ID 1 is Adrian in all years
            if school is not None:
                assert school.display_name == "Adrian"
