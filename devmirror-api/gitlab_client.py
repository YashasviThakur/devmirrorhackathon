"""
DevMirror — GitLab REST API client.
Fetches projects, commits, merge requests, and contribution stats.
Uses the GitLab REST API v4 — no extra dependencies beyond requests.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

GITLAB_BASE = "https://gitlab.com/api/v4"


def _headers(token: str) -> dict:
    return {"PRIVATE-TOKEN": token, "Accept": "application/json"}


# ── User info ──────────────────────────────────────────────────────────────────

def get_user_info(username: str, token: str) -> Optional[dict]:
    try:
        resp = requests.get(
            f"{GITLAB_BASE}/users",
            headers=_headers(token),
            params={"username": username},
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        results = resp.json()
        return results[0] if results else None
    except Exception as e:
        logger.error(f"GitLab get_user_info failed: {e}")
        return None


# ── Projects ───────────────────────────────────────────────────────────────────

def get_projects(user_id: int, token: str, per_page: int = 20) -> list[dict]:
    try:
        resp = requests.get(
            f"{GITLAB_BASE}/users/{user_id}/projects",
            headers=_headers(token),
            params={
                "per_page":   per_page,
                "order_by":   "last_activity_at",
                "sort":       "desc",
                "visibility": "public",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        return resp.json()
    except Exception as e:
        logger.error(f"GitLab get_projects failed: {e}")
        return []


# ── Commits this week ──────────────────────────────────────────────────────────

def get_recent_commits(user_id: int, token: str, projects: list[dict]) -> int:
    """Count commits across all projects in the past 7 days."""
    since = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
    total = 0
    for project in projects[:10]:
        pid = project.get("id")
        try:
            resp = requests.get(
                f"{GITLAB_BASE}/projects/{pid}/repository/commits",
                headers=_headers(token),
                params={"since": since, "per_page": 100},
                timeout=8,
            )
            if resp.status_code == 200:
                total += len(resp.json())
        except Exception:
            continue
    return total


# ── Merge requests ─────────────────────────────────────────────────────────────

def get_merge_requests(user_id: int, token: str, state: str = "opened") -> list[dict]:
    try:
        resp = requests.get(
            f"{GITLAB_BASE}/merge_requests",
            headers=_headers(token),
            params={
                "scope":    "created_by_me",
                "state":    state,
                "per_page": 10,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        mrs = resp.json()
        return [
            {
                "title":      mr.get("title", ""),
                "state":      mr.get("state", ""),
                "project":    mr.get("references", {}).get("full", ""),
                "created_at": mr.get("created_at", "")[:10],
                "web_url":    mr.get("web_url", ""),
            }
            for mr in mrs
        ]
    except Exception as e:
        logger.error(f"GitLab get_merge_requests failed: {e}")
        return []


# ── Full fetch ─────────────────────────────────────────────────────────────────

def fetch_gitlab(username: str, token: str) -> dict[str, Any]:
    """
    Full GitLab data fetch: user info + projects + commits this week + open MRs.
    Returns a structured dict compatible with the /api/data/gitlab endpoint.
    """
    if not username or not token:
        return _empty_gitlab(username)

    user_info = get_user_info(username, token)
    if not user_info:
        return _empty_gitlab(username)

    gl_user_id = user_info.get("id")
    projects   = get_projects(gl_user_id, token)
    commits_week = get_recent_commits(gl_user_id, token, projects)
    open_mrs   = get_merge_requests(gl_user_id, token, state="opened")

    top_project = projects[0].get("name", "") if projects else ""
    languages: list[str] = []
    seen: set[str] = set()
    for p in projects[:8]:
        lang = p.get("predominant_language") or p.get("language", "")
        if lang and lang not in seen:
            languages.append(lang)
            seen.add(lang)

    return {
        "username":      username,
        "name":          user_info.get("name", username),
        "avatar_url":    user_info.get("avatar_url", ""),
        "profile_url":   user_info.get("web_url", f"https://gitlab.com/{username}"),
        "total_projects": len(projects),
        "commits_week":  commits_week,
        "top_project":   top_project,
        "languages":     languages[:5],
        "open_mrs":      len(open_mrs),
        "recent_mrs":    open_mrs[:5],
        "projects":      [
            {
                "name":              p.get("name", ""),
                "description":       (p.get("description") or "")[:100],
                "stars":             p.get("star_count", 0),
                "forks":             p.get("forks_count", 0),
                "last_activity":     (p.get("last_activity_at") or "")[:10],
                "web_url":           p.get("web_url", ""),
            }
            for p in projects[:8]
        ],
    }


def _empty_gitlab(username: str) -> dict[str, Any]:
    return {
        "username":       username,
        "name":           username,
        "avatar_url":     "",
        "profile_url":    f"https://gitlab.com/{username}",
        "total_projects": 0,
        "commits_week":   0,
        "top_project":    "",
        "languages":      [],
        "open_mrs":       0,
        "recent_mrs":     [],
        "projects":       [],
    }
