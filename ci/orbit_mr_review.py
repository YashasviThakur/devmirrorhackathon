#!/usr/bin/env python3
"""
GitLab CI job — post a GitLab Orbit blast-radius review on every merge request.

Runs inside a `merge_request_event` pipeline:
  1. indexes the checked-out repo with GitLab Orbit (`orbit index`)
  2. asks the Orbit knowledge graph for the blast radius of the changed files
  3. posts a Markdown report as an MR comment

Deterministic and key-free — no LLM call required, so it never flakes. Needs a
project/group access token with `api` scope exposed as the CI variable
`GITLAB_TOKEN` (CI_JOB_TOKEN cannot create MR notes).
"""

import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "devmirror-api"))

import orbit_local_client as orbit  # noqa: E402

API = os.environ.get("CI_API_V4_URL", "https://gitlab.com/api/v4")
PROJECT = os.environ.get("CI_PROJECT_ID")
MR_IID = os.environ.get("CI_MERGE_REQUEST_IID")
TOKEN = os.environ.get("GITLAB_TOKEN", "")


def _api(path: str, method: str = "GET", data: dict | None = None):
    req = urllib.request.Request(
        f"{API}{path}", method=method, headers={"PRIVATE-TOKEN": TOKEN}
    )
    if data is not None:
        req.data = urllib.parse.urlencode(data).encode()
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode() or "null")


def _render(impacts: list[dict]) -> str:
    if not impacts:
        return ("🛰️ **GitLab Orbit Code Coach** — the changed files have no recorded "
                "blast radius in the knowledge graph (new or leaf files).")
    lines = [
        "## 🛰️ GitLab Orbit Code Coach — blast radius of this MR",
        "",
        "_Computed from the Orbit knowledge graph (call-graph fan-in + import coupling)._",
        "",
        "| File | Risk | Imported by | Hot functions |",
        "|---|---|---|---|",
    ]
    for it in impacts:
        defs = ", ".join(
            f"`{d['name']}` ({d['callers']})" for d in it.get("hot_definitions", [])
        ) or "—"
        lines.append(
            f"| `{it['file']}` | **{it['risk']}** | {it['importer_count']} files | {defs} |"
        )
    high = [it["file"] for it in impacts if it["risk"] == "HIGH"]
    if high:
        lines += [
            "",
            f"⚠️ **{len(high)} high-blast-radius file(s)** changed — prioritize review & tests: "
            + ", ".join(f"`{h}`" for h in high),
        ]
    lines += ["", "<sub>Powered by GitLab Orbit · DevMirror Code Coach</sub>"]
    return "\n".join(lines)


def main() -> int:
    if not (PROJECT and MR_IID and TOKEN):
        print("Skipping: need CI_PROJECT_ID, CI_MERGE_REQUEST_IID and GITLAB_TOKEN.",
              file=sys.stderr)
        return 0  # never fail the pipeline over config

    if not orbit.is_available():
        print("Skipping: orbit CLI not installed in the job.", file=sys.stderr)
        return 0

    orbit.index_repo(ROOT)

    changes = _api(f"/projects/{PROJECT}/merge_requests/{MR_IID}/changes")
    paths = [
        c.get("new_path") or c.get("old_path")
        for c in (changes or {}).get("changes", [])
        if (c.get("new_path") or c.get("old_path"))
    ]
    impacts = orbit.impact_of_changed_files(paths) if paths else []

    body = _render(impacts)
    _api(f"/projects/{PROJECT}/merge_requests/{MR_IID}/notes", method="POST",
         data={"body": body})
    print(f"Posted Orbit review to MR !{MR_IID} ({len(impacts)} changed file(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
