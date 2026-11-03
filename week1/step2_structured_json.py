"""Step 2: make the model return reliable JSON, then CHECK it in code.

Two layers of safety:
  1. Structured outputs (output_config) -- the API forces the reply to match a JSON schema.
  2. Your own validation -- the model is never the final authority.
"""
import json
from client_setup import get_client, get_text, MODEL

client = get_client()

# The allowed values are the CAP 1.2 severity and urgency values -- week 3 explains them.
SEVERITY = ["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
URGENCY = ["Immediate", "Expected", "Future", "Unknown"]

SCHEMA = {
    "type": "object",
    "properties": {
        "hazard_type": {"type": "string"},
        "severity": {"type": "string", "enum": SEVERITY},
        "area_name": {"type": "string"},
        "urgency": {"type": "string", "enum": URGENCY},
    },
    "required": ["hazard_type", "severity", "area_name", "urgency"],
    "additionalProperties": False,
}

SYSTEM = """You extract alert details from a short hazard description.
Use "Unknown" when the description does not say.

Example input: "Tornado spotted near Sugar Land moving northeast, take shelter now"
Example output: {"hazard_type": "Tornado", "severity": "Extreme", "area_name": "Sugar Land", "urgency": "Immediate"}
"""


def extract(description: str) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM,
        messages=[{"role": "user", "content": description}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    data = json.loads(get_text(response))

    # Validate in code anyway -- never trust model output blindly
    missing = set(SCHEMA["required"]) - data.keys()
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    if data["severity"] not in SEVERITY:
        raise ValueError(f"Bad severity: {data['severity']}")
    if data["urgency"] not in URGENCY:
        raise ValueError(f"Bad urgency: {data['urgency']}")
    return data


if __name__ == "__main__":
    tests = [
        "Flash flooding along Buffalo Bayou in west Houston, water rising fast, avoid roads now",
        "Wildfire 5 miles west of Magnolia, may reach homes by tonight",
        "Chemical release at a plant in Pasadena, shelter in place",
    ]
    for t in tests:
        try:
            print(extract(t))
        except Exception as e:
            print("REJECTED:", e)
