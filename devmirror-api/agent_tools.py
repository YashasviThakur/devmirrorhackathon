"""
DevMirror — Gemini 3 agentic loop with function calling.
Replaces the simple call_ai() pattern with a multi-step agent that can
autonomously call developer data tools before composing its final answer.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-05-20")

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

_SYSTEM_PROMPT = """You are DevMirror Coach — an elite AI agent for software engineers and CS students, powered by Google Cloud and Gemini 3.

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


# ── Tool executor (injected from main.py at call time) ────────────────────────

class AgentContext:
    """Holds all the live data-fetching functions and user context needed during a run."""

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


# ── Agentic loop ───────────────────────────────────────────────────────────────

def run_agent(
    question: str,
    ctx: AgentContext,
    max_turns: int = 6,
) -> dict[str, Any]:
    """
    Run the Gemini 3 agent with tool use.
    Returns:
      {
        "response":    str,          # final text answer
        "tool_calls":  list[dict],   # all tool calls made (for reasoning panel)
        "is_schedule": bool,
        "scheduled_events": list,
      }
    """
    if not GEMINI_API_KEY:
        return {
            "response":         "Gemini API key not configured.",
            "tool_calls":       [],
            "is_schedule":      False,
            "scheduled_events": [],
        }

    genai.configure(api_key=GEMINI_API_KEY)

    system_prompt = _SYSTEM_PROMPT.format(
        today=datetime.utcnow().strftime("%Y-%m-%d"),
        goal_1=ctx.goal_1 or "Not set",
        goal_2=ctx.goal_2 or "Not set",
        goal_3=ctx.goal_3 or "Not set",
    )

    tools = genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=_to_genai_type(v.get("type", "string")),
                            description=v.get("description", ""),
                        )
                        for k, v in t["parameters"].get("properties", {}).items()
                    },
                    required=t["parameters"].get("required", []),
                ),
            )
            for t in _TOOL_DECLARATIONS
        ]
    )

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        tools=[tools],
        system_instruction=system_prompt,
    )

    chat       = model.start_chat()
    all_tool_calls: list[dict] = []
    scheduled_events: list[dict] = []
    is_schedule = False

    try:
        response = chat.send_message(question)
    except Exception as e:
        err = str(e)
        err_type = type(e).__name__
        logger.error(f"[Agent] GEMINI FAILED type={err_type} err={err[:400]}")
        return {"response": f"[DEBUG] {err_type}: {err[:300]}", "tool_calls": [], "is_schedule": False, "scheduled_events": []}

    for _ in range(max_turns):
        # Check if any part is a function call
        fn_calls = [
            part.function_call
            for candidate in response.candidates
            for part in candidate.content.parts
            if part.function_call.name
        ]

        if not fn_calls:
            break

        # Execute all function calls and collect responses
        function_responses = []
        for fn_call in fn_calls:
            tool_name = fn_call.name
            tool_args = dict(fn_call.args)

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

            function_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response={"result": _safe_json(result)},
                    )
                )
            )

        try:
            response = chat.send_message(
                genai.protos.Content(role="user", parts=function_responses)
            )
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower() or "rate" in err.lower():
                msg = "The AI coach is temporarily rate-limited. Please try again in a few minutes."
            else:
                msg = f"AI service error: {err[:200]}"
            logger.error(f"[Agent] tool-response send_message failed: {err}")
            return {"response": msg, "tool_calls": all_tool_calls, "is_schedule": False, "scheduled_events": []}

    # Extract final text
    final_text = ""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, "text") and part.text:
                final_text += part.text

    return {
        "response":         final_text or "I couldn't generate a response. Please try again.",
        "tool_calls":       all_tool_calls,
        "is_schedule":      is_schedule,
        "scheduled_events": scheduled_events,
    }


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_genai_type(t: str):
    return {
        "string":  genai.protos.Type.STRING,
        "integer": genai.protos.Type.INTEGER,
        "number":  genai.protos.Type.NUMBER,
        "boolean": genai.protos.Type.BOOLEAN,
        "array":   genai.protos.Type.ARRAY,
        "object":  genai.protos.Type.OBJECT,
    }.get(t, genai.protos.Type.STRING)


def _safe_json(obj: Any) -> Any:
    """Convert objects to JSON-safe types for the function response."""
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return str(obj)
