"""Deterministic spatial facts about an alert polygon: which named places are in or near it,
and WHERE they are (north part, crosses east-west, just outside the east edge...).

The LLM will only phrase these facts. It never decides what is inside the polygon.
"""
import json
import math

import numpy as np
import shapely
from shapely.geometry import shape
from pyproj import Transformer

import _paths  # noqa: F401  (makes week1 importable)

_fwd = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)  # to meters (Albers)
METERS_PER_MILE = 1609.344


def _project(geom):
    def f(coords):
        x, y = _fwd.transform(coords[:, 0], coords[:, 1])
        return np.column_stack([x, y])
    return shapely.transform(geom, f)


def load_places(path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        fc = json.load(f)
    places = []
    for i, feat in enumerate(fc["features"]):
        p = feat["properties"]
        places.append({
            "id": i,
            "name": p["name"],
            "kind": p.get("kind", "place"),
            "description": p.get("description", ""),
            "geometry": shape(feat["geometry"]),
            # the text we embed: name + kind + description
            "text": f"{p['name']} ({p.get('kind', 'place')}): {p.get('description', '')}",
        })
    return places


def _compass(dx: float, dy: float) -> str:
    angle = (math.degrees(math.atan2(dx, dy)) + 360) % 360  # 0 = north, clockwise
    return ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"][
        int((angle + 22.5) // 45) % 8]


def describe_position(place_geom_m, poly_m) -> str:
    """Plain, deterministic description of where a place sits relative to the polygon."""
    c = poly_m.centroid
    minx, miny, maxx, maxy = poly_m.bounds
    half_size = max(maxx - minx, maxy - miny) / 2

    if place_geom_m.geom_type in ("LineString", "MultiLineString"):
        inside = place_geom_m.intersection(poly_m)
        if inside.is_empty:
            p = place_geom_m.interpolate(place_geom_m.project(c))
            return f"just outside the {_compass(p.x - c.x, p.y - c.y)} edge"
        ix0, iy0, ix1, iy1 = inside.bounds
        direction = "east-west" if (ix1 - ix0) >= (iy1 - iy0) else "north-south"
        mid = inside.centroid
        off = math.hypot(mid.x - c.x, mid.y - c.y)
        where = "through the middle" if off < 0.25 * half_size else f"through the {_compass(mid.x - c.x, mid.y - c.y)} part"
        return f"runs {direction} {where}"

    pt = place_geom_m.representative_point()
    dx, dy = pt.x - c.x, pt.y - c.y
    if not poly_m.contains(pt):
        return f"just outside the {_compass(dx, dy)} edge"
    if math.hypot(dx, dy) < 0.25 * half_size:
        return "near the center"
    return f"in the {_compass(dx, dy)} part"


def places_near(polygon_geojson: dict, places: list[dict], buffer_miles: float = 1.0) -> list[dict]:
    """Spatial filter: places inside the polygon, or within `buffer_miles` of its edge."""
    poly_m = _project(shape(polygon_geojson))
    zone = poly_m.buffer(buffer_miles * METERS_PER_MILE)

    geoms_m = [_project(p["geometry"]) for p in places]
    tree = shapely.STRtree(geoms_m)                       # spatial index, like a GIS index
    hits = tree.query(zone, predicate="intersects")

    results = []
    for i in sorted(hits):
        g = geoms_m[i]
        results.append({
            **{k: v for k, v in places[i].items() if k != "geometry"},
            "inside": bool(g.intersects(poly_m)),
            "position": describe_position(g, poly_m),
        })
    return results
