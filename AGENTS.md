# AGENTS.md

Guidance for Codex (and other agentic coding tools that read AGENTS.md)
when working in this repository. This mirrors `CLAUDE.md` — keep both in
sync if you update one.

## Project Overview

`enterprise-workflow-agent` is a distributed agentic platform (FastAPI +
LangGraph) that orchestrates workflows across enterprise systems (Slack,
Gmail, GitHub, Jira, Calendar) via governed MCP tool access, with
human-in-the-loop approvals and PostgreSQL-backed checkpointing.

## Architecture & Where Things Live

Respect this separation of concerns. Do not create new top-level
directories or move logic across these boundaries without asking first.

- `app/api/` — HTTP route handlers only (FastAPI routers). No business
  logic here — routes call into `services/`, they don't implement workflow
  logic themselves.
- `app/agent/` — LangGraph graph definition (`graph.py`), node functions
  (`nodes.py`), and shared state schema (`state.py`). This is the
  orchestration layer — it should call `services/` and `mcp/`, not talk to
  the database or external APIs directly.
- `app/mcp/` — all MCP server communication (`client.py`), tool
  registration (`registry.py`), and access-control policy (`policies.py`).
  **Any new external tool integration goes through this layer** — never
  call a third-party API directly from `agent/` or `api/`.
- `app/services/` — business logic: approval workflows, execution,
  audit trail. This is the layer that `agent/` and `api/` should call into.
- `app/db/` — Postgres access (`postgres.py`) and LangGraph checkpoint
  persistence (`checkpoint.py`). All DB access goes through here — no raw
  SQL or ORM calls from other layers.
- `app/observability/` — structured logging, metrics, tracing. Use these
  utilities rather than ad hoc `print()` or a new logging setup.

## Build, Test, and Verify

Always run these before considering a task complete, and report the
results:

```bash
# tests
pytest

# lint / format (adjust to whatever is defined in pyproject.toml)
ruff check .
ruff format --check .

# type check, if configured
mypy app
```

If a command doesn't exist yet in `pyproject.toml`, say so rather than
guessing — don't silently skip verification.

## Conventions

- Follow the existing pattern in the nearest analogous file before
  inventing a new one. E.g. new API routes should mirror the structure of
  `app/api/workflows.py`; new MCP tools should mirror `app/mcp/registry.py`.
- Config/secrets go through `app/config.py` (env-based settings) —
  never hardcode credentials, tokens, or connection strings anywhere.
- All workflow actions that mutate external systems (Slack messages,
  Jira tickets, calendar events, etc.) must pass through the approval flow
  in `app/services/approval.py` and be recorded via `app/services/audit.py`.
  Do not add a code path that bypasses approval or audit logging.
- New dependencies: propose them and explain why before adding to
  `pyproject.toml` — don't add packages unilaterally.

## Guardrails — Do Not

- Do not modify `docker-compose.yml`, `Dockerfile`, or DB
  migration/checkpoint schema without flagging the change explicitly and
  explaining the impact.
- Do not touch `app/mcp/policies.py` (tool access-control policy) as a
  side effect of an unrelated task — treat changes here as security-
  sensitive and call them out on their own.
- Do not commit directly to `main`. Work on a branch and stop for review
  before merging, unless explicitly told otherwise.
- Do not remove or weaken audit logging, approval gates, or observability
  instrumentation to "simplify" a fix — flag the tension instead and ask.
- Do not invent new environment variables or config without adding them
  to `app/config.py` and documenting them.

## Task Workflow

1. For anything beyond a one-line fix, outline a short plan before editing
   files (use plan mode).
2. Make scoped changes — one feature/fix per session where possible.
3. Run tests/lint before reporting done.
4. Summarize what changed and why, and flag anything that touches
   approval, audit, MCP policy, or DB checkpoint logic specifically.
