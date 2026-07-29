# Enterprise Workflow Agent

A distributed agentic platform (FastAPI + LangGraph) that orchestrates workflows across enterprise systems — Slack, Gmail, GitHub, Jira, Calendar — via governed MCP tool access, with human-in-the-loop approvals and PostgreSQL-backed checkpointing.

## Project Structure

```
enterprise-workflow-agent/
├── app/                          # Application source
│   ├── main.py                   # FastAPI entry point
│   ├── config.py                 # Environment-based settings
│   ├── api/                      # HTTP route handlers (routers only)
│   │   ├── workflows.py          # Workflow endpoints
│   │   └── approvals.py          # Approval endpoints
│   ├── agent/                    # LangGraph orchestration layer
│   │   ├── graph.py              # Workflow graph definition
│   │   ├── nodes.py              # Graph node functions
│   │   └── state.py              # Shared state schema
│   ├── mcp/                      # MCP tool integration & governance
│   │   ├── client.py             # MCP server communication
│   │   ├── registry.py           # Tool registration
│   │   └── policies.py           # Access-control policy (security-sensitive)
│   ├── services/                 # Business logic
│   │   ├── approval.py           # Human-in-the-loop approvals
│   │   ├── audit.py              # Audit trail
│   │   └── execution.py          # Workflow execution
│   ├── db/                       # Database access
│   │   ├── postgres.py           # PostgreSQL connection
│   │   └── checkpoint.py         # LangGraph checkpoint persistence
│   └── observability/            # Logging, metrics, tracing
│       ├── logging.py
│       ├── metrics.py
│       └── tracing.py
├── tests/                        # Test suite (mirrors app/ layers)
│   ├── conftest.py
│   ├── api/
│   ├── agent/
│   ├── mcp/
│   ├── services/
│   └── db/
├── migrations/                   # Database migrations
│   └── versions/
├── docker-compose.yml            # Local dev stack (app + Postgres)
├── Dockerfile
├── pyproject.toml
├── .env.example
├── AGENTS.md                     # Agent coding guidelines
└── CLAUDE.md                     # Claude Code guidelines
```

## Architecture

| Layer | Responsibility |
|-------|----------------|
| `app/api/` | HTTP handlers — delegates to services, no business logic |
| `app/agent/` | LangGraph orchestration — calls services and MCP, not DB/APIs directly |
| `app/mcp/` | All external tool integrations and access-control policy |
| `app/services/` | Approval workflows, execution, audit trail |
| `app/db/` | All database and checkpoint access |
| `app/observability/` | Structured logging, metrics, tracing |

## Quick Start

```bash
# Copy environment template
cp .env.example .env

# Install dependencies
pip install -e ".[dev]"

# Start Postgres (and app) via Docker
docker compose up -d

# Run the API locally
uvicorn app.main:app --reload --port 8000
```

## Verify

```bash
pytest
ruff check .
ruff format --check .
mypy app
```

## Integrations

Planned MCP-backed integrations:

- **Slack** — messaging and notifications
- **Gmail** — email workflows
- **GitHub** — PR and issue automation
- **Jira** — ticket management
- **Calendar** — scheduling

All mutating actions flow through the approval service and are recorded in the audit trail.
