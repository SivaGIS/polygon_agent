"""Deterministic geometry tools. The LLM never computes geometry -- it only calls these."""
import json
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import shape
from shapely.validation import explain_validity
from pyproj import Transformer

# WGS84 (lon/lat) -> USA Contiguous Albers Equal Area, so areas come out in true square meters
_albers = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)


def _to_albers(coords):
    x, y = _albers.transform(coords[:, 0], coords[:, 1])
    return np.column_stack([x, y])

SQ_M_PER_SQ_MI = 2_589_988.110336


def get_polygon_area(geojson: dict) -> dict:
    """Return area in square miles plus a validity check for a GeoJSON Polygon/MultiPolygon."""
    geom = shape(geojson)
    if not geom.is_valid:
        return {"valid": False, "reason": explain_validity(geom)}
    area_sq_mi = shapely.transform(geom, _to_albers).area / SQ_M_PER_SQ_MI
    minx, miny, maxx, maxy = geom.bounds
    return {
        "valid": True,
        "area_sq_mi": round(area_sq_mi, 2),
        "vertex_count": len(geom.exterior.coords) if geom.geom_type == "Polygon" else None,
        "bbox": [round(v, 4) for v in (minx, miny, maxx, maxy)],
    }


def load_geojson(path: str) -> dict:
    """Load a file and return the geometry part (works for Feature or bare geometry)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("geometry", data)


if __name__ == "__main__":
    # Quick self-test without any API key
    here = Path(__file__).resolve().parent
    print("sample_warning:", get_polygon_area(load_geojson(here / "sample_warning.geojson")))
    print("bowtie:        ", get_polygon_area(load_geojson(here / "bowtie_invalid.geojson")))
