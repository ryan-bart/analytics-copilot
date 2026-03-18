# Analytics Copilot

AI-powered analytics copilot — ask questions in plain English, get SQL, visualizations, and DAX measures.

Built with Python, FastAPI, React, and Claude to demonstrate end-to-end AI-powered analytics workflows.

## Features

- **Natural Language to SQL** — Ask questions like "Total premium by product line" and get accurate SQL
- **Auto-Visualization** — Automatic chart type detection (bar, line, pie, number card) with Plotly
- **DAX Suggestions** — Generate Power BI DAX measures for any query with one click
- **Query History** — Browse and re-run past queries
- **Schema Explorer** — Interactive sidebar showing all tables and columns
- **MCP Server** — Use as a tool in Claude Desktop for conversational analytics
- **SQL Guardrails** — Read-only enforcement prevents any write operations

## How It Works

The app has two halves — a **React frontend** (Vite dev server on port 5173) and a **Python backend** (FastAPI on port 8000) — connected by a REST API. Vite proxies `/api/*` requests to the backend during development so everything feels like a single app.

### Request lifecycle

Here's what happens when you type a question like "Total premium by product line":

1. **Frontend → Backend** — The React `QueryInput` component sends a `POST /api/query` with `{ "question": "Total premium by product line" }`.

2. **Schema introspection** — The backend reads the SQLite database schema (table names, column types, foreign keys) and builds a DDL string. Low-cardinality VARCHAR columns are annotated with their actual distinct values (e.g. `-- values: 'Auto', 'Home', 'Life'`) so the LLM knows what valid filter values look like.

3. **SQL generation (Claude API)** — The schema DDL and the user's question are sent to Claude (Sonnet). Claude returns a JSON object containing: the SQL query, a plain-English explanation, and a suggested chart type.

4. **Guardrails** — Before executing anything, the generated SQL is validated: it must be a single `SELECT` or `WITH` statement with no blocked keywords (`INSERT`, `DROP`, `ALTER`, etc.). This is a hard gate — if validation fails, the query is rejected.

5. **Execution** — The validated SQL runs against the SQLite database in read-only mode. Results come back as a list of row dictionaries.

6. **Visualization** — The backend picks a chart type (bar, line, pie, scatter, or number card) based on the result shape and Claude's suggestion, then builds a Plotly JSON spec (data + layout). This means chart logic lives server-side — the frontend is just a renderer.

7. **Response** — Everything is bundled into a single JSON response: `sql`, `explanation`, `columns`, `rows`, `chart_json`, and sent back to the frontend.

8. **Rendering** — The frontend renders the results table, the Plotly chart (lazy-loaded via `react-plotly.js`), and a "Generate DAX" button. An `ErrorBoundary` wraps the result area so a rendering failure in one component doesn't crash the whole page.

### DAX generation

Clicking "Generate DAX" sends the question, SQL, and column names to `POST /api/dax`. The backend calls Claude again with a DAX-specific prompt and returns suggested Power BI measures.

### MCP Server

There's also a standalone MCP server (`backend/mcp_server.py`) that exposes the same query/schema/DAX capabilities as tools for Claude Desktop, using stdio transport instead of HTTP.

### Architecture diagram

```mermaid
graph TB
    User([User]) --> Frontend[React Frontend<br/>Vite + Tailwind + Plotly]
    User --> Claude[Claude Desktop<br/>via MCP]

    Frontend -->|REST API| Backend[FastAPI Backend]
    Claude -->|stdio| MCP[MCP Server]

    Backend --> LLM[Claude API<br/>NL → SQL + DAX]
    Backend --> DB[(SQLite<br/>Insurance Data)]
    Backend --> Viz[Chart Builder<br/>Plotly JSON]
    Backend --> Guard[SQL Guardrails]

    MCP --> LLM
    MCP --> DB

    Guard -->|validates| DB
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
# Clone and enter the project
git clone https://github.com/ryan-bart/analytics-copilot.git
cd analytics-copilot

# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY

# Seed the database
python -m backend.database.seed

# Start the backend (port 8000)
python -m backend.main

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### MCP Server (Claude Desktop)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "analytics-copilot": {
      "command": "/path/to/analytics-copilot/.venv/bin/python",
      "args": ["-m", "backend.mcp_server"],
      "cwd": "/path/to/analytics-copilot"
    }
  }
}
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/schema` | Full database schema |
| `GET` | `/api/schema/{table}` | Single table schema |
| `POST` | `/api/query` | Natural language query → SQL → results |
| `POST` | `/api/dax` | Generate DAX measures for a query |
| `GET` | `/api/history` | Recent query history |
| `GET` | `/api/history/{id}` | Single history item |

## Example Queries

- "How many active policies are there?"
- "Total premium by product line"
- "Monthly claim counts over time"
- "Top 10 customers by total premium"
- "Average claim amount by region"
- "Policy status distribution"

## Tech Stack

| Layer | Technology |
|-------|------------|
| AI | Anthropic Claude API (Sonnet) |
| Backend | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend | React, TypeScript, Vite, Tailwind CSS v4 |
| Visualization | Plotly (server-side JSON → react-plotly.js) |
| MCP | FastMCP with stdio transport |
| Testing | pytest (35 tests) |

## Docker

```bash
cd docker
ANTHROPIC_API_KEY=your-key docker compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

## Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Dataset

Seeded insurance database with realistic distributions:

- **200** customers across 5 US regions
- **385** policies (Auto, Home, Life, Commercial, Health)
- **341** claims (Collision, Liability, Comprehensive, Property Damage, Medical)
- **871** payments with multiple payment methods
- Data spans 2022–2025

## License

MIT
