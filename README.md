# MCP From Zero

Code for the video **"MCP From Zero"**: building a Model Context Protocol server for **TrailMart**, a small outdoor-gear shop's support desk, step by step, with real runs.

- MCP specification **2026-07-28** · Python SDK `mcp` **2.3.0** · PostgreSQL **18** · Python **3.15** (via `uv`)
- Every request and answer shown in the video came from these files.

## Layout

| Folder | Video part |
|---|---|
| `parts/02-messages-on-the-wire` | The raw JSON-RPC messages, sent by hand |
| `parts/03-first-server` | A first server with one fake tool, tested in the MCP Inspector |
| `parts/05-postgres-read-tools` | `find_products` and `get_order` on Postgres, least-privilege roles |
| `parts/06-results-and-errors` | Before and after a `ToolError` for a missing order |
| `parts/07-resources-and-prompts` | `policy://returns`, `order://{order_id}`, a late-delivery prompt |
| `parts/08-weather-api` | `check_trail_weather` with Open-Meteo (free, no key, non-commercial) |
| `parts/09-refund-human-yes` | `start_refund` with elicitation and an idempotency key |
| `parts/10-connecting-claude` | `agent.py`: a tiny host with a Claude tool loop |
| `parts/11-going-remote` | Streamable HTTP, `curl`, and Claude Code |
| `parts/12-security-and-tests` | An injection attempt and pytest tests |
| `trailmart/` | The finished server, the agent and the tests |
| `db/` | Schema, seed data and roles for the demo database |

## Run it

```bash
# 1. a local Postgres 18 (the video used port 5545), then:
psql -h localhost -p 5545 -U postgres -c "CREATE DATABASE trailmart"
psql -h localhost -p 5545 -U postgres -d trailmart -f db/schema.sql -f db/seed.sql -f db/roles.sql

# 2. the two addresses the server reads (demo passwords from db/roles.sql)
export TRAILMART_READER_DSN="postgresql://tm_reader:reader-local-only@localhost:5545/trailmart"
export TRAILMART_REFUNDS_DSN="postgresql://tm_refunds:refunds-local-only@localhost:5545/trailmart"

# 3. the finished server
cd trailmart && uv sync
uv run pytest -q                                   # 3 tests
uv run mcp run server.py --transport streamable-http   # http://127.0.0.1:8000/mcp

# 4. the agent (needs your own key; never commit it)
export ANTHROPIC_API_KEY=...
uv run agent.py "Where is order 1042?"
```

The passwords in `db/roles.sql` are for a local demo only. Before you expose a server to other people, add authorization (see the MCP specification's authorization section).
