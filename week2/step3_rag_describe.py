"""Step 3: RAG -- Retrieval-Augmented Generation for alert-area wording.

  1. RETRIEVE (spatial): places inside / near the polygon        -> deterministic GIS
  2. RETRIEVE (semantic): rank them by what helps people locate  -> embeddings
  3. GENERATE: the model writes the description from ONLY those facts
  4. GUARDRAIL: code rejects any name that was not retrieved

Run with --compare to also see what the model writes WITHOUT retrieval (it may invent names).
"""
import json
import sys

import _paths
from client_setup import get_client, get_text, MODEL
from geo_tools import load_geojson
from spatial_context import load_places, places_near
from vector_store import VectorStore

client = get_client()

QUERY = "major highways, roads and well-known landmarks residents use to know where they are"

SCHEMA = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "names_used": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["description", "names_used"],
    "additionalProperties": False,
}

SYSTEM = """You write the location part of a public emergency alert.
Rules:
- Use ONLY place names from the PLACES list, spelled exactly as given.
- Use the position facts given; do not guess other locations.
- One or two short sentences, plain language, no coordinates.
- List every place name you used in names_used."""


def retrieve(polygon: dict, k: int = 8) -> list[dict]:
    places = load_places(_paths.places_file())
    nearby = places_near(polygon, places, buffer_miles=1.0)          # 1. spatial
    store = VectorStore()
    store.add(nearby)                                                 # embed only nearby places
    ranked = store.search(QUERY, k=k)                                 # 2. semantic
    for score, rec in ranked:
        print(f"  {score:5.2f}  {rec['name']:<32} {rec['position']}")
    return [rec for _, rec in ranked]


def generate(hazard: str, facts: list[dict]) -> dict:
    places_text = "\n".join(f"- {p['name']} ({p['kind']}): {p['position']}" for p in facts)
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Hazard: {hazard}\n\nPLACES:\n{places_text}"}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    return json.loads(get_text(response))


def guardrail(result: dict, facts: list[dict]) -> list[str]:
    """Deterministic check: every name used must come from retrieval and appear in the text."""
    allowed = {p["name"] for p in facts}
    problems = [f"'{n}' was not retrieved" for n in result["names_used"] if n not in allowed]
    problems += [f"'{n}' listed but not in the text" for n in result["names_used"]
                 if n not in result["description"]]
    return problems


def without_rag(hazard: str) -> str:
    response = client.messages.create(
        model=MODEL, max_tokens=300,
        system="You write the location part of a public emergency alert. One or two sentences.",
        messages=[{"role": "user", "content": f"Hazard: {hazard}. The polygon covers roughly "
                   "longitude -95.82 to -95.50, latitude 29.70 to 29.90. Describe the area."}],
    )
    return get_text(response)


if __name__ == "__main__":
    hazard = "Flash Flood Warning"
    polygon = load_geojson(_paths.SAMPLE_POLYGON)

    print("Retrieved places (score = similarity to the query):")
    facts = retrieve(polygon)

    result = generate(hazard, facts)
    print("\nDescription:\n ", result["description"])
    print("Names used:", result["names_used"])

    problems = guardrail(result, facts)
    print("\nGuardrail:", "PASSED" if not problems else "REJECTED -> " + "; ".join(problems))

    if "--compare" in sys.argv:
        print("\nWithout RAG (no place list -- check every name yourself):\n ", without_rag(hazard))
