"""Shared setup: finds the .env file in the project folder and creates the Claude client.

If the key is missing, it explains exactly what to fix instead of a long traceback.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import anthropic

PROJECT_DIR = Path(__file__).resolve().parent.parent   # the polygon-agent folder
ENV_FILE = PROJECT_DIR / ".env"

load_dotenv(ENV_FILE)
MODEL = os.getenv("MODEL", "claude-haiku-5-5")


def get_client() -> anthropic.Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not ENV_FILE.exists():
        others = [p.name for p in PROJECT_DIR.glob(".env*")] + [p.name for p in PROJECT_DIR.glob("env*")]
        sys.exit(
            f"\nNo .env file found at:\n  {ENV_FILE}\n"
            f"Files that look similar in that folder: {others or 'none'}\n"
            "Fix (VS Code, Windows or Mac): right-click .env.example in the Explorer -> Copy, then Paste,\n"
            "rename the copy to exactly  .env  (in the polygon-agent folder, not inside .venv),\n"
            "open it, paste your key after ANTHROPIC_API_KEY= and save.\n"
        )
    if not key or key == "sk-ant-your-key-here":
        sys.exit(
            f"\n.env was found at {ENV_FILE}, but ANTHROPIC_API_KEY is empty or still the placeholder.\n"
            "Open .env in VS Code and make the line look like:\n"
            "  ANTHROPIC_API_KEY=sk-ant-api03-...   (no quotes, no spaces around =)\n"
        )
    if not key.startswith("sk-ant-"):
        print("Warning: the key does not start with 'sk-ant-'. Check that you copied the whole key.")
    return anthropic.Anthropic(api_key=key)


def get_text(response) -> str:
    """Return only the text parts of a reply.

    A reply can contain several blocks: 'thinking' (the model reasoning first), 'tool_use',
    and 'text'. Never assume content[0] is the text.
    """
    return "".join(b.text for b in response.content if b.type == "text")
