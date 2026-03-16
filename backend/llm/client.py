import anthropic

from backend.config import settings

MODEL = "claude-sonnet-4-20250514"


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)
