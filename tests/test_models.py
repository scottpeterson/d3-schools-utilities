"""Tests for School dataclass and related models."""

from d3_schools.models import CONFERENCES, Region, School


class TestSchool:
    def test_basic_creation(self):
        school = School(ncaa_id="286", variants={"display": "Hope"}, conference="MIAA", region=7)
        assert school.ncaa_id == "286"
        assert school.conference == "MIAA"
        assert school.region == 7

    def test_display_name_from_display_variant(self):
        school = School(ncaa_id="286", variants={"display": "Hope"})
        assert school.display_name == "Hope"
        assert school.name == "Hope"

    def test_display_name_fallback_to_massey(self):
        school = School(ncaa_id="12", variants={"massey": "Anderson_IN"})
        assert school.display_name == "Anderson IN"

    def test_display_name_fallback_to_id(self):
        school = School(ncaa_id="999")
        assert school.display_name == "School 999"

    def test_get_variant(self):
        school = School(ncaa_id="286", variants={"display": "Hope", "snyder": "Hope"})
        assert school.get("display") == "Hope"
        assert school.get("snyder") == "Hope"
        assert school.get("nonexistent") is None

    def test_is_active_with_region(self):
        school = School(ncaa_id="286", region=7, conference="MIAA")
        assert school.is_active is True

    def test_is_active_without_region(self):
        school = School(ncaa_id="225", region=0, conference="")
        assert school.is_active is False

    def test_frozen(self):
        school = School(ncaa_id="286")
        try:
            school.ncaa_id = "999"
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass

    def test_repr_active(self):
        school = School(ncaa_id="286", variants={"display": "Hope"}, region=7)
        assert "Hope" in repr(school)
        assert "inactive" not in repr(school)

    def test_repr_inactive(self):
        school = School(ncaa_id="225", variants={"display": "Ferrum"}, region=0)
        assert "Ferrum" in repr(school)
        assert "inactive" in repr(school)


class TestRegion:
    def test_region_values(self):
        assert Region.REGION_1 == 1
        assert Region.REGION_10 == 10

    def test_region_is_int(self):
        assert isinstance(Region.REGION_7, int)
        assert Region.REGION_7 == 7


class TestConferences:
    def test_known_conferences(self):
        assert "MIAA" in CONFERENCES
        assert "NESCAC" in CONFERENCES
        assert "UAA" in CONFERENCES

    def test_conferences_is_frozenset(self):
        assert isinstance(CONFERENCES, frozenset)
