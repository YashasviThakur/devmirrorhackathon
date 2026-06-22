# DevMirror Code Coach — GitLab Transcend Hackathon 2026

**Track:** Showcase (Agents, Flows, and Skills) · **Deadline:** June 24, 2026

> An architecture-aware code coach that uses the **GitLab Orbit knowledge graph**
> for real — it indexes a repository with Orbit, queries the graph for structural
> signals, and grounds every recommendation in the project's actual dependency
> structure instead of generic LLM guesses.

---

## Why this uses Orbit *meaningfully*

The hackathon's one mandatory requirement is to use **GitLab Orbit** — the
queryable knowledge graph of a codebase. This skill does exactly that via the
official Orbit local CLI:

```bash
orbit index <repo>                       # build the DuckDB knowledge graph
orbit sql "<SQL>" -F json                # read-only SQL over the graph
orbit schema                             # inspect the generated schema
orbit mcp                                # (also) serve the graph over MCP
```

It queries four Orbit graph tables — `gl_definition`, `gl_imported_symbol`,
`gl_edge`, `gl_file` — to compute signals a context-free LLM cannot:

| Signal | What it answers | Orbit query (abridged) |
|---|---|---|
| **Complexity hotspots** | Which files carry the most definitions | `SELECT file_path, COUNT(*) FROM gl_definition GROUP BY 1` |
| **Blast radius** | Which functions are most-called (riskiest to change) | `JOIN gl_edge … WHERE relationship_kind='CALLS'` (call-graph fan-in) |
| **Module coupling** | Which internal modules many files import | `SELECT import_path, COUNT(DISTINCT file_path) FROM gl_imported_symbol` |
| **Longest functions** | Refactor candidates by line span | `SELECT name, end_line-start_line FROM gl_definition WHERE definition_type IN (…)` |

The **blast radius** signal is the headline: it walks Orbit's `CALLS`
relationships (`Definition → Definition`) to rank functions by how many call
sites depend on them. That is the kind of whole-codebase structural reasoning
Orbit exists to provide.

---

## What it produces (real output on this repo)

```
Orbit knowledge graph: 62 files, 864 definitions, 424 imports, 2248 edges.

── Highest blast radius (fan-in) ──────────────────────────
   • _run (devmirror-api/main.py) — 16 callers
   • _get_user_or_404 (devmirror-api/main.py) — 15 callers
   • _run_sql (devmirror-api/coral_client.py) — 11 callers

── Longest functions ──────────────────────────────────────
   • focus_compat (devmirror-api/main.py) — 189 lines
   • lvb_compat (devmirror-api/main.py) — 149 lines
   • run_agent (devmirror-api/agent_tools.py) — 127 lines
```

Gemini then reasons over these *real* facts to produce prioritized risks, a
refactor plan, and a test-priority list — each citing actual files/functions.

---

## Architecture

```
devmirror-api/
├── orbit_local_client.py   ← REAL GitLab Orbit client (index + SQL over the graph)
├── orbit_coach.py          ← the skill entrypoint (Orbit → Gemini coaching report)
├── code_coach_agent.py     ← MR review on the real diff + Orbit context
├── agent_tools.py          ← `fetch_gitlab_orbit` agent tool (Orbit-backed)
└── main.py                 ← FastAPI endpoints wire Orbit into the app
```

- **`/api/coach/analyze-mr`** — reviews a merge request's *actual diff*, grounded
  in Orbit graph context.
- **`/api/coach/find-debt`** — audits *real source files*, prioritized by Orbit
  hotspots.
- **`/api/data/gitlab/orbit`** — returns the live Orbit knowledge-graph context.
- **Agent tool `fetch_gitlab_orbit`** — lets the DevMirror Gemini agent pull
  Orbit context inside a coaching conversation.

Every Orbit path degrades gracefully: if the `orbit` CLI/graph isn't present, the
app still works (MR review falls back to diff-only analysis).

---

## Run it

```bash
# 1. Install GitLab Orbit (local CLI)
#    https://docs.gitlab.com/orbit/   (Windows: install.ps1, macOS/Linux: install.sh)

# 2. Run the skill on any repo
cd devmirror-api
python orbit_coach.py /path/to/repo --top 8

#    Add the AI narrative:
export GEMINI_API_KEY=...        # PowerShell: $env:GEMINI_API_KEY="..."
python orbit_coach.py /path/to/repo
```

No GitLab.com project or hosted Orbit Remote required — Orbit Local builds the
graph from any repository on disk.

---

## AI Catalog artifact

- **`skill.yml`** / **`manifest.json`** — MIT-licensed skill definition for the
  GitLab Duo Agent Platform / AI Catalog, describing the Orbit queries, the
  `orbit_coach.py` entrypoint, and the three capabilities.
- The graph is also **MCP-compatible** (`orbit mcp`), so the same context is
  available to Duo Agent Platform and external agents.

---

## How it maps to the judging criteria

- **Technological Implementation** — real Orbit graph queries (call-graph fan-in,
  coupling), not relabeled REST calls; graceful fallbacks; verified schema.
- **Design & Usability** — one command produces a prioritized, readable report;
  embedded in the DevMirror web app's AI Coach.
- **Potential Impact** — blast-radius-aware review and test prioritization scale
  to any codebase Orbit can index.
- **Quality of the idea** — coaching grounded in the *actual* dependency graph is
  exactly what Orbit unlocks over generic LLM review.

---

*Author: Yashasvi Thakur · github.com/YashasviThakur · Submitted for GitLab Transcend 2026 (Showcase Track)*
