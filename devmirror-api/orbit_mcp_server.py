"""
DevMirror Code Coach — MCP server.

Exposes the GitLab Orbit Code Coach to MCP-compatible agents (GitLab Duo Agent
Platform, Claude Code, Codex). This complements Orbit's own `orbit mcp` by
serving *coaching* (blast radius, risk, prioritized guidance) on top of the
knowledge graph, not just raw graph access.

Run (stdio transport):
    pip install "mcp[cli]"          # one-time
    python orbit_mcp_server.py

Register with an MCP client, e.g. Claude Code (.mcp.json):
    {
      "mcpServers": {
        "devmirror-code-coach": {
          "command": "python",
          "args": ["devmirror-api/orbit_mcp_server.py"]
        }
      }
    }
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import orbit_local_client as orbit  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # keep the module import-safe without the SDK installed
    FastMCP = None


def build_server():
    if FastMCP is None:
        raise SystemExit('MCP SDK not installed. Run:  pip install "mcp[cli]"')

    mcp = FastMCP("devmirror-code-coach")

    @mcp.tool()
    def coach_report(repo_path: str, top: int = 8) -> dict:
        """Index a repo with GitLab Orbit and return architecture-aware context:
        complexity hotspots, blast radius, module coupling, and longest functions."""
        if not orbit.is_available():
            return {"error": "GitLab Orbit CLI not installed (https://docs.gitlab.com/orbit/)"}
        return orbit.build_context(repo_path, do_index=True, top=top)

    @mcp.tool()
    def blast_radius(repo_path: str, top: int = 10) -> list[dict]:
        """Most-called functions in the repo (call-graph fan-in) — the riskiest to change."""
        if not orbit.is_available():
            return [{"error": "GitLab Orbit CLI not installed"}]
        orbit.index_repo(repo_path)
        pid = orbit._project_id(repo_path)
        return orbit.blast_radius(pid, top)

    @mcp.tool()
    def changed_files_impact(repo_path: str, files: list[str]) -> list[dict]:
        """Blast radius and HIGH/MEDIUM/LOW risk for a set of changed files (MR review)."""
        if not orbit.is_available():
            return [{"error": "GitLab Orbit CLI not installed"}]
        orbit.index_repo(repo_path)
        pid = orbit._project_id(repo_path)
        return orbit.impact_of_changed_files(files, pid=pid)

    return mcp


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
