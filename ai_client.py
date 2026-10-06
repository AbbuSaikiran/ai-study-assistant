"""Generative AI API: sends prompts to the model and returns the text."""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.6-flash"


def get_api_key(secrets=None) -> str | None:
    """Look for the key in environment variables, then Streamlit secrets."""
    load_dotenv(override=True)
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key and key.strip() and key != "your-gemini-api-key-here":
        return key.strip()
    if secrets is not None:
        try:
            return secrets.get("GEMINI_API_KEY") or secrets.get("GOOGLE_API_KEY")
        except Exception:
            return None
    return None


def ask_ai(system: str, user: str, api_key: str, model_name: str | None = None) -> str:
    chosen_model = model_name or os.getenv("AI_MODEL", DEFAULT_MODEL)
    client = genai.Client(api_key=api_key)
    try:
        interaction = client.interactions.create(
            model=chosen_model,
            system_instruction=system,
            input=user,
        )
        if interaction.output_text:
            return interaction.output_text
    except Exception:
        pass

    # Standard fallback
    config = types.GenerateContentConfig(
        system_instruction=system
    )
    response = client.models.generate_content(
        model=chosen_model,
        contents=user,
        config=config,
    )
    return response.text or ""
