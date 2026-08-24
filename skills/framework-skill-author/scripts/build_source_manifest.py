#!/usr/bin/env python3
"""把来源发现结果和各 Skill 的 sources.md 合并为 Pack 级来源清单。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s)>\]}]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_url(url: str) -> str:
    return url.rstrip(".,;:")


def skill_root(pack: Path) -> Path:
    nested = pack / "skills"
    return nested if nested.is_dir() else pack


def collect_usage(pack: Path) -> tuple[dict[str, set[str]], list[str]]:
    usage: dict[str, set[str]] = {}
    missing: list[str] = []
    root = skill_root(pack)
    if not root.is_dir():
        raise ValueError(f"Skill 目录不存在: {root}")

    for child in sorted(path for path in root.iterdir() if path.is_dir()):
        if not (child / "SKILL.md").is_file():
            continue
        sources_file = child / "sources.md"
        if not sources_file.is_file():
            missing.append(child.name)
            continue
        for raw_url in URL_RE.findall(sources_file.read_text(encoding="utf-8")):
            url = normalize_url(raw_url)
            usage.setdefault(url, set()).add(child.name)
    return usage, missing


def main() -> int:
    parser = argparse.ArgumentParser(description="构建可追踪到具体 Skill 的 source-manifest.json。")
    parser.add_argument("--inventory", required=True, type=Path, help="discover_sources.py 输出的 JSON")
    parser.add_argument("--pack", required=True, type=Path, help="生成的框架 Skill Pack 根目录")
    parser.add_argument("--output", required=True, type=Path, help="输出 manifest 路径")
    parser.add_argument("--allow-unverified", action="store_true", help="允许 sources.md 中存在未发现的 URL")
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    discovered = {
        normalize_url(str(item.get("url", ""))): item
        for item in inventory.get("sources", [])
        if item.get("url")
    }
    usage, missing_sources_files = collect_usage(args.pack)

    rows: list[dict[str, object]] = []
    unverified: list[str] = []
    for url, used_by in sorted(usage.items()):
        item = dict(discovered.get(url, {}))
        if not item:
            item = {
                "url": url,
                "source_type": "unclassified",
                "available": False,
                "status": None,
            }
            unverified.append(url)
        verification = "verified" if item.get("available") else "unverified"
        item["verification"] = verification
        item["used_by"] = sorted(used_by)
        rows.append(item)

    payload = {
        "schema_version": "1",
        "framework": inventory.get("framework", ""),
        "target_version": inventory.get("target_version", "unspecified"),
        "generated_at": utc_now(),
        "inventory_retrieved_at": inventory.get("retrieved_at", ""),
        "official_hosts": sorted(
            {
                urlparse(url).netloc
                for url in [*inventory.get("docs_entries", []), *inventory.get("repository_entries", [])]
                if urlparse(url).netloc
            }
        ),
        "sources": rows,
        "issues": {
            "missing_sources_files": missing_sources_files,
            "unverified_urls": unverified,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已写入 {args.output}：{len(rows)} 个来源，{len(unverified)} 个未验证 URL。")

    if missing_sources_files:
        print("缺少 sources.md: " + ", ".join(missing_sources_files), file=sys.stderr)
    if unverified and not args.allow_unverified:
        print("存在未验证来源；核验后重试，或显式使用 --allow-unverified。", file=sys.stderr)
        return 2
    return 0 if not missing_sources_files else 2


if __name__ == "__main__":
    sys.exit(main())
