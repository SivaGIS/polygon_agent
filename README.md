# polygon-agent

A practice geospatial AI agent for emergency alert polygons: import hazard geometry, validate it,
measure over/under-alerting, and let an LLM describe the area in plain language -- while all
geometry is computed by deterministic code and approved by a person.

## Week 1 -- LLM basics
| File | What it teaches |
|---|---|
| `week1/geo_tools.py` | Deterministic geometry: validity check + true area in sq mi (Albers equal-area) |
| `week1/step1_hello.py` | First LLM call: system prompt, messages, tokens |
| `week1/step2_structured_json.py` | Structured outputs (JSON schema) + validating in code |
| `week1/step3_tool_calling.py` | Tool calling: the model asks, Shapely computes |

## Week 2 -- RAG: embeddings, vector search, local place names
| File | What it teaches |
|---|---|
| `week2/step1_embeddings_intro.py` | Embeddings: similar meanings score close together (no API key) |
| `week2/step2_spatial_filter.py` | Spatial retrieval: STRtree + deterministic position facts (no API key) |
| `week2/step3_rag_describe.py` | Full RAG: spatial filter -> semantic ranking -> LLM wording -> guardrail |
| `week2/fetch_osm_places.py` | Optional: real place names from OpenStreetMap (Overpass API) |
| `week2/spatial_context.py`, `vector_store.py`, `embeddings.py` | The building blocks |

Rule: location first (GIS decides what is in the area), meaning second (embeddings rank it),
and the model only phrases facts it was given -- code rejects any name that was not retrieved.

## Setup -- Windows 11 (PowerShell in VS Code)
Tested with Python 3.14 (also works on 3.12-3.13).

```
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python check_setup.py         # confirms versions
copy .env.example .env        # then paste your API key into .env
python week1\geo_tools.py     # works with no API key
python week1\step1_hello.py
```
If PowerShell says "running scripts is disabled", run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer Y, then activate again.

## Setup -- macOS 12 Monterey
Requires Python 3.10-3.12 (pyproj 3.6.1 has no Python 3.13 build).

```
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python check_setup.py
cp .env.example .env          # then paste your API key into .env
python week1/geo_tools.py
python week1/step1_hello.py
```
