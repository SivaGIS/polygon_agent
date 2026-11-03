"""Lets week2 scripts reuse week1 code (client_setup, geo_tools) and find their own data files."""
import sys
from pathlib import Path

WEEK2_DIR = Path(__file__).resolve().parent
WEEK1_DIR = WEEK2_DIR.parent / "week1"
if str(WEEK1_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK1_DIR))

DEFAULT_PLACES = WEEK2_DIR / "places_west_houston.geojson"
OSM_PLACES = WEEK2_DIR / "places_osm.geojson"          # created by fetch_osm_places.py
SAMPLE_POLYGON = WEEK1_DIR / "sample_warning.geojson"


def places_file() -> Path:
    """Use real OpenStreetMap data if you downloaded it, otherwise the practice file."""
    return OSM_PLACES if OSM_PLACES.exists() else DEFAULT_PLACES
