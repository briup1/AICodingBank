#!/usr/bin/env python3
"""Resolve one TAPD story ID to a registered local product requirement, read-only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REGISTRY = {
    "44973445": {
        "project_name": "询报价项目",
        "repo": Path("/home/weilan/workdir/remote_project/ai-agent"),
        "map": Path(".agents/automation/.project02-tapd-map.json"),
    }
}
REQUIRED_REPO_FILES = ("AGENTS.md", "PRD-总览.md", "PRD-当前线上完整版.md")


def fail(message: str, code: int) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    return code


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--tapd-id", required=True)
    parser.add_argument("--local-requirement-id", help="Exact R-* ID read from this TAPD story")
    args = parser.parse_args()

    entry = REGISTRY.get(args.workspace_id)
    if not entry:
        return fail("workspace_not_registered", 2)

    repo: Path = entry["repo"]
    if not repo.is_dir() or any(not (repo / f).is_file() for f in REQUIRED_REPO_FILES):
        return fail("product_repository_unavailable_or_invalid", 3)

    mapping_file = repo / entry["map"]
    if not mapping_file.is_file() or not inside(mapping_file, repo):
        return fail("mapping_file_unavailable", 4)

    try:
        mapping = json.loads(mapping_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fail("mapping_file_invalid", 5)

    matched_id = None
    role = None
    for local_id, value in mapping.get("requirements", {}).items():
        if value.get("primary") == args.tapd_id:
            matched_id, role = local_id, "primary"
            break
        if args.tapd_id in value.get("related", []):
            matched_id, role = local_id, "related"
            break

    if not matched_id:
        # The local cache may lag behind TAPD. Fall back to an exact local
        # requirement ID supplied by the caller after reading the one story.
        if args.local_requirement_id:
            import re
            if not re.fullmatch(r"R-\d{8}-[A-Z]\d{3}", args.local_requirement_id):
                return fail("local_requirement_id_invalid", 6)
            matched_id, role = args.local_requirement_id, "tapd_description_local_id"
        else:
            return fail("requirement_mapping_not_found", 6)

    candidates = list(repo.glob(f"版本管理/周迭代/*/需求/{matched_id}.md"))
    if len(candidates) != 1 or not inside(candidates[0], repo):
        return fail("local_requirement_file_not_found_or_ambiguous", 7)

    requirement = candidates[0]
    week = requirement.parents[1].name
    weekly_overview = requirement.parents[1] / f"PRD-{week}-总览.md"
    result = {
        "ok": True,
        "workspace_id": args.workspace_id,
        "project_name": entry["project_name"],
        "local_requirement_id": matched_id,
        "mapping_role": role,
        "repository": str(repo),
        "repository_agents": str(repo / "AGENTS.md"),
        "requirement_file": str(requirement),
        "weekly_overview": str(weekly_overview) if weekly_overview.is_file() else None,
        "root_overview": str(repo / "PRD-总览.md"),
        "current_snapshot": str(repo / "PRD-当前线上完整版.md"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
