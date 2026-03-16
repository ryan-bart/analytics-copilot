# Analytics Copilot

AI-powered analytics copilot — ask questions in plain English, get SQL, visualizations, and DAX measures.

## Status

Under active development. See [Implementation Plan](#) for details.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY
python -m backend.database.seed
```

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **AI**: Anthropic Claude API
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Plotly
- **Tools**: MCP Server, DAX generation

## License

MIT
