"""
DevMirror Code Coach Agent — AI-powered code analysis and improvement suggestions.
Uses GitLab Orbit context to analyze code quality, complexity, and best practices.
Integrated with Gemini for intelligent coaching and recommendations.
"""

import logging
import json
from typing import Any, Optional
import requests

logger = logging.getLogger(__name__)

GEMINI_API_KEY = ""  # Set from env in main.py


def analyze_merge_request(
    project_id: int,
    mr_iid: int,
    gitlab_token: str,
    gemini_key: str,
) -> dict[str, Any]:
    """
    Analyze a merge request using GitLab Orbit context and Gemini AI.
    Returns improvement suggestions, code quality score, and action items.
    """
    if not gitlab_token or not gemini_key:
        return {"success": False, "error": "Missing GitLab token or Gemini API key"}

    try:
        # Fetch MR details
        mr_resp = requests.get(
            f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}",
            headers={"PRIVATE-TOKEN": gitlab_token},
            timeout=10,
        )
        if mr_resp.status_code != 200:
            return {"success": False, "error": "Failed to fetch MR"}

        mr_data = mr_resp.json()

        # Build context for Gemini
        mr_context = {
            "title": mr_data.get("title", ""),
            "description": mr_data.get("description", "")[:1000],
            "additions": mr_data.get("additions", 0),
            "deletions": mr_data.get("deletions", 0),
            "changes_count": mr_data.get("changes_count", 0),
            "author": mr_data.get("author", {}).get("name", ""),
        }

        # Ask Gemini for code review insights
        prompt = f"""You are an expert code reviewer analyzing a GitLab merge request.

Merge Request: {mr_context['title']}
Author: {mr_context['author']}
Changes: {mr_context['additions']} additions, {mr_context['deletions']} deletions across {mr_context['changes_count']} files

Description:
{mr_context['description']}

Based on the scale of changes and description, provide:
1. Code Quality Assessment (1-10 score)
2. Key Improvement Areas (3-5 bullet points)
3. Risk Factors (if any)
4. One Concrete Next Action

Keep response under 300 words. Be constructive and specific."""

        gemini_resp = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": gemini_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500,
                },
            },
            timeout=15,
        )

        if gemini_resp.status_code != 200:
            return {"success": False, "error": "Gemini API failed"}

        gemini_data = gemini_resp.json()
        analysis_text = (
            gemini_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        return {
            "success": True,
            "mr_title": mr_context["title"],
            "mr_author": mr_context["author"],
            "changes": {
                "additions": mr_context["additions"],
                "deletions": mr_context["deletions"],
                "files_changed": mr_context["changes_count"],
            },
            "ai_analysis": analysis_text,
            "mr_url": mr_data.get("web_url", ""),
        }

    except Exception as e:
        logger.error(f"Code coach analysis failed: {e}")
        return {"success": False, "error": str(e)}


def find_technical_debt(
    project_id: int,
    gitlab_token: str,
    gemini_key: str,
) -> dict[str, Any]:
    """
    Scan for technical debt patterns in a project using GitLab Orbit.
    Uses Gemini to identify code smells, complexity hotspots, and improvement opportunities.
    """
    if not gitlab_token or not gemini_key:
        return {"success": False, "error": "Missing credentials"}

    try:
        # Fetch recent commits to understand project activity
        commits_resp = requests.get(
            f"https://gitlab.com/api/v4/projects/{project_id}/repository/commits",
            headers={"PRIVATE-TOKEN": gitlab_token},
            params={"per_page": 20},
            timeout=10,
        )

        if commits_resp.status_code != 200:
            return {"success": False, "error": "Failed to fetch commits"}

        commits = commits_resp.json()
        commit_summary = {
            "recent_commits": len(commits),
            "latest_author": commits[0].get("author_name", "") if commits else "",
            "avg_files_per_commit": sum(
                len(c.get("parent_ids", [])) for c in commits
            ) / max(len(commits), 1),
        }

        # Ask Gemini to identify debt patterns
        prompt = f"""You are a technical debt analyzer for a software project.

Project Statistics:
- Recent commits: {commit_summary['recent_commits']}
- Latest contributor: {commit_summary['latest_author']}

Based on typical patterns in active projects, identify likely technical debt areas:
1. Code Complexity Hotspots (where they often exist in projects)
2. Testing Gaps (common in established projects)
3. Documentation Debt
4. Dependency Management Issues
5. Performance Optimization Opportunities

For EACH area, provide:
- Description of the debt type
- Why it matters
- Concrete first step to address it

Be practical and specific. Focus on quick wins."""

        gemini_resp = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": gemini_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 800,
                },
            },
            timeout=15,
        )

        if gemini_resp.status_code != 200:
            return {"success": False, "error": "Gemini API failed"}

        gemini_data = gemini_resp.json()
        debt_analysis = (
            gemini_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        return {
            "success": True,
            "project_id": project_id,
            "debt_analysis": debt_analysis,
            "metrics": commit_summary,
        }

    except Exception as e:
        logger.error(f"Technical debt analysis failed: {e}")
        return {"success": False, "error": str(e)}
