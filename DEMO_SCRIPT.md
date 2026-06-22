# Demo Script — DevMirror Code Coach (≈2 minutes)

Goal: prove **real GitLab Orbit usage** and the architecture-aware payoff, fast.

---

### 0:00 — Hook (15s)
> "Every code review tool judges a diff in isolation. Mine reads the whole
> dependency graph with **GitLab Orbit** — so it knows the function you just
> changed has 16 callers, and tells you to test it before merging."

### 0:15 — Orbit is real (25s)
Terminal:
```bash
orbit index .          # builds the knowledge graph
orbit schema           # show the real gl_* tables
orbit sql "SELECT file_path, COUNT(*) FROM gl_definition GROUP BY 1 ORDER BY 2 DESC LIMIT 5" -F json
```
> "This is the actual Orbit CLI and the actual graph — not relabeled REST calls."

### 0:40 — The skill (35s)
```bash
python orbit_coach.py . --top 8
```
Point at the output:
> "Hotspots, **blast radius** from the call graph — `_run`, 16 callers — coupling,
> longest functions. Then Gemini turns that into prioritized coaching."

### 1:15 — Automated MR review (25s)
Open a merge request in GitLab; show the CI-posted comment:
> "On every MR, a CI job indexes with Orbit and posts the blast radius of the
> changed files. `coral_client.py` → HIGH risk, `_run_sql` has 11 callers."
(`.gitlab-ci.yml` + `ci/orbit_mr_review.py`)

### 1:40 — Where it lives (15s)
Show the **Orbit Insights** page in DevMirror + mention the **MCP server**:
> "Same Orbit core, four surfaces: CLI skill, CI, MCP for Duo Agent Platform, and
> this dashboard."

### 1:55 — Close (5s)
> "Coaching grounded in the real architecture — that's what Orbit unlocks."

---

## Pre-demo checklist
- [ ] `orbit --help` works (CLI installed)
- [ ] `GEMINI_API_KEY` set (for the AI narrative)
- [ ] Repo indexed once (`orbit index .`)
- [ ] A sample MR open with `GITLAB_TOKEN` CI variable set (for the CI comment)
- [ ] Backend running for the Orbit Insights page (`uvicorn main:app`)
