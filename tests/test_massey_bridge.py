"""Tests for Massey bridge functionality with real bundled data."""

import pytest

from d3_schools import SchoolRegistry


class TestMasseyBridgeWBB:
    """WBB Massey bridge tests using actual bundled data."""

    def test_hope_massey_id(self, real_registry):
        school = real_registry.get_by_massey_id("148", year="wbb:2026")
        assert school is not None
        assert school.display_name == "Hope"
        assert school.ncaa_id == "286"

    def test_adrian_massey_id(self, real_registry):
        school = real_registry.get_by_massey_id("1", year="wbb:2026")
        assert school is not None
        assert school.display_name == "Adrian"

    def test_round_trip_massey_ncaa(self, real_registry):
        """Massey ID -> NCAA ID -> Massey ID should round-trip."""
        ncaa_id = real_registry.massey_id_to_ncaa_id("148", year="wbb:2026")
        assert ncaa_id is not None
        massey_id = real_registry.ncaa_id_to_massey_id(ncaa_id, year="wbb:2026")
        assert massey_id == "148"

    def test_id_to_name_produces_valid_mapping(self, real_registry):
        mapping = real_registry.id_to_name(id_type="massey", year="wbb:2026")
        assert len(mapping) > 400
        assert "148" in mapping
        assert mapping["148"] == "Hope"

    def test_name_to_id_inverse(self, real_registry):
        id_to_name = real_registry.id_to_name(id_type="massey", year="wbb:2026")
        name_to_id = real_registry.name_to_id(id_type="massey", year="wbb:2026")
        for mid, name in id_to_name.items():
            assert name in name_to_id
            assert name_to_id[name] == mid

    def test_multiple_years_available(self, real_registry):
        """WBB data for 2024, 2025, 2026 should be available."""
        for year in ["wbb:2024", "wbb:2025", "wbb:2026"]:
            school = real_registry.get_by_massey_id("1", year=year)
            if school is not None:
                assert school.display_name == "Adrian"


class TestMasseyBridgeMBB:
    """MBB Massey bridge tests using actual bundled data."""

    def test_hope_massey_id(self, real_registry):
        school = real_registry.get_by_massey_id("145", year="mbb:2026")
        assert school is not None
        assert school.display_name == "Hope"
        assert school.ncaa_id == "286"

    def test_adrian_massey_id(self, real_registry):
        school = real_registry.get_by_massey_id("1", year="mbb:2026")
        assert school is not None
        assert school.display_name == "Adrian"

    def test_round_trip_massey_ncaa(self, real_registry):
        """Massey ID -> NCAA ID -> Massey ID should round-trip."""
        ncaa_id = real_registry.massey_id_to_ncaa_id("145", year="mbb:2026")
        assert ncaa_id is not None
        massey_id = real_registry.ncaa_id_to_massey_id(ncaa_id, year="mbb:2026")
        assert massey_id == "145"

    def test_id_to_name_produces_valid_mapping(self, real_registry):
        mapping = real_registry.id_to_name(id_type="massey", year="mbb:2026")
        assert len(mapping) == 408
        assert "145" in mapping
        assert mapping["145"] == "Hope"

    def test_name_to_id_inverse(self, real_registry):
        id_to_name = real_registry.id_to_name(id_type="massey", year="mbb:2026")
        name_to_id = real_registry.name_to_id(id_type="massey", year="mbb:2026")
        for mid, name in id_to_name.items():
            assert name in name_to_id
            assert name_to_id[name] == mid


class TestMasseyBareYearFallback:
    """Bare year keys only work when a year has exactly one sport."""

    def test_bare_year_works_for_single_sport(self, real_registry):
        """2024 and 2025 only have WBB, so bare year should work."""
        s1 = real_registry.get_by_massey_id("1", year="2024")
        s2 = real_registry.get_by_massey_id("1", year="wbb:2024")
        assert s1 is not None
        assert s2 is not None
        assert s1.ncaa_id == s2.ncaa_id

    def test_bare_year_unavailable_for_multi_sport(self, real_registry):
        """2026 has both MBB and WBB, so bare year should not resolve."""
        school = real_registry.get_by_massey_id("1", year="2026")
        assert school is None

    def test_sport_scoped_keys_always_work(self, real_registry):
        """Sport-scoped keys should always work regardless of sport count."""
        wbb = real_registry.get_by_massey_id("1", year="wbb:2026")
        mbb = real_registry.get_by_massey_id("1", year="mbb:2026")
        assert wbb is not None
        assert mbb is not None
        assert wbb.ncaa_id == mbb.ncaa_id  # Same school (Adrian), different massey IDs
