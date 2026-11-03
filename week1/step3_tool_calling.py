"""Step 3: tool calling. The model DECIDES to call get_polygon_area; your Shapely code DOES the math.

This is the core pattern of the job: "the LLM phrases, deterministic code computes."
"""
import json
from pathlib import Path
from client_setup import get_client, MODEL

from geo_tools import get_polygon_area, load_geojson

client = get_client()
DATA_DIR = Path(__file__).resolve().parent  # the week1 folder, wherever you run from

# 1. Describe the tool: name, description, and a JSON Schema for its input
TOOLS = [
    {
        "name": "get_polygon_area",
        "description": (
            "Checks a GeoJSON polygon for validity and returns its area in square miles, "
            "vertex count and bounding box. Always use this tool for any area or validity "
            "question -- never estimate geometry yourself."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "polygon_id": {
                    "type": "string",
                    "enum": ["sample_warning", "bowtie_invalid"],
                    "description": "Which stored polygon to measure.",
                }
            },
            "required": ["polygon_id"],
        },
    }
]
# Note: the model passes an ID, not raw coordinates. Geometry stays in your system,
# so the model can never alter or invent it. Keep this habit for the whole project.


def run_tool(name: str, args: dict) -> dict:
    if name == "get_polygon_area":
        geom = load_geojson(DATA_DIR / f"{args['polygon_id']}.geojson")
        return get_polygon_area(geom)
    raise ValueError(f"Unknown tool {name}")


def ask(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    response = client.messages.create(
        model=MODEL, max_tokens=500, tools=TOOLS, messages=messages,
        system="You help emergency alert originators review alert polygons.",
    )

    # 2. Loop while the model wants to use tools
    while response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [model called {block.name} with {block.input}]")
                try:
                    output = run_tool(block.name, block.input)
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": json.dumps(output)})
                except Exception as e:
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": f"Error: {e}", "is_error": True})
        # 3. Send results back (tool_result blocks must come first in the user message)
        messages.append({"role": "user", "content": results})
        response = client.messages.create(
            model=MODEL, max_tokens=500, tools=TOOLS, messages=messages,
            system="You help emergency alert originators review alert polygons.",
        )

    return "".join(b.text for b in response.content if b.type == "text")


if __name__ == "__main__":
    for q in [
        "How big is the sample_warning polygon, and is it valid?",
        "Can I send an alert using the bowtie_invalid polygon? Explain in plain words.",
    ]:
        print("\nQ:", q)
        print("A:", ask(q))
