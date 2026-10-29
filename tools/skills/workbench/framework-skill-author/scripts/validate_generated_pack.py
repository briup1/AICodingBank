#!/usr/bin/env python3
"""验证生成的框架 Skill Pack 的结构、触发元数据和来源关联。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL_RE = re.compile(r"https?://[^\s)>\]}]+")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
TODO_RE = re.compile(r"\bTODO\b|\[TODO:|待填写|PLACEHOLDER", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("缺少合法的 YAML frontmatter")

    raw, body = match.groups()
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise ValueError("frontmatter 必须是对象")
        return data, body
    except ImportError:
        data: dict[str, object] = {}
        for line in raw.splitlines():
            if line.startswith((" ", "\t")) or ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"\'')
        return data, body


def find_skill_root(pack: Path) -> Path:
    nested = pack / "skills"
    return nested if nested.is_dir() else pack


def validate_skill(skill_dir: Path) -> tuple[list[str], list[str], dict[str, object] | None]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return ["缺少 SKILL.md"], warnings, None

    try:
        metadata, body = parse_frontmatter(skill_md)
    except (OSError, ValueError, Exception) as exc:
        return [str(exc)], warnings, None

    name = metadata.get("name")
    description = metadata.get("description")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        errors.append("name 必须是合法的 hyphen-case 字符串")
    elif name != skill_dir.name:
        errors.append(f"name '{name}' 与目录名 '{skill_dir.name}' 不一致")

    if not isinstance(description, str) or not description.strip():
        errors.append("description 不能为空")
    elif len(description.strip()) > 1024:
        errors.append("description 超过 1024 字符")

    full_text = skill_md.read_text(encoding="utf-8")
    if TODO_RE.search(full_text):
        errors.append("存在 TODO 或占位符")
    if len(body.strip()) < 120:
        warnings.append("SKILL.md 正文过短，可能不足以提供有效决策指导")

    sources = skill_dir / "sources.md"
    if not sources.is_file():
        errors.append("缺少 sources.md")
    else:
        urls = URL_RE.findall(sources.read_text(encoding="utf-8"))
        if not urls:
            errors.append("sources.md 未包含 HTTP(S) 官方来源")

    for target in LINK_RE.findall(body):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        local = (skill_dir / target.split("#", 1)[0]).resolve()
        try:
            local.relative_to(skill_dir.resolve())
        except ValueError:
            errors.append(f"本地链接越出 Skill 目录: {target}")
            continue
        if not local.exists():
            errors.append(f"本地链接不存在: {target}")

    return errors, warnings, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="验证生成的框架 Skill Pack。")
    parser.add_argument("pack", type=Path, help="Pack 根目录，内部可包含 skills/ 子目录")
    parser.add_argument("--manifest", type=Path, help="可选的 source-manifest.json")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args()

    root = find_skill_root(args.pack)
    if not root.is_dir():
        print(f"Skill 目录不存在: {root}", file=sys.stderr)
        return 2

    skill_dirs = sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())
    report: dict[str, object] = {"pack": str(args.pack), "skills": {}, "errors": [], "warnings": []}
    global_errors: list[str] = report["errors"]  # type: ignore[assignment]
    global_warnings: list[str] = report["warnings"]  # type: ignore[assignment]

    if not skill_dirs:
        global_errors.append("没有发现包含 SKILL.md 的 Skill")

    descriptions: dict[str, str] = {}
    skill_names: set[str] = set()
    for skill_dir in skill_dirs:
        errors, warnings, metadata = validate_skill(skill_dir)
        report["skills"][skill_dir.name] = {"errors": errors, "warnings": warnings}  # type: ignore[index]
        if metadata:
            name = str(metadata.get("name", ""))
            description = str(metadata.get("description", "")).strip()
            if name in skill_names:
                errors.append(f"重复的 Skill name: {name}")
            skill_names.add(name)
            if description:
                if description in descriptions:
                    errors.append(f"description 与 {descriptions[description]} 完全相同")
                else:
                    descriptions[description] = skill_dir.name

    if args.manifest:
        if not args.manifest.is_file():
            global_errors.append(f"manifest 不存在: {args.manifest}")
        else:
            try:
                manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
                used_by = {
                    skill
                    for source in manifest.get("sources", [])
                    for skill in source.get("used_by", [])
                }
                for skill_name in sorted(skill_names - used_by):
                    global_errors.append(f"manifest 没有关联 Skill: {skill_name}")
                issues = manifest.get("issues", {})
                if issues.get("unverified_urls"):
                    global_warnings.append("manifest 包含未验证 URL")
            except (OSError, json.JSONDecodeError) as exc:
                global_errors.append(f"manifest 无法解析: {exc}")

    total_errors = len(global_errors)
    total_warnings = len(global_warnings)
    for item in report["skills"].values():  # type: ignore[union-attr]
        total_errors += len(item["errors"])
        total_warnings += len(item["warnings"])
    report["summary"] = {"skill_count": len(skill_dirs), "errors": total_errors, "warnings": total_warnings}

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Skill 数量: {len(skill_dirs)}，错误: {total_errors}，警告: {total_warnings}")
        for skill_name, item in report["skills"].items():  # type: ignore[union-attr]
            for error in item["errors"]:
                print(f"[错误] {skill_name}: {error}")
            for warning in item["warnings"]:
                print(f"[警告] {skill_name}: {warning}")
        for error in global_errors:
            print(f"[错误] Pack: {error}")
        for warning in global_warnings:
            print(f"[警告] Pack: {warning}")

    return 0 if total_errors == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
