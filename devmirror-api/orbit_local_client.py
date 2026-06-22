"""
DevMirror — GitLab Orbit (Knowledge Graph) client.

REAL GitLab Orbit usage via the official `orbit` CLI (Orbit Local). Orbit indexes
a repository into a structured, queryable knowledge graph (DuckDB) and exposes it
over SQL — giving an AI agent architecture-aware context instead of guesses.

    orbit index <repo>          build the local knowledge graph
    orbit sql "<SQL>" -F json   read-only SQL over the graph
    orbit schema                describe the graph

Graph tables (verified against orbit 0.78):
    gl_file            (path, name, extension, language, project_id, ...)
    gl_definition      (file_path, name, definition_type, start_line, end_line, fqn, ...)
    gl_imported_symbol (file_path, import_path, identifier_name, import_type, ...)
    gl_edge            (source_id, source_kind, relationship_kind, target_id, target_kind)

Docs: https://docs.gitlab.com/orbit/   Repo: gitlab-org/orbit/knowledge-graph
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
from typing import Any, Optional

logger = logging.getLogger(__name__)

# definition_type values Orbit emits for callable definitions (CamelCase).
_FUNC_TYPES = (
    "Function", "AsyncFunction", "DecoratedFunction",
    "DecoratedAsyncFunction", "Method",
)


# ── CLI plumbing ─────────────────────────────────────────────────────────────

def _orbit_bin() -> Optional[str]:
    """Locate the orbit binary on PATH or in the default install dir."""
    found = shutil.which("orbit")
    if found:
        return found
    candidates = []
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.append(os.path.join(local, "Programs", "orbit", "orbit.exe"))
    candidates += [
        "/usr/local/bin/orbit",
        os.path.expanduser("~/.local/bin/orbit"),
        os.path.expanduser("~/.orbit/bin/orbit"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def is_available() -> bool:
    return _orbit_bin() is not None


def _exec(args: list[str], timeout: int = 120) -> Optional[subprocess.CompletedProcess]:
    binary = _orbit_bin()
    if not binary:
        return None
    try:
        return subprocess.run(
            [binary, *args], capture_output=True, text=True, timeout=timeout
        )
    except Exception as e:
        logger.error(f"orbit {args[:1]} failed: {e}")
        return None


def index_repo(repo_path: str, timeout: int = 300) -> Optional[dict]:
    """Build/refresh the Orbit knowledge graph for a local repository."""
    res = _exec(["index", repo_path], timeout=timeout)
    if not res or res.returncode != 0:
        logger.warning(f"orbit index failed: {getattr(res, 'stderr', '(no binary)')}")
        return None
    try:
        return json.loads(res.stdout)
    except Exception:
        return {"indexed": True}


def sql(query: str, timeout: int = 60) -> list[dict]:
    """Run a read-only SQL query against the Orbit graph; return rows as dicts."""
    res = _exec(["sql", query, "-F", "json"], timeout=timeout)
    if not res or res.returncode != 0:
        if res:
            logger.warning(f"orbit sql error: {res.stderr[:200]}")
        return []
    try:
        data = json.loads(res.stdout or "[]")
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"orbit sql parse failed: {e}")
        return []


def _project_id(repo_path: str) -> Optional[int]:
    """Resolve the project_id Orbit assigned to a repo, for query scoping."""
    safe = repo_path.replace("'", "''")
    rows = sql(f"SELECT project_id FROM _orbit_manifest WHERE repo_path = '{safe}' LIMIT 1")
    if rows and rows[0].get("project_id") is not None:
        return int(rows[0]["project_id"])
    return None


def _scope(pid: Optional[int], alias: str = "") -> str:
    """Build an optional project_id predicate (alias-aware for joins)."""
    if pid is None:
        return ""
    col = f"{alias}.project_id" if alias else "project_id"
    return f"{col} = {int(pid)}"


# ── Analysis queries (verified on real graph data) ───────────────────────────

def hotspots(pid: Optional[int] = None, limit: int = 8) -> list[dict]:
    """Files with the most definitions — complexity density proxy."""
    where = _scope(pid)
    where = f"WHERE {where} " if where else ""
    return sql(
        f"SELECT file_path, COUNT(*) AS definitions FROM gl_definition "
        f"{where}GROUP BY 1 ORDER BY 2 DESC LIMIT {int(limit)}"
    )


def longest_functions(pid: Optional[int] = None, limit: int = 8) -> list[dict]:
    """Longest callable definitions by line span (refactor candidates)."""
    types = ", ".join(f"'{t}'" for t in _FUNC_TYPES)
    scope = _scope(pid)
    scope = f"AND {scope} " if scope else ""
    return sql(
        f"SELECT file_path, name, (end_line - start_line) AS span FROM gl_definition "
        f"WHERE definition_type IN ({types}) AND end_line > start_line {scope}"
        f"ORDER BY span DESC LIMIT {int(limit)}"
    )


def blast_radius(pid: Optional[int] = None, limit: int = 8) -> list[dict]:
    """Most-called definitions (fan-in) — highest blast radius if changed."""
    scope = _scope(pid, alias="d")
    scope = f"AND {scope} " if scope else ""
    return sql(
        "SELECT d.file_path, d.name, COUNT(*) AS callers "
        "FROM gl_edge e JOIN gl_definition d ON e.target_id = d.id "
        "WHERE e.relationship_kind = 'CALLS' AND e.target_kind = 'Definition' "
        f"{scope}GROUP BY 1, 2 ORDER BY 3 DESC LIMIT {int(limit)}"
    )


def module_coupling(pid: Optional[int] = None, limit: int = 8) -> list[dict]:
    """Internal modules imported by the most files — coupling hotspots."""
    scope = _scope(pid)
    scope = f"AND {scope} " if scope else ""
    return sql(
        "SELECT import_path, COUNT(DISTINCT file_path) AS importers "
        f"FROM gl_imported_symbol WHERE import_path LIKE '.%' {scope}"
        f"GROUP BY 1 ORDER BY 2 DESC LIMIT {int(limit)}"
    )


def importers_of(file_path: str, pid: Optional[int] = None, limit: int = 25) -> list[str]:
    """Files that import a given file (module-level blast radius)."""
    stem = re.sub(r"[^A-Za-z0-9_.\-]", "", os.path.splitext(os.path.basename(file_path))[0])
    if not stem:
        return []
    scope = _scope(pid)
    scope = f"AND {scope} " if scope else ""
    rows = sql(
        "SELECT DISTINCT file_path FROM gl_imported_symbol "
        f"WHERE (import_path LIKE '%/{stem}' OR import_path LIKE '%{stem}') {scope}"
        f"LIMIT {int(limit)}"
    )
    return [r["file_path"] for r in rows]


def _hot_defs_in_file(file_path: str, pid: Optional[int] = None, limit: int = 3) -> list[dict]:
    """Most-called definitions inside a specific file (local fan-in)."""
    safe = file_path.replace("'", "''")
    scope = _scope(pid, alias="d")
    scope = f"AND {scope} " if scope else ""
    return sql(
        "SELECT d.name, COUNT(*) AS callers "
        "FROM gl_edge e JOIN gl_definition d ON e.target_id = d.id "
        "WHERE e.relationship_kind = 'CALLS' AND e.target_kind = 'Definition' "
        f"AND d.file_path = '{safe}' {scope}"
        f"GROUP BY 1 ORDER BY 2 DESC LIMIT {int(limit)}"
    )


def _def_count(file_path: str, pid: Optional[int] = None) -> int:
    safe = file_path.replace("'", "''")
    where = f"AND project_id = {int(pid)}" if pid is not None else ""
    rows = sql(f"SELECT COUNT(*) AS n FROM gl_definition WHERE file_path = '{safe}' {where}")
    return int(rows[0]["n"]) if rows else 0


def impact_of_changed_files(paths: list[str], pid: Optional[int] = None) -> list[dict]:
    """
    For each changed file, compute its blast radius from the Orbit graph:
    how many files import it, the most-called functions it defines, and a
    derived risk level. This is what makes MR review architecture-aware.
    """
    results: list[dict] = []
    for path in paths:
        importers = importers_of(path, pid=pid, limit=50)
        hot = _hot_defs_in_file(path, pid=pid, limit=3)
        max_callers = max((int(d.get("callers", 0)) for d in hot), default=0)
        n_importers = len(importers)
        # Simple, explainable risk score from real graph fan-in.
        score = n_importers + max_callers
        risk = "HIGH" if score >= 12 else "MEDIUM" if score >= 5 else "LOW"
        results.append({
            "file": path,
            "risk": risk,
            "importer_count": n_importers,
            "importers": importers[:10],
            "hot_definitions": hot,
            "definitions": _def_count(path, pid=pid),
        })
    # Riskiest first.
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    results.sort(key=lambda r: (order[r["risk"]], -r["importer_count"]))
    return results


def graph_stats(pid: Optional[int] = None) -> dict[str, int]:
    out: dict[str, int] = {}
    for table in ("gl_file", "gl_definition", "gl_imported_symbol", "gl_edge"):
        where = ""
        if pid is not None and table != "gl_edge":  # gl_edge has no project_id column
            where = f" WHERE project_id = {int(pid)}"
        rows = sql(f"SELECT COUNT(*) AS n FROM {table}{where}")
        out[table] = int(rows[0]["n"]) if rows else 0
    return out


# ── High-level context builder (consumed by code_coach_agent) ────────────────

def build_context(repo_path: Optional[str] = None, do_index: bool = True, top: int = 8) -> dict[str, Any]:
    """
    Produce architecture-aware context for the Code Coach.

    Returns a dict with ``available`` plus human-readable ``summary``,
    ``hotspots``, ``blast_radius``, ``dependencies`` and ``long_functions``
    lines, and the underlying ``raw`` rows.
    """
    if not is_available():
        return {"available": False, "detail": "orbit CLI not installed"}

    if repo_path and do_index:
        index_repo(repo_path)

    pid = _project_id(repo_path) if repo_path else None
    stats = graph_stats(pid)
    if not stats.get("gl_definition"):
        return {"available": False, "detail": "no graph data — index a repo first"}

    hot = hotspots(pid, top)
    fanin = blast_radius(pid, top)
    coup = module_coupling(pid, top)
    longf = longest_functions(pid, top)

    summary = (
        f"Orbit knowledge graph: {stats['gl_file']} files, "
        f"{stats['gl_definition']} definitions, "
        f"{stats['gl_imported_symbol']} imports, {stats['gl_edge']} edges."
    )

    return {
        "available": True,
        "summary": summary,
        "stats": stats,
        "hotspots": [f"{r['file_path']} — {r['definitions']} definitions" for r in hot],
        "blast_radius": [
            f"{r['name']} ({r['file_path']}) — {r['callers']} callers" for r in fanin
        ],
        "dependencies": [
            f"{r['import_path']} — imported by {r['importers']} files" for r in coup
        ],
        "long_functions": [
            f"{r['name']} ({r['file_path']}) — {r['span']} lines" for r in longf
        ],
        "raw": {
            "hotspots": hot, "blast_radius": fanin,
            "coupling": coup, "long_functions": longf,
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(build_context(path), indent=2))
