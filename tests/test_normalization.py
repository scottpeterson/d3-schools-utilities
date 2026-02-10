"""Tests for name normalization."""

from d3_schools._normalize import normalize


class TestNormalize:
    def test_basic_lowercase(self):
        assert normalize("Hope") == "hope"

    def test_strip_whitespace(self):
        assert normalize("  Hope  ") == "hope"

    def test_underscores_to_spaces(self):
        assert normalize("Anderson_IN") == "anderson in"

    def test_dots_to_spaces(self):
        assert normalize("Alfred_St.") == "alfred st"  # dot -> space, trailing stripped

    def test_hyphens_to_spaces(self):
        assert normalize("Claremont-M-S") == "claremont m s"

    def test_parens_to_spaces(self):
        assert normalize("Trinity (CT)") == "trinity ct"

    def test_collapse_whitespace(self):
        assert normalize("St.  Mary's  (MD)") == "st mary's md"

    def test_empty_string(self):
        assert normalize("") == ""

    def test_already_normalized(self):
        assert normalize("hope") == "hope"

    def test_mixed_special_chars(self):
        assert normalize("Washington_&_Lee") == "washington & lee"

    def test_apostrophe_preserved(self):
        result = normalize("St. Mary's")
        assert "mary's" in result
