# Analytics Copilot

## Commands

```bash
# Backend
source .venv/bin/activate
python -m backend.main              # Start API on :8000
python -m backend.database.seed     # Seed database
python -m backend.mcp_server        # Start MCP server

# Frontend
cd frontend && npm run dev          # Start dev server on :5173

# Tests & Linting
pytest tests/ -v                    # Run all tests
ruff check backend/                 # Lint Python
cd frontend && npx tsc --noEmit     # TypeScript check
```

## Architecture

- `backend/` — Python FastAPI application
  - `api/` — REST endpoints and Pydantic schemas
  - `database/` — SQLAlchemy models, engine, seeder, inspector
  - `llm/` — Claude API client, SQL/DAX generation, guardrails, prompts
  - `visualization/` — Chart type picker and Plotly chart builder
  - `history/` — Query history persistence
  - `main.py` — FastAPI app entry point
  - `mcp_server.py` — MCP server for Claude Desktop
  - `config.py` — pydantic-settings configuration
- `frontend/` — React + TypeScript + Vite
  - `src/components/` — QueryInput, ResultsTable, ChartView, DaxPanel, SchemaPanel, HistoryPanel
  - `src/api/client.ts` — API fetch wrappers
  - `src/types/` — TypeScript interfaces
- `tests/` — pytest test suite

## Conventions

- Python linting: ruff with E, F, I, N, W rules, 100 char line length
- Prompt strings in `backend/llm/prompts.py` are exempt from E501
- SQLite database at `data/insurance.db` (gitignored)
- All SQL execution goes through guardrails (SELECT-only)
- Chart type is picked server-side; frontend is a thin Plotly renderer
