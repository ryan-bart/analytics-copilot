"""DAX measure suggestion engine using Claude."""

import json
import logging
from dataclasses import dataclass

from backend.llm.client import MODEL, get_client
from backend.llm.prompts import DAX_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class DaxMeasure:
    name: str
    expression: str
    description: str


@dataclass
class DaxResult:
    measures: list[DaxMeasure]
    error: str | None = None


def suggest_dax(question: str, sql: str, columns: list[str]) -> DaxResult:
    """Generate DAX measure suggestions based on a query context."""
    client = get_client()

    user_message = (
        f"Question: {question}\n\n"
        f"SQL Query:\n{sql}\n\n"
        f"Result Columns: {', '.join(columns)}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=DAX_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error("Failed to parse DAX response: %s", raw_text[:200])
        return DaxResult(measures=[], error="Failed to parse AI response")

    measures = [
        DaxMeasure(
            name=m.get("name", ""),
            expression=m.get("expression", ""),
            description=m.get("description", ""),
        )
        for m in parsed.get("measures", [])
    ]

    return DaxResult(measures=measures)
