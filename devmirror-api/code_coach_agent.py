"""
DevMirror Code Coach Agent — AI-powered code analysis grounded in REAL code.

Two capabilities:
  • analyze_merge_request — fetches the actual MR diff (not just metadata) and
    reviews the real changed code with Gemini.
  • find_technical_debt   — fetches real source files from the repository and
    analyses them for genuine debt signals, instead of guessing from commit counts.

Both accept an optional ``orbit_context`` dict produced by ``orbit_local_client``
(GitLab Orbit / Knowledge Graph). When present, the structural graph context
(definitions, cross-file references, blast radius, hotspots) is fed to the model
so the review is architecture-aware — the core promise of the hackathon.

GitLab REST API v4 reference: https://docs.gitlab.com/api/merge_requests/
"""

import logging
from typing import Any, Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

GITLAB_API = "https://gitlab.com/api/v4"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

# Keep prompts within sane token budgets.
_MAX_DIFF_FILES = 12
_MAX_DIFF_CHARS = 12_000
_MAX_DEBT_FILES = 6
_MAX_FILE_CHARS = 4_000
_SOURCE_EXTS = (
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb",
    ".kt", ".c", ".cpp", ".h", ".cs", ".php", ".swift", ".scala",
)


# ── GitLab helpers ───────────────────────────────────────────────────────────

def _headers(token: str) -> dict:
    return {"PRIVATE-TOKEN": token}


def _get(path: str, token: str, **params) -> Optional[requests.Response]:
    try:
        resp = requests.get(
            f"{GITLAB_API}{path}", headers=_headers(token), params=params, timeout=15
        )
        return resp
    except Exception as e:
        logger.error(f"GitLab GET {path} failed: {e}")
        return None


def _default_branch(project_id: int, token: str) -> str:
    resp = _get(f"/projects/{project_id}", token)
    if resp is not None and resp.status_code == 200:
        return resp.json().get("default_branch") or "main"
    return "main"


def _fetch_mr_diff(project_id: int, mr_iid: int, token: str) -> Optional[dict]:
    """Return MR metadata + the real per-file diffs."""
    base = _get(f"/projects/{project_id}/merge_requests/{mr_iid}", token)
    if base is None or base.status_code != 200:
        return None
    mr = base.json()

    # /changes carries the actual diff hunks. Fall back to /diffs (newer API).
    changes_resp = _get(f"/projects/{project_id}/merge_requests/{mr_iid}/changes", token)
    changes: list[dict] = []
    if changes_resp is not None and changes_resp.status_code == 200:
        changes = changes_resp.json().get("changes", []) or []
    else:
        diffs_resp = _get(f"/projects/{project_id}/merge_requests/{mr_iid}/diffs", token)
        if diffs_resp is not None and diffs_resp.status_code == 200:
            changes = diffs_resp.json() or []

    return {"mr": mr, "changes": changes}


def _render_diff(changes: list[dict]) -> tuple[str, int]:
    """Render changed files into a capped textual diff for the model."""
    chunks: list[str] = []
    used = 0
    shown = 0
    for ch in changes[:_MAX_DIFF_FILES]:
        path = ch.get("new_path") or ch.get("old_path") or "unknown"
        diff = ch.get("diff", "") or ""
        if not diff:
            continue
        remaining = _MAX_DIFF_CHARS - used
        if remaining <= 0:
            break
        snippet = diff[:remaining]
        chunks.append(f"--- {path}\n{snippet}")
        used += len(snippet)
        shown += 1
    return "\n\n".join(chunks), shown


def _list_source_files(project_id: int, token: str, branch: str) -> list[str]:
    resp = _get(
        f"/projects/{project_id}/repository/tree",
        token, ref=branch, recursive=True, per_page=100,
    )
    if resp is None or resp.status_code != 200:
        return []
    files = [
        item.get("path", "")
        for item in resp.json()
        if item.get("type") == "blob" and item.get("path", "").endswith(_SOURCE_EXTS)
    ]
    return files


def _fetch_file(project_id: int, path: str, token: str, branch: str) -> str:
    enc = quote(path, safe="")
    resp = _get(
        f"/projects/{project_id}/repository/files/{enc}/raw", token, ref=branch
    )
    if resp is None or resp.status_code != 200:
        return ""
    return resp.text[:_MAX_FILE_CHARS]


# ── Gemini ───────────────────────────────────────────────────────────────────

def _gemini(prompt: str, gemini_key: str, max_tokens: int = 900) -> Optional[str]:
    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            params={"key": gemini_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": max_tokens},
            },
            timeout=30,
        )
        if resp.status_code != 200:
            logger.error(f"Gemini error {resp.status_code}: {resp.text[:200]}")
            return None
        return (
            resp.json().get("candidates", [{}])[0]
            .get("content", {}).get("parts", [{}])[0].get("text", "")
        )
    except Exception as e:
        logger.error(f"Gemini call failed: {e}")
        return None


def _orbit_block(orbit_context: Optional[dict]) -> str:
    """Render Orbit graph context into the prompt, if available."""
    if not orbit_context or not orbit_context.get("available"):
        return ""
    lines = ["", "GitLab Orbit knowledge-graph context (use this to ground your review):"]
    summary = orbit_context.get("summary")
    if summary:
        lines.append(summary)
    for key in ("hotspots", "blast_radius", "dependencies"):
        rows = orbit_context.get(key)
        if rows:
            lines.append(f"\n{key.replace('_', ' ').title()}:")
            for r in rows[:10]:
                lines.append(f"  - {r}")
    return "\n".join(lines)


# ── Capabilities ─────────────────────────────────────────────────────────────

def analyze_merge_request(
    project_id: int,
    mr_iid: int,
    gitlab_token: str,
    gemini_key: str,
    orbit_context: Optional[dict] = None,
) -> dict[str, Any]:
    """Review a merge request using its REAL diff (+ optional Orbit context)."""
    if not gitlab_token or not gemini_key:
        return {"success": False, "error": "Missing GitLab token or Gemini API key"}

    data = _fetch_mr_diff(project_id, mr_iid, gitlab_token)
    if data is None:
        return {"success": False, "error": "Failed to fetch merge request"}

    mr = data["mr"]
    diff_text, files_shown = _render_diff(data["changes"])
    if not diff_text:
        return {"success": False, "error": "No diff content available for this MR"}

    prompt = f"""You are an expert code reviewer. Review the ACTUAL diff below.

Merge Request: {mr.get('title', '')}
Author: {mr.get('author', {}).get('name', '')}
Description: {(mr.get('description') or '')[:600]}
{_orbit_block(orbit_context)}

=== DIFF ({files_shown} file(s)) ===
{diff_text}
=== END DIFF ===

Base your review ONLY on the code shown. Provide:
1. Code Quality Score (1-10) with one-line justification
2. Specific issues — cite the file and what's wrong (bugs, edge cases, naming, duplication)
3. Risk factors for merging
4. One concrete next action

Be specific and reference real lines/identifiers from the diff. Under 320 words."""

    analysis = _gemini(prompt, gemini_key)
    if analysis is None:
        return {"success": False, "error": "Gemini analysis failed"}

    return {
        "success": True,
        "mr_title": mr.get("title", ""),
        "mr_author": mr.get("author", {}).get("name", ""),
        "changes": {
            "additions": mr.get("additions", 0),
            "deletions": mr.get("deletions", 0),
            "files_changed": len(data["changes"]),
            "files_analyzed": files_shown,
        },
        "orbit_powered": bool(orbit_context and orbit_context.get("available")),
        "ai_analysis": analysis,
        "mr_url": mr.get("web_url", ""),
    }


def find_technical_debt(
    project_id: int,
    gitlab_token: str,
    gemini_key: str,
    orbit_context: Optional[dict] = None,
) -> dict[str, Any]:
    """Scan REAL source files for technical debt (+ optional Orbit hotspots)."""
    if not gitlab_token or not gemini_key:
        return {"success": False, "error": "Missing credentials"}

    branch = _default_branch(project_id, gitlab_token)
    files = _list_source_files(project_id, gitlab_token, branch)
    if not files:
        return {"success": False, "error": "No source files found to analyse"}

    # Prefer Orbit-identified hotspots; otherwise sample the listed files.
    targets: list[str] = []
    if orbit_context and orbit_context.get("available"):
        for row in orbit_context.get("hotspots", []):
            path = row.get("path") if isinstance(row, dict) else str(row)
            if path in files:
                targets.append(path)
    for f in files:
        if f not in targets:
            targets.append(f)
    targets = targets[:_MAX_DEBT_FILES]

    sources: list[str] = []
    for path in targets:
        content = _fetch_file(project_id, path, gitlab_token, branch)
        if content:
            sources.append(f"### FILE: {path}\n{content}")

    if not sources:
        return {"success": False, "error": "Could not read any source files"}

    code_blob = "\n\n".join(sources)
    prompt = f"""You are a senior engineer auditing real code for technical debt.
{_orbit_block(orbit_context)}

Below are {len(sources)} real source file(s) from the project:

{code_blob}

For the code ABOVE (cite specific files/functions), identify:
1. Complexity hotspots — overly long/nested functions, with the file name
2. Testing gaps — untested critical paths you can infer
3. Documentation debt — missing/misleading docs
4. Duplication & dead code
5. Performance or correctness risks

For each finding: the file, why it matters, and a concrete first step.
Ground every point in the actual code shown. Under 420 words."""

    debt = _gemini(prompt, gemini_key, max_tokens=1100)
    if debt is None:
        return {"success": False, "error": "Gemini analysis failed"}

    return {
        "success": True,
        "project_id": project_id,
        "branch": branch,
        "files_analyzed": [s.split("\n", 1)[0].replace("### FILE: ", "") for s in sources],
        "orbit_powered": bool(orbit_context and orbit_context.get("available")),
        "debt_analysis": debt,
    }
