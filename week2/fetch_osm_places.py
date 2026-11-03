"""Optional (day 6): download REAL place names from OpenStreetMap for the alert polygon's area.

Writes week2/places_osm.geojson. Steps 2 and 3 automatically use it once it exists
(delete the file to go back to the practice gazetteer).

Uses the free Overpass API -- please run it only occasionally (it is a shared public service).
"""
import json
import urllib.parse
import urllib.request
from collections import defaultdict

from shapely.geometry import LineString, Point, Polygon, mapping, shape
from shapely.ops import unary_union

import _paths
from geo_tools import load_geojson

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

KIND = [  # (OSM tag, value test, our kind)
    ("highway", lambda v: v in ("motorway", "trunk"), "highway"),
    ("highway", lambda v: v == "primary", "major road"),
    ("waterway", lambda v: v in ("river", "stream", "canal"), "waterway"),
    ("leisure", lambda v: v == "park", "park"),
    ("amenity", lambda v: v == "hospital", "hospital"),
    ("place", lambda v: v in ("town", "suburb", "neighbourhood", "village"), "neighborhood"),
    ("natural", lambda v: v == "water", "water"),
]


def build_query(south, west, north, east) -> str:
    bbox = f"{south},{west},{north},{east}"
    return f"""[out:json][timeout:60];
(
  way["highway"~"^(motorway|trunk|primary)$"]["name"]({bbox});
  way["waterway"~"^(river|stream|canal)$"]["name"]({bbox});
  way["leisure"="park"]["name"]({bbox});
  way["natural"="water"]["name"]({bbox});
  node["amenity"="hospital"]["name"]({bbox});
  way["amenity"="hospital"]["name"]({bbox});
  node["place"~"^(town|suburb|neighbourhood|village)$"]["name"]({bbox});
);
out geom;"""


def classify(tags: dict) -> str | None:
    for key, test, kind in KIND:
        if key in tags and test(tags[key]):
            return kind
    return None


def to_geometry(el: dict):
    if el["type"] == "node":
        return Point(el["lon"], el["lat"])
    coords = [(p["lon"], p["lat"]) for p in el.get("geometry", [])]
    if len(coords) < 2:
        return None
    if len(coords) >= 4 and coords[0] == coords[-1]:
        poly = Polygon(coords)
        return poly.representative_point() if poly.is_valid else LineString(coords)
    return LineString(coords)


def convert(elements: list[dict]) -> dict:
    """Overpass JSON -> GeoJSON. Road pieces with the same name are merged into one feature."""
    groups = defaultdict(list)
    for el in elements:
        tags = el.get("tags", {})
        kind = classify(tags)
        geom = to_geometry(el)
        if kind and geom is not None:
            name = tags["name"]
            if tags.get("ref") and kind in ("highway", "major road") and tags["ref"] not in name:
                name = f"{name} ({tags['ref']})"
            groups[(name, kind)].append(geom)

    features = []
    for (name, kind), geoms in sorted(groups.items()):
        merged = unary_union(geoms)
        if merged.geom_type in ("MultiPoint", "GeometryCollection"):
            merged = merged.representative_point()
        features.append({
            "type": "Feature",
            "properties": {"name": name, "kind": kind, "description": f"{kind} from OpenStreetMap"},
            "geometry": mapping(merged),
        })
    return {"type": "FeatureCollection",
            "name": "OpenStreetMap places (c) OpenStreetMap contributors, ODbL",
            "features": features}


def fetch(polygon: dict, margin_deg: float = 0.03) -> dict:
    minx, miny, maxx, maxy = shape(polygon).bounds
    query = build_query(miny - margin_deg, minx - margin_deg, maxy + margin_deg, maxx + margin_deg)
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data,
                                 headers={"User-Agent": "polygon-agent-learning-project"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


if __name__ == "__main__":
    polygon = load_geojson(_paths.SAMPLE_POLYGON)
    print("Asking OpenStreetMap (Overpass API) for named places... this can take 10-60 seconds")
    raw = fetch(polygon)
    fc = convert(raw.get("elements", []))
    with open(_paths.OSM_PLACES, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False)
    kinds = defaultdict(int)
    for feat in fc["features"]:
        kinds[feat["properties"]["kind"]] += 1
    print(f"Saved {len(fc['features'])} places to {_paths.OSM_PLACES.name}: {dict(kinds)}")
    print("Steps 2 and 3 will now use this real data. Delete the file to go back to the practice data.")
