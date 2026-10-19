"""Run one AI pre-review session against the KnowTether Content Reviewer agent.

Usage:
    python run_review.py <project-dir> [--artifact final.md] [--budget-cents 300]

<project-dir> must contain the final text and .kpdm/work.json; files under
<project-dir>/sources/ are uploaded as source material. The agent and
environment are created once with `ant apply`; this script only starts sessions.

Environment variables:
    AGENT_ID, ENV_ID   IDs from claude-lock.json
    GITHUB_TOKEN       fine-grained, read-only token for mchenla/knowtether
    KNOWTETHER_REF     branch to check out (default: main)
"""
import argparse
import os
from pathlib import Path

import anthropic

HERE = Path(__file__).resolve().parent


def upload(client, path: Path, mount: str) -> dict:
    with path.open("rb") as stream:
        file = client.beta.files.upload(file=stream)
    return {"type": "file", "file_id": file.id, "mount_path": mount}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path)
    parser.add_argument("--artifact", default="final.md")
    parser.add_argument("--budget-cents", type=int, default=300, help="hard spend cap per session, in US cents")
    args = parser.parse_args()
    project = args.project.resolve(strict=True)
    client = anthropic.Anthropic()

    resources = [
        {"type": "github_repository", "url": "https://github.com/mchenla/knowtether",
         "mount_path": "/workspace/knowtether", "authorization_token": os.environ["GITHUB_TOKEN"],
         "checkout": {"type": "branch", "name": os.environ.get("KNOWTETHER_REF", "main")}},
        upload(client, project / args.artifact, "/review/final.md"),
        upload(client, project / ".kpdm/work.json", "/review/.kpdm/work.json"),
    ]
    for source in sorted((project / "sources").glob("**/*")) if (project / "sources").is_dir() else []:
        if source.is_file():
            resources.append(upload(client, source, "/review/sources/" + source.relative_to(project / "sources").as_posix()))

    session = client.beta.sessions.create(
        agent=os.environ["AGENT_ID"],
        environment_id=os.environ["ENV_ID"],
        title="Pre-review: " + project.name,
        resources=resources,
        budget={"type": "limit", "max_list_cost": {"amount": str(args.budget_cents), "currency": "USD"}},
    )
    print("Watch live: https://platform.claude.com/workspaces/default/sessions/" + session.id)

    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(session_id=session.id, events=[{
            "type": "user.define_outcome",
            "description": f"Review /mnt/session/uploads/review/final.md (originally {args.artifact}) "
                           "and write the report to /mnt/session/outputs/review.md.",
            "rubric": {"type": "text", "content": (HERE / "rubric.md").read_text(encoding="utf-8")},
            "max_iterations": 3,
        }])
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
            elif event.type == "span.outcome_evaluation_end":
                print(f"\n[grader] iteration {event.iteration}: {event.result}")
            elif (event.type in ("agent.tool_use", "agent.mcp_tool_use")
                  and event.evaluated_permission == "ask"):
                # Unattended run: refuse anything the server could not judge safe.
                client.beta.sessions.events.send(session_id=session.id, events=[{
                    "type": "user.tool_confirmation", "tool_use_id": event.id, "result": "deny"}])
            elif event.type == "session.status_idle" and event.stop_reason.type != "requires_action":
                print(f"\n[session idle: {event.stop_reason.type}]")
                break
            elif event.type == "session.status_terminated":
                print("\n[session terminated]")
                break

    out = project / "review"
    out.mkdir(exist_ok=True)
    for item in client.beta.files.list(scope_id=session.id, betas=["managed-agents-2026-04-01"]).data:
        client.beta.files.download(item.id).write_to_file(out / item.filename)
        print("Saved", out / item.filename)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
