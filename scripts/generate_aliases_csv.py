#!/usr/bin/env python3
"""Generate d3_schools/data/aliases.csv from TEAM_NAME_ALIASES and MANUAL_ALIASES.

Sources:
  1. TEAM_NAME_ALIASES in myapp/d3hoops_games_scraper.py — d3hoops aliases
  2. MANUAL_ALIASES in myapp/score_scrapers/team_name_resolver.py — shortcode aliases

Each alias maps an alternate name to a display name. We then resolve the display
name to an ncaa_id via the schools.csv we already generated.
"""

import csv
import sys
from pathlib import Path


# ── Hardcoded alias dictionaries (extracted from source) ──────────────────

# From myapp/d3hoops_games_scraper.py TEAM_NAME_ALIASES
# Maps: d3hoops alternate name -> d3hoops canonical name (which matches display or d3hoops column)
D3HOOPS_ALIASES = {
    'new york university': 'nyu',
    'suny geneseo': 'geneseo st.',
    'rpi': 'rensselaer',
    'vermont state castleton': 'castleton',
    'vermont state lyndon': 'nvu-lyndon',
    'vermont state johnson': 'nvu-johnson',
    'alfred state': 'alfred st.',
    'regis (mass.)': 'regis',
    'penn': 'pennsylvania',
    'wheaton (mass.)': 'wheaton (ma)',
    'wheaton (ill.)': 'wheaton (il)',
    "st. mary's (md.)": "st. mary's (md)",
    "st. mary's (ind.)": "st. mary's (in)",
    'gwynedd mercy': 'gwynedd-mercy',
    'north central (minn.)': 'north central (mn)',
    'north central (ill.)': 'north central (il)',
    'university of dallas': 'dallas univ',
    'penn state-altoona': 'psu-altoona',
    'penn state-berks': 'psu-berks',
    'westminster (mo.)': 'westminster (mo)',
    'st. joseph (conn.)': 'st. joseph (ct)',
    'worcester state': 'worcester st.',
    'lebanon valley': 'lebanon val',
    'franciscan (ohio)': 'franciscan',
    'suny-canton': 'suny canton',
    'william peace': 'peace',
    'randolph': 'randolph col',
    'centenary (la.)': 'centenary (la)',
    'maranatha baptist': 'maranatha bap',
    'bethany lutheran': 'bethany luth',
    'suny-purchase': 'suny purchase',
    'central': 'central (ia)',
    'case western reserve': 'case western',
    'university of the ozarks': 'univ ozarks',
    'illinois college': 'illinois col',
    'minnesota-morris': 'minn-morris',
    'pacific lutheran': 'pac lutheran',
    'union': 'union (ny)',
    'keene state': 'keene st.',
    'mount st. mary': 'mt. st. mary',
    'montclair state': 'montclair st.',
    'washington and lee': 'washington & lee',
    'mount holyoke': 'mt. holyoke',
    'franklin and marshall': 'franklin & marshall',
    'mount union': 'mt. union',
    'suny-cobleskill': 'suny cobleskill',
    "st. joseph's (maine)": "st. joseph's (me)",
    'thomas': 'thomas (me)',
    'lewis and clark': 'lewis & clark',
    'wesleyan (ga.)': 'wesleyan (ga)',
    'westminster (pa.)': 'westminster (pa)',
    'plymouth state': 'plymouth st.',
    'bethany': 'bethany (wv)',
    'bridgewater state': 'bridgewater st.',
    'brooklyn': 'brooklyn college',
    'ccny': 'city college (ny)',
    'concordia (wis.)': 'concordia (wi)',
    'concordia (texas)': 'concordia (tx)',
    'concordia-moorhead': 'concordia moorhead',
    'delaware valley': 'delaware val',
    'eastern': 'eastern univ',
    'fitchburg state': 'fitchburg st.',
    'framingham state': 'framingham st.',
    'lancaster bible': 'lancaster bib',
    'maine maritime': 'maine-maritime',
    'n.c. wesleyan': 'nc wesleyan',
    'pratt': 'pratt inst',
    'suny-old westbury': 'old westbury',
    'salem state': 'salem st.',
    'wentworth': 'wentworth tech',
    'york (n.y.)': 'york (ny)',
    'johnson and wales': 'johnson & wales (ri)',
    'centenary (n.j.)': 'centenary (nj)',
    'trinity (d.c.)': 'trinity (dc)',
    'farmingdale state': 'farmingdale',
    'notre dame (md.)': 'notre dame (md)',
    'simpson': 'simpson (ia)',
    'austin': 'austin college',
    'washington u.': 'washu',
    'brockport': 'brockport st.',
    'buffalo state': 'buffalo st.',
    "st. joseph's (l.i.)": "st. joseph's (li)",
    'fdu-florham': 'fdu florham',
    'mount aloysius': 'mt. aloysius',
    'plattsburgh state': 'plattsburgh st.',
    'mount st. joseph': 'mt. st. joseph',
    'washington and jefferson': 'washington & jefferson',
    'oswego state': 'oswego st.',
    "st. joseph's (bklyn.)": "st. joseph's (ny)",
    'york (pa.)': 'york (pa)',
    'westfield state': 'westfield st.',
    'st. thomas (texas)': 'st. thomas (tx)',
    'trinity (conn.)': 'trinity (ct)',
    'salem': 'salem (nc)',
    'hunter': 'hunter',
    'uw-la crosse': 'uw-la crosse',
    'morrisville state': 'morrisville st.',
    'messiah': 'messiah',
    'massachusetts college': 'ma col lib arts',
    'western connecticut': 'western connecticut',
    'trinity (texas)': 'trinity (tx)',
    'northwestern (minn.)': 'northwestern (mn)',
    'christopher newport': 'christopher newport',
    'wesleyan': 'wesleyan (ct)',
    "st. mary's (minn.)": "st. mary's (mn)",
    'sage': 'sage',
    'penn state-harrisburg': 'psu-harrisburg',
    'mount st. vincent': 'mt. st. vincent',
    'illinois wesleyan': 'illinois wesleyan',
    'carleton': 'carleton',
    'bridgewater (va.)': 'bridgewater (va)',
    'suny cortland': 'cortland st.',
    'oneonta': 'oneonta st.',
    'suny-oneonta': 'oneonta st.',
    'suny potsdam': 'potsdam st.',
    'fredonia': 'fredonia st.',
    'suny fredonia': 'fredonia st.',
    'new paltz': 'new paltz st.',
    'suny new paltz': 'new paltz st.',
    'gordon': 'gordon',
    'endicott': 'endicott',
    'roger williams': 'roger williams',
    'emerson': 'emerson',
    'lasell': 'lasell',
    'nichols': 'nichols',
    'rivier': 'rivier',
    'curry': 'curry',
    'anna maria': 'anna maria',
    'southern maine': 'southern maine',
    'eastern connecticut': 'eastern connecticut',
    'southern vermont': 'southern vermont',
    'daniel webster': 'daniel webster',
    'colby-sawyer': 'colby-sawyer',
    'st. joseph (maine)': "st. joseph's (me)",
    'umass boston': 'mass-boston',
    'umass dartmouth': 'mass-dartmouth',
    'uw-stevens point': 'uw-stevens point',
    'uw-eau claire': 'uw-eau claire',
    'uw-whitewater': 'uw-whitewater',
    'uw-oshkosh': 'uw-oshkosh',
    'uw-river falls': 'uw-river falls',
    'uw-stout': 'uw-stout',
    'uw-platteville': 'uw-platteville',
    'uw-superior': 'uw-superior',
    'st. norbert': 'st. norbert',
    'lake forest': 'lake forest',
    'lawrence': 'lawrence',
    'grinnell': 'grinnell',
    'knox': 'knox',
    'monmouth (ill.)': 'monmouth (il)',
    'ripon': 'ripon',
    'cornell college': 'cornell (ia)',
    'coe': 'coe',
    'luther': 'luther',
    'wartburg': 'wartburg',
    'loras': 'loras',
    'dubuque': 'dubuque',
    'nebraska wesleyan': 'nebraska wesleyan',
    'gustavus adolphus': 'gustavus adolphus',
    'macalester': 'macalester',
    'st. olaf': 'st. olaf',
    'st. catherine': 'st. catherine',
    'hamline': 'hamline',
    'concordia (minn.)': 'concordia moorhead',
    'pacific (ore.)': 'pacific (or)',
    'willamette': 'willamette',
    'puget sound': 'puget sound',
    'whitworth': 'whitworth',
    'linfield': 'linfield',
    'george fox': 'george fox',
    'whitman': 'whitman',
    'pomona-pitzer': 'pomona-pitzer',
    'claremont-mudd-scripps': 'claremont-m-s',
    'chapman': 'chapman',
    'occidental': 'occidental',
    'redlands': 'redlands',
    'la verne': 'la verne',
    'whittier': 'whittier',
    'colorado college': 'colorado col',
    'rhodes': 'rhodes',
    'sewanee': 'sewanee',
    'centre': 'centre',
    'birmingham-southern': 'birmingham-so',
    'millsaps': 'millsaps',
    'oglethorpe': 'oglethorpe',
    'hendrix': 'hendrix',
    'southwestern (texas)': 'southwestern (tx)',
    'texas lutheran': 'texas lutheran',
    'schreiner': 'schreiner',
    'hardin-simmons': 'hardin-simmons',
    'howard payne': 'howard payne',
    'mary hardin-baylor': 'mary hardin-baylor',
    "le tourneau": 'letourneau',
    'east texas baptist': 'east texas baptist',
    'sul ross state': 'sul ross st.',
    'louisiana college': 'louisiana col',
    'emory': 'emory',
    'carnegie mellon': 'carnegie mellon',
    'rochester': 'rochester',
    'university of chicago': 'chicago',
    'nyu': 'nyu',
    'johns hopkins': 'johns hopkins',
    'brandeis': 'brandeis',
    'wash. u.': 'washu',
    'wash u': 'washu',
    'wash. u': 'washu',
    'rochester (n.y.)': 'rochester',
    'st. thomas (texas)': 'st. thomas (tx)',
    'centenary (la.)': 'centenary (la)',
    'muw': 'miss univ women',
    'maryville (tenn.)': 'maryville',
    'fdu': 'fdu florham',
}

# From myapp/score_scrapers/team_name_resolver.py MANUAL_ALIASES
MANUAL_ALIASES = {
    "oc": "Oglethorpe",
    "rpi": "Rensselaer",
    "plat": "Plattsburgh St.",
    "canton": "SUNY Canton",
    "gen": "SUNY Geneseo",
    "npwbb": "SUNY New Paltz",
    "lin": "Linfield",
    "midd": "Middlebury",
    "trin": "Trinity (CT)",
    "bow": "Bowdoin",
    "naz": "Nazareth",
    "trinity univ": "Trinity (TX)",
    "trinity univ.": "Trinity (TX)",
    "trinity university": "Trinity (TX)",
}


def _normalize(s: str) -> str:
    """Normalize a name for matching: lowercase, underscores to spaces, strip periods."""
    return s.lower().replace("_", " ").replace(".", "").strip()


def load_schools_csv(path: Path) -> dict[str, str]:
    """Load schools.csv and build a comprehensive name -> ncaa_id lookup.

    Indexes every variant column value (display, massey, d3hoops, etc.)
    under both exact lowercase and normalized forms.
    """
    name_to_ncaa = {}  # lowercase/normalized name -> ncaa_id
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ncaa_id = row["ncaa_id"].strip()
            for col in ["display", "massey", "d3hoops", "stats_ncaa", "ncaa_manual", "snyder"]:
                val = row.get(col, "").strip()
                if val and val != "-":
                    # Index both exact lowercase and normalized
                    name_to_ncaa[val.lower()] = ncaa_id
                    name_to_ncaa[_normalize(val)] = ncaa_id
    return name_to_ncaa


def main():
    data_dir = Path(__file__).parent.parent / "d3_schools" / "data"
    schools_path = data_dir / "schools.csv"

    if not schools_path.exists():
        print("ERROR: Run generate_schools_csv.py first to create schools.csv")
        sys.exit(1)

    print(f"Loading schools.csv from {schools_path}...")
    name_to_ncaa = load_schools_csv(schools_path)
    print(f"  Built lookup with {len(name_to_ncaa)} name entries")

    aliases = []
    unresolved = []

    def resolve_name(name: str) -> str | None:
        """Try to resolve a name to an ncaa_id using multiple strategies."""
        # Exact lowercase
        ncaa_id = name_to_ncaa.get(name.lower())
        if ncaa_id:
            return ncaa_id
        # Normalized (no periods, underscores to spaces)
        ncaa_id = name_to_ncaa.get(_normalize(name))
        if ncaa_id:
            return ncaa_id
        return None

    # Process D3HOOPS_ALIASES
    # These map d3hoops_alternate -> d3hoops_canonical
    for alias_name, canonical_name in D3HOOPS_ALIASES.items():
        ncaa_id = resolve_name(canonical_name)
        if ncaa_id:
            if alias_name.lower() != canonical_name.lower():
                aliases.append({
                    "alias_value": alias_name,
                    "variant_type": "d3hoops",
                    "ncaa_id": ncaa_id,
                })
        else:
            unresolved.append(("d3hoops", alias_name, canonical_name))

    # Process MANUAL_ALIASES
    # These map shortcode -> display_name
    for alias_name, display_name in MANUAL_ALIASES.items():
        ncaa_id = resolve_name(display_name)
        if ncaa_id:
            aliases.append({
                "alias_value": alias_name,
                "variant_type": "shortcode",
                "ncaa_id": ncaa_id,
            })
        else:
            unresolved.append(("shortcode", alias_name, display_name))

    # Manual overrides for aliases whose targets use names not in any CSV column.
    # These are d3hoops scraper internal names that don't match the master data.
    manual_overrides = {
        # d3hoops alias -> ncaa_id (resolved manually)
        ("fredonia", "d3hoops"): "242",           # Fredonia
        ("suny fredonia", "d3hoops"): "242",       # Fredonia
        ("new paltz", "d3hoops"): "475",           # SUNY New Paltz
        ("suny new paltz", "d3hoops"): "475",      # SUNY New Paltz
        ("oneonta", "d3hoops"): "526",             # SUNY Oneonta
        ("suny-oneonta", "d3hoops"): "526",        # SUNY Oneonta
        ("suny potsdam", "d3hoops"): "552",        # SUNY Potsdam
        ("cornell college", "d3hoops"): "166",     # Cornell (IA)
    }
    for (alias_val, vtype), ncaa_id in manual_overrides.items():
        aliases.append({
            "alias_value": alias_val,
            "variant_type": vtype,
            "ncaa_id": ncaa_id,
        })

    # Remove those from unresolved
    override_keys = {k[0] for k in manual_overrides}
    unresolved = [(v, a, t) for v, a, t in unresolved if a not in override_keys]

    # Deduplicate
    seen = set()
    unique_aliases = []
    for a in aliases:
        key = (a["alias_value"].lower(), a["variant_type"], a["ncaa_id"])
        if key not in seen:
            seen.add(key)
            unique_aliases.append(a)

    # Write aliases.csv
    output_path = data_dir / "aliases.csv"
    fieldnames = ["alias_value", "variant_type", "ncaa_id"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted(unique_aliases, key=lambda x: (x["variant_type"], x["alias_value"])))

    print(f"\nWrote {len(unique_aliases)} aliases to {output_path}")

    if unresolved:
        print(f"\n  WARNING: {len(unresolved)} aliases could not be resolved to an ncaa_id:")
        for vtype, alias, target in sorted(unresolved):
            print(f"    [{vtype}] '{alias}' -> '{target}'")


if __name__ == "__main__":
    main()
