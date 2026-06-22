# DevMirror Code Coach — Devpost Submission

**GitLab Transcend Hackathon 2026 · Showcase Track (Agents, Flows, and Skills)**

---

## Inspiration

Every code review tool I'd used reviewed a diff in isolation — it could tell me a
function was long, but never that the function I just changed is called from 16
places, so I'd better write tests before merging. That *whole-codebase* awareness
is exactly what **GitLab Orbit** (the Knowledge Graph) provides. I wanted a coach
that reasons over the real dependency graph, not generic LLM guesses.

## What it does

**DevMirror Code Coach** indexes any repository with GitLab Orbit and turns the
knowledge graph into architecture-aware coaching:

- **Complexity hotspots** — which files carry the most definitions
- **Blast radius** — the most-called functions (call-graph fan-in); changing them
  is risky
- **Module coupling** — which internal modules many files import
- **Longest functions** — refactor candidates by line span

It then asks Gemini to produce a prioritized report — top risks, a refactor plan,
and a test-priority list — each grounded in real graph facts.

It runs in **four surfaces** off one Orbit core:
1. **CLI skill** (`orbit_coach.py`) — the MIT, AI-Catalog artifact
2. **CI auto-reviewer** — posts a blast-radius review on every merge request
3. **MCP server** — exposes the coach to the Duo Agent Platform / Claude Code
4. **Web dashboard** — an "Orbit Insights" page inside DevMirror

## How it uses GitLab Orbit (the mandatory requirement)

Real usage via the official `orbit` local CLI — no relabeled REST calls:

```bash
orbit index <repo>                 # build the DuckDB knowledge graph
orbit sql "SELECT ..." -F json     # query gl_definition / gl_imported_symbol / gl_edge
```

The headline query walks Orbit's `CALLS` relationships to rank functions by
fan-in — the **blast radius** signal. On this very repo it surfaces `_run`
(16 callers) and `_get_user_or_404` (15) as the riskiest functions to touch.

## How I built it

- **Orbit Local** CLI for the knowledge graph (DuckDB), queried over SQL
- **Python** client (`orbit_local_client.py`) wrapping `orbit index` / `orbit sql`
- **Gemini 2.5 Flash** for the coaching narrative
- **FastAPI** backend + **React/Vite** frontend (DevMirror)
- **GitLab CI** for the automated MR reviewer; **MCP** for agent integration

## Challenges

- The graph schema is generated at runtime from an ontology — I used `orbit schema`
  to read the real columns (e.g. `definition_type` is CamelCase: `Function`,
  `Method`) instead of guessing, which fixed empty-result queries.
- TypeScript definitions don't carry line spans in the index, so I lean on
  definition counts and the call graph for cross-language signal.
- Mapping an MR's changed files to their graph blast radius without a hosted Orbit
  Remote — solved by indexing the local checkout in CI.

## Accomplishments

A coach that gives advice no diff-only tool can: "this MR touches `coral_client.py`
which contains `_run_sql` (11 callers) — HIGH blast radius, add tests first."

## What's next

- Resolve `CALLS → ImportedSymbol` edges across files for cross-module blast radius
- Publish the skill to the GitLab AI Catalog and iterate on versions
- Per-MR Gemini narrative in CI (currently deterministic table)

## Built with

`gitlab-orbit` · `knowledge-graph` · `duckdb` · `python` · `gemini` · `fastapi` ·
`react` · `gitlab-ci` · `mcp`

## Links

- **Repo:** https://github.com/YashasviThakur/devmirrorhackathon
- **Write-up:** [GITLAB_TRANSCEND.md](GITLAB_TRANSCEND.md)
- **Demo script:** [DEMO_SCRIPT.md](DEMO_SCRIPT.md)
