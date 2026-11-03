"""Step 1: your first LLM call. Learn: system prompt, messages, max_tokens, tokens.

Note: the Claude API removed the `temperature` setting on 2026-10-21, so answers can vary
from run to run. In this project, consistency comes from clear prompts, a fixed output
schema (step 2) and checking every answer in code -- not from a sampling setting.
"""
from client_setup import get_client, get_text, MODEL

client = get_client()

response = client.messages.create(
    model=MODEL,
    max_tokens=300,
    system="You are an assistant for emergency alert originators. Be brief and factual.",
    messages=[
        {"role": "user", "content": "In two sentences, what is a Wireless Emergency Alert?"}
    ],
)

print(get_text(response))
print("\n--- tokens used:", response.usage.input_tokens, "in /", response.usage.output_tokens, "out")
