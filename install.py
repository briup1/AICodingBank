#!/usr/bin/env python3
"""安装登记中的 Skill，并生成能力目录。

用法: python3 install.py
可重复运行：第三方仓库 git pull 到最新，软链幂等重建，目录重新生成。
闸门：只有带 verified 日期且未被本机禁用的 Skill 会被软链。
本机配置：可在被 Git 忽略的 skills.local.yaml 中通过 disabled 列表停用 Skill。
"""
import json
import os
import subprocess
import sys
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(ROOT, "vendor")
LOCAL_CONFIG = "skills.local.yaml"


def load_disabled(path):
    """读取本机禁用清单；文件不存在时视为空。"""
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    if not isinstance(cfg, dict):
        raise ValueError("本机配置必须是 YAML 映射")
    disabled = cfg.get("disabled") or []
    if not isinstance(disabled, list) or not all(
        isinstance(name, str) and name.strip() for name in disabled
    ):
        raise ValueError("skills.local.yaml 的 disabled 必须是非空字符串列表")
    return {name.strip() for name in disabled}


def link(src, targets, name, report):
    if not os.path.isdir(src):
        report.append(f"!! 跳过 {name}: 源目录不存在 {src}")
        return
    for target in targets:
        dst = os.path.join(target, name)
        if os.path.islink(dst):
            os.remove(dst)
        elif os.path.exists(dst):
            report.append(f"!! 跳过 {name} -> {dst}: 已存在真实目录，请手动处理")
            continue
        os.symlink(src, dst)


def unlink_disabled(targets, name, report):
    """只移除加载位置中的软链接，绝不自动删除真实目录。"""
    for target in targets:
        dst = os.path.join(target, name)
        if os.path.islink(dst):
            os.remove(dst)
        elif os.path.exists(dst):
            report.append(f"!! 无法停用 {name} -> {dst}: 存在真实目录，请手动迁移")


def vendor_dir_name(repo, ref=None):
    """为同一仓库的默认分支与固定 ref 生成互不冲突的缓存目录名。"""
    name = repo.replace("/", "__")
    if ref:
        safe_ref = "".join(
            char if char.isalnum() or char in ".-_" else "__" for char in ref
        )
        name += f"__ref__{safe_ref}"
    return name


def sync_github_repo(repo, ref, vendor_dir):
    """同步 GitHub 仓库；指定 ref 时固定到该分支或标签。"""
    url = f"https://github.com/{repo}.git"
    if os.path.isdir(os.path.join(vendor_dir, ".git")):
        if not ref:
            return subprocess.run(
                ["git", "-C", vendor_dir, "pull", "-q"]
            ).returncode == 0
        fetched = subprocess.run(
            ["git", "-C", vendor_dir, "fetch", "-q", "--depth", "1", "origin", ref]
        )
        if fetched.returncode != 0:
            return False
        return subprocess.run(
            ["git", "-C", vendor_dir, "checkout", "-q", "--detach", "FETCH_HEAD"]
        ).returncode == 0

    command = ["git", "clone", "-q", "--depth", "1"]
    if ref:
        command.extend(["--branch", ref])
    command.extend([url, vendor_dir])
    return subprocess.run(command).returncode == 0


def write_catalog(entries, path):
    by_tag = defaultdict(list)
    for entry in entries:
        for tag in entry.get("tags") or ["未分类"]:
            by_tag[tag].append(entry)
    total = len(entries)
    verified = sum(1 for entry in entries if entry.get("verified"))
    lines = [
        "# Skill 总目录（install.py 自动生成，勿手改）",
        "",
        f"共 {total} 个 · 已验证 {verified} · 待验证 {total - verified}",
        "",
        "想看深度使用经验 → wiki entity 页；想改行为 → SKILL.md；本目录只回答“它能干什么、边界在哪”。",
    ]
    for tag in sorted(by_tag):
        lines += ["", f"## {tag}"]
        for entry in sorted(by_tag[tag], key=lambda item: item["name"]):
            verified_at = entry.get("verified")
            status = f"已验证 {verified_at}" if verified_at else "**待验证（未安装）**"
            lines.append(
                f"- **{entry['name']}**（{entry['origin']}·{status}）— "
                f"{entry.get('capability', '')}"
            )
            if entry.get("boundary"):
                lines.append(f"  边界：{entry['boundary']}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    report = []
    try:
        disabled = load_disabled(os.path.join(ROOT, LOCAL_CONFIG))
    except (OSError, yaml.YAMLError, ValueError) as exc:
        print(f"!! 本机配置无效: {exc}")
        sys.exit(1)

    with open(os.path.join(ROOT, "skills.yaml"), encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    targets = [os.path.expanduser(target) for target in cfg["targets"]]
    for target in targets:
        os.makedirs(target, exist_ok=True)

    self_entries = cfg.get("self") or []
    lock_path = os.path.join(ROOT, cfg["third_party"]["lock"])
    with open(lock_path, encoding="utf-8") as f:
        lock = json.load(f)["skills"]
    known_names = {entry["name"] for entry in self_entries} | set(lock)
    unknown_disabled = disabled - known_names
    if unknown_disabled:
        report.append(
            "!! 本机禁用项未登记: " + ", ".join(sorted(unknown_disabled))
        )

    entries = []

    # 自研
    for skill in self_entries:
        entry = dict(skill, origin="自研")
        entries.append(entry)
        if skill["name"] in disabled:
            unlink_disabled(targets, skill["name"], report)
        elif entry.get("verified"):
            link(os.path.join(ROOT, skill["path"]), targets, skill["name"], report)

    # 第三方：clone/pull 上游仓库到 vendor/，按 lock 逐个软链
    repos = defaultdict(list)
    for name, meta in lock.items():
        ref = meta.get("ref")
        origin = f"第三方·{meta['source']}" + (f"@{ref}" if ref else "")
        entry = dict(meta, name=name, origin=origin)
        entries.append(entry)
        if name in disabled:
            unlink_disabled(targets, name, report)
        if meta.get("sourceType") != "github":
            report.append(f"!! 跳过 {name}: 未知 sourceType {meta.get('sourceType')}")
            continue
        repos[(meta["source"], ref)].append(entry)

    os.makedirs(VENDOR, exist_ok=True)
    for (repo, ref), metas in repos.items():
        vendor_dir = os.path.join(VENDOR, vendor_dir_name(repo, ref))
        if not sync_github_repo(repo, ref, vendor_dir):
            source = f"{repo}@{ref}" if ref else repo
            report.append(f"!! 同步失败 {source}，跳过其 {len(metas)} 个 skill")
            continue
        for meta in metas:
            if meta["name"] not in disabled and meta.get("verified"):
                link(
                    os.path.join(vendor_dir, os.path.dirname(meta["skillPath"])),
                    targets,
                    meta["name"],
                    report,
                )

    write_catalog(entries, os.path.join(ROOT, "CATALOG.md"))

    pending = [entry["name"] for entry in entries if not entry.get("verified")]
    for name in pending:
        report.append(f"-- 待验证未安装: {name}")
    for name in sorted(disabled & known_names):
        report.append(f"-- 本机禁用未安装: {name}")
    print("\n".join(report) if report else "全部就绪")
    bad = [line for line in report if line.startswith("!!")]
    print(
        f"\n完成: {len(entries)} 个登记（{len(pending)} 个待验证，"
        f"{len(disabled & known_names)} 个本机禁用）, {len(bad)} 条异常, CATALOG.md 已生成"
    )
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
