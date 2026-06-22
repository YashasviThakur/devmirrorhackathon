# Publishing the Code Coach to the GitLab AI Catalog

The Showcase track requires at least one artifact published to the **AI Catalog**
(open source, MIT). This repo provides the source artifact (`skill.yml`,
`manifest.json`, `orbit_coach.py`); the AI Catalog itself is registered through
the **GitLab Duo Agent Platform UI**.

> Docs: https://docs.gitlab.com/user/duo_agent_platform/ai_catalog/

## What we publish

The **DevMirror Code Coach** — an agent/flow that uses GitLab Orbit to analyse a
codebase and return prioritized, blast-radius-aware coaching. License: **MIT**.

## Steps

1. **Open the AI Catalog**
   In GitLab: **Search/Go to → your group → Automate → AI Catalog** (or the Duo
   Agent Platform area). You need Duo Agent Platform enabled for the group.

2. **Create the item**
   Choose **New agent** (for the coaching agent) or **New flow** (for the CI-style
   automated reviewer). Provide:
   - **Name:** `DevMirror Code Coach (GitLab Orbit)` — specific, includes purpose
   - **Description:** "Architecture-aware code coaching from the GitLab Orbit
     knowledge graph: complexity hotspots, blast radius, coupling, and a
     prioritized refactor/test plan."

3. **Point it at this project / configure it**
   - Repo: `https://github.com/YashasviThakur/devmirrorhackathon`
   - Entry point: `devmirror-api/orbit_coach.py`
   - Prereqs (document in the item): GitLab Orbit CLI installed; optional
     `GEMINI_API_KEY` for the AI narrative.
   - Orbit is also MCP-exposed via `orbit_mcp_server.py` for Duo agents.

4. **Add use cases & examples**
   Include the sample output from `GITLAB_TRANSCEND.md` (hotspots + blast radius).

5. **Publish**
   Start **Private** to validate with the team, then switch to **Public** so it's
   discoverable. GitLab auto-versions the item when you change its prompt/config.

## Checklist (for the submission)
- [ ] MIT `LICENSE` present at repo root ✅ (already in repo)
- [ ] `skill.yml` + `manifest.json` accurate ✅
- [ ] AI Catalog item created and set to **Public**
- [ ] Item links back to this public repo
- [ ] Description includes purpose, use cases, and prerequisites
