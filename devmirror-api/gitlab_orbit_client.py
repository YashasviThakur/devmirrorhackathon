"""
DevMirror — GitLab Orbit API client.
Fetches structured codebase context from GitLab Orbit.
Enables AI agents to understand code structure, dependencies, and complexity.
"""

import os
import logging
from typing import Any, Optional
import requests

logger = logging.getLogger(__name__)

GITLAB_ORBIT_BASE = "https://gitlab.com/api/graphql"


def _headers(token: str) -> dict:
    return {
        "PRIVATE-TOKEN": token,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_project_context(project_id: int, token: str) -> Optional[dict]:
    """Fetch project context from GitLab Orbit GraphQL API."""
    if not token:
        return None

    query = """
    query {
      project(id: "%d") {
        id
        name
        description
        repository {
          blobs {
            nodes {
              name
              path
              size
            }
          }
        }
        statistics {
          commitCount
          forkCount
          starCount
        }
      }
    }
    """ % project_id

    try:
        resp = requests.post(
            GITLAB_ORBIT_BASE,
            headers=_headers(token),
            json={"query": query},
            timeout=15,
        )
        if resp.status_code != 200:
            logger.warning(f"GitLab Orbit query failed: {resp.status_code}")
            return None
        data = resp.json()
        if "errors" in data:
            logger.warning(f"GitLab Orbit GraphQL error: {data['errors']}")
            return None
        return data.get("data", {}).get("project")
    except Exception as e:
        logger.error(f"GitLab Orbit get_project_context failed: {e}")
        return None


def analyze_code_complexity(project_id: int, file_path: str, token: str) -> Optional[dict]:
    """Analyze code complexity for a specific file."""
    if not token:
        return None

    try:
        # Fetch file content via REST API
        resp = requests.get(
            f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/{file_path.replace('/', '%2F')}",
            headers={"PRIVATE-TOKEN": token},
            params={"ref": "main"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None

        file_data = resp.json()
        content = file_data.get("content", "")

        # Basic complexity heuristics
        lines = content.split("\n")
        functions = [l for l in lines if l.strip().startswith("def ")]
        classes = [l for l in lines if l.strip().startswith("class ")]
        imports = [l for l in lines if l.strip().startswith("import ")]

        return {
            "file": file_path,
            "lines_of_code": len(lines),
            "function_count": len(functions),
            "class_count": len(classes),
            "import_count": len(imports),
            "complexity_score": (len(functions) + len(classes) * 2) / max(len(lines) / 100, 1),
        }
    except Exception as e:
        logger.error(f"Code complexity analysis failed: {e}")
        return None


def get_merge_request_context(
    project_id: int, mr_iid: int, token: str
) -> Optional[dict]:
    """Fetch MR context with changed files and diff stats."""
    if not token:
        return None

    try:
        resp = requests.get(
            f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}",
            headers={"PRIVATE-TOKEN": token},
            timeout=10,
        )
        if resp.status_code != 200:
            return None

        mr_data = resp.json()
        return {
            "title": mr_data.get("title", ""),
            "description": mr_data.get("description", "")[:500],
            "state": mr_data.get("state", ""),
            "changes_count": mr_data.get("changes_count", 0),
            "additions": mr_data.get("additions", 0),
            "deletions": mr_data.get("deletions", 0),
            "author": mr_data.get("author", {}).get("name", ""),
            "created_at": (mr_data.get("created_at") or "")[:10],
            "web_url": mr_data.get("web_url", ""),
        }
    except Exception as e:
        logger.error(f"GitLab Orbit get_merge_request_context failed: {e}")
        return None


def fetch_orbit_context(project_id: int, token: str) -> dict[str, Any]:
    """Fetch comprehensive Orbit context for a project."""
    if not project_id or not token:
        return {"available": False}

    project = get_project_context(project_id, token)
    if not project:
        return {"available": False}

    return {
        "available": True,
        "project_id": project_id,
        "project_name": project.get("name", ""),
        "description": project.get("description", ""),
        "statistics": project.get("statistics", {}),
    }
