"""All Gemini calls live here."""
import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM = (
    "You are PocketSmart AI, a friendly personal finance assistant. "
    "Give practical, specific, short advice based on the user's data. "
    "Use bullet points. You are not a licensed financial advisor."
)


def _client(api_key: str | None = None):
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Missing GEMINI_API_KEY. Add it to .env or the sidebar.")
    return genai.Client(api_key=key)


def _ask(prompt: str, api_key=None) -> str:
    resp = _client(api_key).models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"system_instruction": SYSTEM},
    )
    return resp.text or ""


def get_advice(summary: dict, question: str, api_key=None) -> str:
    prompt = f"User's budget summary (JSON):\n{json.dumps(summary)}\n\nQuestion: {question}"
    return _ask(prompt, api_key)


def get_recommendations(summary: dict, goal: str, target: float, months: int, api_key=None) -> str:
    prompt = (
        f"Budget summary:\n{json.dumps(summary)}\n\n"
        f"Goal: {goal}. Target amount: {target}. Timeline: {months} months.\n"
        "1) Say if it's achievable and the monthly saving needed.\n"
        "2) Suggest 5 specific cuts by category.\n"
        "3) Suggest a simple monthly plan."
    )
    return _ask(prompt, api_key)


def auto_categorize(description: str, categories: list[str], api_key=None) -> str:
    prompt = (
        f"Pick the single best category for this expense: '{description}'.\n"
        f"Options: {', '.join(categories)}.\nReply with the category name only."
    )
    try:
        out = _ask(prompt, api_key).strip().split("\n")[0].strip(" .*")
        return out if out in categories else "Other"
    except Exception:
        return "Other"