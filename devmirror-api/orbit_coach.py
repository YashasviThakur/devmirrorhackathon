#!/usr/bin/env python3
"""
DevMirror Code Coach — a GitLab Orbit skill.

Indexes a repository with **GitLab Orbit** (the Knowledge Graph) and turns the
graph into an architecture-aware coaching report:

  1. `orbit index <repo>`  builds a structured knowledge graph of the codebase
  2. real SQL queries pull complexity hotspots, blast radius (call-graph fan-in),
     module coupling, and the longest functions
  3. Gemini reasons over that *real structure* to produce prioritized guidance

Unlike a generic LLM review, every recommendation is grounded in the project's
actual dependency graph — the core promise of GitLab Orbit.

Usage:
    python orbit_coach.py <repo_path> [--top 8] [--json]

Environment:
    GEMINI_API_KEY   Google AI Studio key. If unset, the Orbit analysis is still
                     printed (without the AI narrative), so the skill is testable
                     offline.

Runnable artifact behind the DevMirror Code Coach skill (see skill.yml /
manifest.json). MIT licensed — https://github.com/YashasviThakur/devmirrorhackathon
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import requests

import orbit_local_client as orbit

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def _coach_prompt(ctx: dict) -> str:
    def block(title: str, items: list[str]) -> str:
        body = "\n".join(f"  - {x}" for x in items) if items else "  (none)"
        return f"{title}:\n{body}"

    return f"""You are DevMirror Code Coach. You are reviewing a codebase using its
GitLab Orbit knowledge graph — a structured map of the real code, not guesses.

{ctx.get('summary', '')}

{block("Complexity hotspots (files by definition count)", ctx.get("hotspots", []))}

{block("Highest blast radius (most-called functions — risky to change)", ctx.get("blast_radius", []))}

{block("Most-coupled internal modules (imported by many files)", ctx.get("dependencies", []))}

{block("Longest functions (refactor candidates)", ctx.get("long_functions", []))}

Using ONLY the graph facts above, produce a prioritized coaching report:
1. **Top 3 risks** — name the specific file/function and why the graph flags it
   (e.g. high fan-in + long body = fragile core).
2. **Refactor plan** — concrete first step for each risk.
3. **Test priority** — which 2-3 functions most need tests, justified by blast radius.
4. **One sentence** on overall architectural health.

Reference the real names from the graph. Be specific. Under 400 words."""


def _gemini(prompt: str, api_key: str) -> str | None:
    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1100},
            },
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"[gemini] error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            return None
        return (
            resp.json().get("candidates", [{}])[0]
            .get("content", {}).get("parts", [{}])[0].get("text", "")
        )
    except Exception as e:  # pragma: no cover
        print(f"[gemini] call failed: {e}", file=sys.stderr)
        return None


def coach(repo_path: str, top: int = 8) -> dict:
    """Run the full Orbit-powered coaching pass and return a result dict."""
    ctx = orbit.build_context(repo_path, do_index=True, top=top)
    if not ctx.get("available"):
        return {"success": False, "error": ctx.get("detail", "Orbit unavailable"), "orbit": ctx}

    result = {"success": True, "repo": repo_path, "orbit_context": ctx}
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        analysis = _gemini(_coach_prompt(ctx), api_key)
        result["ai_analysis"] = analysis or "(AI analysis unavailable)"
    else:
        result["ai_analysis"] = None
    return result


def _print_report(res: dict) -> None:
    ctx = res.get("orbit_context", {})
    print("=" * 70)
    print("  DevMirror Code Coach — powered by GitLab Orbit")
    print("=" * 70)
    print(f"\n{ctx.get('summary', '')}\n")
    for title, key in (
        ("Complexity hotspots", "hotspots"),
        ("Highest blast radius (fan-in)", "blast_radius"),
        ("Most-coupled modules", "dependencies"),
        ("Longest functions", "long_functions"),
    ):
        print(f"── {title} " + "─" * (66 - len(title)))
        for line in ctx.get(key, []):
            print(f"   • {line}")
        print()
    if res.get("ai_analysis"):
        print("── AI coaching report " + "─" * 46)
        print(res["ai_analysis"])
    else:
        print("(Set GEMINI_API_KEY to add the AI coaching narrative.)")


def main() -> int:
    # Windows consoles default to cp1252; the report and Gemini output use UTF-8.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="DevMirror Code Coach — GitLab Orbit skill")
    parser.add_argument("repo_path", help="Path to the repository to analyse")
    parser.add_argument("--top", type=int, default=8, help="Rows per signal (default 8)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a report")
    args = parser.parse_args()

    if not orbit.is_available():
        print("error: the `orbit` CLI is not installed. See "
              "https://docs.gitlab.com/orbit/", file=sys.stderr)
        return 2

    res = coach(args.repo_path, top=args.top)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        _print_report(res)
    return 0 if res.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
