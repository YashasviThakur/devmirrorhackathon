"""
DevMirror — Gemini agentic loop using REST API directly (no SDK).
Uses requests.post() so the API key is always read fresh from env vars.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

# ── Tool declarations ──────────────────────────────────────────────────────────

_TOOL_DECLARATIONS = [
    {
        "name": "fetch_github_stats",
        "description": (
            "Fetch live GitHub statistics for a developer: repos, commits this week, "
            "top repository, languages, followers, contribution grid."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "GitHub username"}
            },
            "required": ["username"],
        },
    },
    {
        "name": "fetch_leetcode_stats",
        "description": (
            "Fetch LeetCode statistics: total problems solved, difficulty breakdown "
            "(easy/medium/hard), current streak, acceptance rate, ranking."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "LeetCode username"}
            },
            "required": ["username"],
        },
    },
    {
        "name": "fetch_codeforces_stats",
        "description": (
            "Fetch Codeforces stats: rating, rank, max rating, problems solved, "
            "recent submission verdicts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "handle": {"type": "string", "description": "Codeforces handle"}
            },
            "required": ["handle"],
        },
    },
    {
        "name": "fetch_gitlab_stats",
        "description": (
            "Fetch GitLab statistics: total projects, commits this week, open merge "
            "requests, top project, languages used."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "GitLab username"},
                "token":    {"type": "string", "description": "GitLab personal access token"},
            },
            "required": ["username", "token"],
        },
    },
    {
        "name": "fetch_gitlab_orbit",
        "description": (
            "Fetch GitLab Orbit context for a project: codebase structure, complexity metrics, "
            "code quality indicators. Enables AI-powered code analysis and coaching."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "GitLab project ID"},
                "token":      {"type": "string", "description": "GitLab personal access token"},
            },
            "required": ["project_id", "token"],
        },
    },
    {
        "name": "fetch_gmail_opportunities",
        "description": (
            "Fetch filtered Gmail emails about internships, hackathons, and scholarships "
            "for the authenticated user."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "DevMirror user ID"}
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "fetch_calendar_events",
        "description": "Fetch upcoming Google Calendar events for the authenticated user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "DevMirror user ID"}
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "schedule_calendar_event",
        "description": "Create a new Google Calendar event for the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id":     {"type": "integer"},
                "summary":     {"type": "string", "description": "Event title"},
                "description": {"type": "string", "description": "Event description"},
                "start_time":  {"type": "string", "description": "ISO 8601 start datetime"},
                "end_time":    {"type": "string", "description": "ISO 8601 end datetime"},
            },
            "required": ["user_id", "summary", "start_time", "end_time"],
        },
    },
    {
        "name": "get_user_profile",
        "description": "Get the user's goals, handles, and linked account info from DevMirror.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "DevMirror user ID"}
            },
            "required": ["user_id"],
        },
    },
]


# ── System prompt ──────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are DevMirror Coach — an elite AI agent for software engineers and CS students, powered by Google Cloud and Gemini.

You have access to tools that fetch LIVE data from the user's developer accounts: GitHub, GitLab, LeetCode, Codeforces, Gmail, and Google Calendar.

AGENT RULES:
1. Always fetch relevant live data using tools before answering questions about the user's progress.
2. For scheduling requests, use schedule_calendar_event and confirm what was created.
3. Be specific — reference actual numbers, repo names, problem titles from the fetched data.
4. Be motivating, never shame. Celebrate wins. Give ONE concrete next action.
5. Use markdown for formatting: **bold**, ## headers, bullet points. Max 400 words.
6. Never be vague. If data isn't available, say so and recommend what to set up.

Today is {today}. The user's goals are:
  • Goal 1: {goal_1}
  • Goal 2: {goal_2}
  • Goal 3: {goal_3}
"""


# ── Agent context ──────────────────────────────────────────────────────────────

class AgentContext:
    def __init__(
        self,
        user_id: int,
        goal_1: str,
        goal_2: str,
        goal_3: str,
        fetch_github_fn,
        fetch_leetcode_fn,
        fetch_codeforces_fn,
        fetch_gitlab_fn,
        fetch_orbit_fn,
        fetch_gmail_fn,
        fetch_calendar_fn,
        create_calendar_fn,
        get_user_fn,
        gitlab_username: str = "",
        gitlab_token: str = "",
    ):
        self.user_id          = user_id
        self.goal_1           = goal_1
        self.goal_2           = goal_2
        self.goal_3           = goal_3
        self.fetch_github     = fetch_github_fn
        self.fetch_leetcode   = fetch_leetcode_fn
        self.fetch_codeforces = fetch_codeforces_fn
        self.fetch_gitlab_raw = fetch_gitlab_fn
        self.fetch_orbit      = fetch_orbit_fn
        self.fetch_gmail      = fetch_gmail_fn
        self.fetch_calendar   = fetch_calendar_fn
        self.create_calendar  = create_calendar_fn
        self.get_user         = get_user_fn
        self.gitlab_username  = gitlab_username
        self.gitlab_token     = gitlab_token

    def execute_tool(self, name: str, args: dict) -> Any:
        try:
            if name == "fetch_github_stats":
                return self.fetch_github(args["username"])
            if name == "fetch_leetcode_stats":
                return self.fetch_leetcode(args["username"])
            if name == "fetch_codeforces_stats":
                return self.fetch_codeforces(args["handle"])
            if name == "fetch_gitlab_stats":
                return self.fetch_gitlab_raw(
                    args.get("username", self.gitlab_username),
                    args.get("token", self.gitlab_token),
                )
            if name == "fetch_gitlab_orbit":
                return self.fetch_orbit(
                    args["project_id"],
                    args.get("token", self.gitlab_token),
                )
            if name == "fetch_gmail_opportunities":
                return self.fetch_gmail(args["user_id"])
            if name == "fetch_calendar_events":
                return self.fetch_calendar(args["user_id"])
            if name == "schedule_calendar_event":
                event = {
                    "summary":     args.get("summary", "DevMirror Task"),
                    "description": args.get("description", ""),
                    "start_time":  args["start_time"],
                    "end_time":    args["end_time"],
                }
                result = self.create_calendar(args["user_id"], event)
                return {"created": True, "event_id": result.get("id", ""), **event}
            if name == "get_user_profile":
                return self.get_user(args["user_id"])
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            return {"error": str(e)}
        return {"error": f"Unknown tool: {name}"}


# ── REST-based agentic loop ────────────────────────────────────────────────────

def run_agent(
    question: str,
    ctx: AgentContext,
    max_turns: int = 6,
) -> dict[str, Any]:
    # Use Vertex AI with service account credentials
    import google.auth
    import google.auth.transport.requests

    model   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    project = os.getenv("VERTEX_PROJECT", "gen-lang-client-0893010417")
    location = os.getenv("VERTEX_LOCATION", "us-central1")

    try:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        token = credentials.token
    except Exception as e:
        logger.error(f"[Agent] Failed to get Vertex AI credentials: {e}")
        return {
            "response":         "AI credentials not configured. Check GOOGLE_APPLICATION_CREDENTIALS_JSON.",
            "tool_calls":       [],
            "is_schedule":      False,
            "scheduled_events": [],
        }

    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/"
        f"locations/{location}/publishers/google/models/{model}:generateContent"
    )

    system_prompt = _SYSTEM_PROMPT.format(
        today=datetime.utcnow().strftime("%Y-%m-%d"),
        goal_1=ctx.goal_1 or "Not set",
        goal_2=ctx.goal_2 or "Not set",
        goal_3=ctx.goal_3 or "Not set",
    )

    contents: list[dict] = [{"role": "user", "parts": [{"text": question}]}]
    tools = [{"function_declarations": _TOOL_DECLARATIONS}]

    all_tool_calls: list[dict] = []
    scheduled_events: list[dict] = []
    is_schedule = False

    for turn in range(max_turns):
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents":           contents,
            "tools":              tools,
            "generationConfig":   {"temperature": 0.7, "maxOutputTokens": 1024},
        }

        try:
            resp = requests.post(url, json=payload, timeout=45, headers={"Authorization": f"Bearer {token}"})
        except Exception as e:
            logger.error(f"[Agent] network error: {e}")
            return {"response": "Could not reach AI service. Check your connection.", "tool_calls": all_tool_calls, "is_schedule": False, "scheduled_events": []}

        if resp.status_code == 429:
            return {"response": "The AI coach is temporarily rate-limited. Please try again in a few minutes.", "tool_calls": all_tool_calls, "is_schedule": False, "scheduled_events": []}

        if resp.status_code != 200:
            err = resp.text[:300]
            logger.error(f"[Agent] Gemini error {resp.status_code}: {err}")
            return {"response": f"AI service error ({resp.status_code}): {err[:150]}", "tool_calls": all_tool_calls, "is_schedule": False, "scheduled_events": []}

        data       = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return {"response": "No response from AI.", "tool_calls": all_tool_calls, "is_schedule": is_schedule, "scheduled_events": scheduled_events}

        parts = candidates[0].get("content", {}).get("parts", [])

        # Add model turn to history
        contents.append({"role": "model", "parts": parts})

        # Check for function calls
        fn_calls = [p["functionCall"] for p in parts if "functionCall" in p]

        if not fn_calls:
            # Final text response
            text = "".join(p.get("text", "") for p in parts).strip()
            return {
                "response":         text or "I couldn't generate a response. Please try again.",
                "tool_calls":       all_tool_calls,
                "is_schedule":      is_schedule,
                "scheduled_events": scheduled_events,
            }

        # Execute tools and collect responses
        fn_response_parts = []
        for fn_call in fn_calls:
            tool_name = fn_call.get("name", "")
            tool_args = fn_call.get("args", {})

            logger.info(f"[Agent] calling tool: {tool_name}({list(tool_args.keys())})")
            all_tool_calls.append({"tool": tool_name, "args": list(tool_args.keys())})

            result = ctx.execute_tool(tool_name, tool_args)

            if tool_name == "schedule_calendar_event" and isinstance(result, dict) and result.get("created"):
                is_schedule = True
                scheduled_events.append({
                    "summary": result.get("summary", ""),
                    "start":   result.get("start_time", ""),
                    "end":     result.get("end_time", ""),
                })

            fn_response_parts.append({
                "functionResponse": {
                    "name":     tool_name,
                    "response": {"result": _safe_json(result)},
                }
            })

        contents.append({"role": "user", "parts": fn_response_parts})

    # Max turns hit — return whatever we have
    text = "".join(p.get("text", "") for p in parts).strip()
    return {
        "response":         text or "I've processed your request.",
        "tool_calls":       all_tool_calls,
        "is_schedule":      is_schedule,
        "scheduled_events": scheduled_events,
    }


# ── Helpers ────────────────────────────────────────────────────────────────────

def _safe_json(obj: Any) -> Any:
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return str(obj)
