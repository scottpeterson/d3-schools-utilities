# d3-schools

Canonical D3 school identity clearinghouse. Pass in any name variant, get back whatever format you need.

Team identity data for D3 athletics is fragmented across Massey Ratings, D3hoops.com, NCAA stats, and Snyder efficiency ratings -- each source uses its own names for the same school. This package bundles canonical data for all ~440 NCAA Division III schools and provides O(1) lookups between any naming convention.

## Installation

```bash
pip install d3-schools
```

### From source

```bash
git clone https://github.com/scottpeterson/d3-schools.git
cd d3-schools
pip install -e .
```

### Requirements

- Python >= 3.9
- No runtime dependencies (stdlib only)

## Quick Start

```python
from d3_schools import SchoolRegistry

registry = SchoolRegistry()

# Find a school by any name from any source
school = registry.find("Hope")
school.display_name   # "Hope"
school.conference      # "MIAA"
school.region          # 7
school.is_active       # True

# Translate between naming formats
registry.resolve("Anderson_IN", output="display")   # "Anderson"
registry.resolve("Hope", output="ncaa_id")           # "286"
registry.resolve("wash. u.", output="display")        # "WashU"

# Massey ID bridge (sport-scoped -- WBB bundled)
registry.get_by_massey_id("148", year="2026")  # School(ncaa_id='286', name='Hope')
```

---

## Data Model

### `School` (frozen dataclass)

| Field | Type | Description |
|---|---|---|
| `ncaa_id` | `str` | Stable NCAA ID (primary key, persists across years) |
| `variants` | `Dict[str, str]` | Open namespace of name variants (see below) |
| `conference` | `str` | Conference abbreviation (e.g., `"MIAA"`). Empty if no longer D3. |
| `region` | `int` | NCAA region (1--10). `0` if no longer D3. |
| `gender` | `str` | `"Coed"`, `"Women"`, or `"Men"` |

**Properties:**

| Property | Type | Description |
|---|---|---|
| `display_name` | `str` | Human-readable name. Fallback: `display` -> `massey` cleanup -> `"School {ncaa_id}"` |
| `name` | `str` | Alias for `display_name` |
| `is_active` | `bool` | `True` if `region > 0` (currently in D3) |

**Methods:**

| Method | Returns | Description |
|---|---|---|
| `get(variant)` | `Optional[str]` | Get a specific name variant, or `None` |

### Bundled Variant Types

| Variant Key | Source | Example (Hope College) |
|---|---|---|
| `display` | Scott Peterson Display format | `"Hope"` |
| `massey` | Massey Ratings format | `"Hope"` |
| `d3hoops` | D3hoops.com format | `"Hope"` |
| `stats_ncaa` | stats.NCAA.org format | `"Hope"` |
| `ncaa_manual` | NCAA Championship Manual (full official) | `"Hope College"` |
| `snyder` | Matt Snyder Display format | `"Hope"` |

The variant namespace is **open** -- adding a column to `schools.csv` creates a new variant automatically (zero code changes).

### `Region` (IntEnum)

```python
from d3_schools import Region

Region.REGION_1   # 1
Region.REGION_10  # 10
```

### `CONFERENCES` (frozenset)

```python
from d3_schools import CONFERENCES

"MIAA" in CONFERENCES  # True
```

All ~42 known D3 conferences as of the 2025--26 season.

### Inactive Schools

Schools with `region=0` and empty `conference` are no longer NCAA D3 members (e.g., Ferrum, Birmingham-Southern, Cazenovia). They remain in the registry for historical lookups.

```python
school = registry.find("Ferrum")
school.is_active   # False
school.region      # 0
school.conference  # ""
```

---

## API Reference

### `SchoolRegistry`

#### Constructor

```python
SchoolRegistry(data_dir: Optional[Path] = None)
```

Loads bundled CSV data and builds O(1) indexes. Pass `data_dir` to use custom data files instead of the bundled defaults.

---

#### Core Lookups

```python
registry.get(ncaa_id: str) -> Optional[School]
```
Look up a school by NCAA ID (primary key).

```python
registry.get_by_massey_id(massey_id: str, year: str) -> Optional[School]
```
Look up a school by Massey ID for a given year. Massey IDs are sport+gender specific (WBB bundled). Accepts both `"2026"` and `"wbb:2026"` as the year key.

---

#### Find (any name in -> School out)

```python
registry.find(name: str, source: str = "") -> Optional[School]
```
Find a school by any name variant. Returns `None` if the name is ambiguous (matches multiple schools) or not found. Pass `source` to restrict the search to a single variant namespace.

```python
registry.find("Hope")                                 # -> School
registry.find("Trinity (TX)")                          # -> School
registry.find("Trinity (Texas)", source="d3hoops")     # -> School (scoped)
```

```python
registry.find_all(name: str) -> List[School]
```
Find all schools matching a name variant. Useful for ambiguous names like "Trinity".

```python
registry.find_all("Trinity (CT)")  # -> [School(...)]
```

---

#### Resolve (any name in -> desired format out)

```python
registry.resolve(name: str, output: str = "display", source: str = "") -> Optional[str]
```
Resolve any name variant to a desired output format. Combines `find()` + `get()` in one call.

| Parameter | Description |
|---|---|
| `name` | Input name (any variant from any source) |
| `output` | Desired output format: `"display"`, `"d3hoops"`, `"snyder"`, `"ncaa_id"`, `"ncaa_manual"`, etc. |
| `source` | Optional: restrict input matching to one variant namespace |

```python
registry.resolve("Anderson_IN", output="display")         # "Anderson"
registry.resolve("Hope", output="ncaa_id")                 # "286"
registry.resolve("Hope", output="ncaa_manual")             # "Hope College"
registry.resolve("wash. u.", output="display")              # "WashU"
registry.resolve("Trinity (Texas)", source="d3hoops",
                 output="ncaa_id")                          # "715"
```

---

#### Massey ID Bridge

Massey IDs are year-specific and sport+gender-specific. The bundled data includes WBB (Women's Basketball) mappings for 2024, 2025, and 2026.

```python
registry.massey_id_to_ncaa_id(massey_id: str, year: str) -> Optional[str]
registry.ncaa_id_to_massey_id(ncaa_id: str, year: str) -> Optional[str]
```

```python
registry.massey_id_to_ncaa_id("148", year="2026")   # "286"
registry.ncaa_id_to_massey_id("286", year="2026")   # "148"
```

Both `"2026"` and `"wbb:2026"` are accepted as year keys.

---

#### Backward-Compatible Dictionaries

For migrating existing code that expects `{id: name}` or `{name: id}` dicts:

```python
registry.id_to_name(id_type: str = "massey", year: str = "", variant: str = "display") -> Dict[str, str]
registry.name_to_id(id_type: str = "massey", year: str = "", variant: str = "display") -> Dict[str, str]
```

| `id_type` | Requires `year` | Result |
|---|---|---|
| `"massey"` | Yes | `{"148": "Hope", "1": "Adrian", ...}` |
| `"ncaa"` | No | `{"286": "Hope", "1": "Adrian", ...}` |

```python
id_map = registry.id_to_name(id_type="massey", year="2026")
id_map["148"]  # "Hope"

name_map = registry.name_to_id(id_type="massey", year="2026")
name_map["Hope"]  # "148"
```

---

#### Metadata Queries

```python
registry.all_schools() -> List[School]
registry.schools_in_conference(conference: str) -> List[School]
registry.variant_types -> List[str]      # ["display", "massey", "d3hoops", ...]
```

```python
len(registry)       # 440
"286" in registry   # True
registry["286"]     # School(ncaa_id='286', name='Hope')
```

---

#### Overlay (custom/private variants)

Add custom name variants without modifying the bundled data:

```python
registry.load_overlay(path: str) -> None
```

The overlay CSV needs an `ncaa_id` column plus any custom columns:

```csv
ncaa_id,nickname,broadcast_name
286,Flying Dutch,Hope (MI)
1,Bulldogs,Adrian (MI)
```

```python
registry.load_overlay("my_custom_names.csv")
registry.find("Flying Dutch")              # -> School(ncaa_id='286')
registry.resolve("Hope", output="nickname") # "Flying Dutch"
```

---

## Exceptions

| Exception | Raised When |
|---|---|
| `SchoolNotFoundError` | `registry["999"]` -- NCAA ID not found |
| `AmbiguousMatchError` | (Available for consumer use; `find()` returns `None` instead) |
| `DataLoadingError` | Bundled CSV files are missing or malformed |

All inherit from `D3SchoolsError`.

```python
from d3_schools import SchoolNotFoundError

try:
    school = registry["999"]
except SchoolNotFoundError as e:
    print(e.query)  # "999"
```

---

## Bundled Data

```
d3_schools/data/
  schools.csv              # 440 schools, 6 variant columns + metadata
  aliases.csv              # 144 many-to-one aliases (d3hoops + shortcodes)
  massey/
    wbb/                   # Women's Basketball (sport+gender scoped)
      2024.csv             # 423 Massey ID -> NCAA ID mappings
      2025.csv             # 417 mappings
      2026.csv             # 413 mappings
```

### `schools.csv` format

```csv
ncaa_id,display,massey,d3hoops,stats_ncaa,ncaa_manual,snyder,conference,region,gender
286,Hope,Hope,Hope,Hope,Hope College,Hope,MIAA,7,Coed
```

Reserved metadata columns (`ncaa_id`, `conference`, `region`, `gender`) are not treated as name variants. **Everything else is auto-discovered as a variant type** from the CSV headers at load time.

### `aliases.csv` format

```csv
alias_value,variant_type,ncaa_id
wash. u.,d3hoops,379
trin,shortcode,716
```

### `massey/wbb/{year}.csv` format

```csv
massey_id,ncaa_id
148,286
1,1
```

---

## Adding New Variant Types

1. Add a column to `schools.csv` (e.g., `jacob_schauer`)
2. Fill in names for each school
3. `SchoolRegistry` auto-discovers it -- no code changes needed
4. All API methods work with it immediately:

```python
registry.resolve("Hope", output="jacob_schauer")
registry.find("Andy", source="jacob_schauer")
```

---

## Data Update Workflow

When school data changes (new season, conference realignment, etc.):

1. Update `schools.csv` (add/modify rows)
2. Add `massey/wbb/{year}.csv` for new season
3. Bump version in `pyproject.toml`
4. `pip install --upgrade d3-schools`

### Regenerating data from d3-bball-npi sources

```bash
python scripts/generate_schools_csv.py /path/to/d3-bball-npi
python scripts/generate_aliases_csv.py
python scripts/generate_massey_year.py /path/to/d3-bball-npi
python scripts/validate_data.py
```

---

## Development

```bash
git clone https://github.com/scottpeterson/d3-schools.git
cd d3-schools
pip install -e ".[dev]"
pytest tests/ -v              # run tests (78 tests)
```

### Running Tests

```bash
pytest tests/ -v                    # all tests
pytest tests/test_registry.py -v    # registry tests only
pytest tests/ --cov=d3_schools      # with coverage
```
