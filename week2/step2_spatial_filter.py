"""Step 2: spatial filter -- which named places are in or near the alert polygon, and where.

This is pure GIS (Shapely + an STRtree spatial index). No AI, no API key.
Location first, meaning second: we never ask the model "what is near here?"
"""
import json

import _paths
from spatial_context import load_places, places_near
from geo_tools import load_geojson

places = load_places(_paths.places_file())
polygon = load_geojson(_paths.SAMPLE_POLYGON)

print(f"Gazetteer: {_paths.places_file().name} ({len(places)} places)")
print("Alert polygon: week1/sample_warning.geojson\n")

nearby = places_near(polygon, places, buffer_miles=1.0)
print(f"{len(nearby)} places inside or within 1 mile:\n")
for p in nearby:
    flag = "IN " if p["inside"] else "near"
    print(f"  [{flag}] {p['name']:<32} {p['kind']:<24} {p['position']}")

skipped = [p["name"] for p in places if p["name"] not in {n["name"] for n in nearby}]
print(f"\nFiltered out (too far away): {', '.join(skipped)}")

# Save for the next step / for inspection in VS Code
with open(_paths.WEEK2_DIR / "nearby_places.json", "w", encoding="utf-8") as f:
    json.dump(nearby, f, indent=2)
print("\nSaved nearby_places.json")
