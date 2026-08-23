#!/usr/bin/env python3
"""读 skills.yaml，把已验证的自研和第三方 skill 软链到各 agent 加载位置，
并自动生成 CATALOG.md（按标签分组的能力总目录）。

用法: python3 install.py
可重复运行：第三方仓库 git pull 到最新，软链幂等重建，目录重新生成。
闸门：只有带 verified 日期的 skill 会被软链；未验证的只出现在目录里。
"""
import json
import os
import subprocess
import sys
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(ROOT, "vendor")


def link(src, targets, name, report):
    if not os.path.isdir(src):
        report.append(f"!! 跳过 {name}: 源目录不存在 {src}")
        return
    for t in targets:
        dst = os.path.join(t, name)
        if os.path.islink(dst):
            os.remove(dst)
        elif os.path.exists(dst):
            report.append(f"!! 跳过 {name} -> {dst}: 已存在真实目录，请手动处理")
            continue
        os.symlink(src, dst)


def write_catalog(entries, path):
    by_tag = defaultdict(list)
    for e in entries:
        for tag in e.get("tags") or ["未分类"]:
            by_tag[tag].append(e)
    total = len(entries)
    verified = sum(1 for e in entries if e.get("verified"))
    lines = [
        "# Skill 总目录（install.py 自动生成，勿手改）",
        "",
        f"共 {total} 个 · 已验证 {verified} · 待验证 {total - verified}",
        "",
        "想看深度使用经验 → wiki entity 页；想改行为 → SKILL.md；本目录只回答“它能干什么、边界在哪”。",
    ]
    for tag in sorted(by_tag):
        lines += ["", f"## {tag}"]
        for e in sorted(by_tag[tag], key=lambda x: x["name"]):
            v = e.get("verified")
            status = f"已验证 {v}" if v else "**待验证（未安装）**"
            lines.append(f"- **{e['name']}**（{e['origin']}·{status}）— {e.get('capability', '')}")
            if e.get("boundary"):
                lines.append(f"  边界：{e['boundary']}")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    cfg = yaml.safe_load(open(os.path.join(ROOT, "skills.yaml")))
    targets = [os.path.expanduser(t) for t in cfg["targets"]]
    for t in targets:
        os.makedirs(t, exist_ok=True)
    report = []
    entries = []

    # 自研
    for s in cfg.get("self") or []:
        e = dict(s, origin="自研")
        entries.append(e)
        if e.get("verified"):
            link(os.path.join(ROOT, s["path"]), targets, s["name"], report)

    # 第三方：clone/pull 上游仓库到 vendor/，按 lock 逐个软链
    lock_path = os.path.join(ROOT, cfg["third_party"]["lock"])
    lock = json.load(open(lock_path))["skills"]
    repos = defaultdict(list)
    for name, meta in lock.items():
        meta["name"] = name
        meta["origin"] = f"第三方·{meta['source']}"
        entries.append(meta)
        if meta.get("sourceType") != "github":
            report.append(f"!! 跳过 {name}: 未知 sourceType {meta.get('sourceType')}")
            continue
        repos[meta["source"]].append(meta)

    os.makedirs(VENDOR, exist_ok=True)
    for repo, metas in repos.items():
        vdir = os.path.join(VENDOR, repo.replace("/", "__"))
        if os.path.isdir(os.path.join(vdir, ".git")):
            subprocess.run(["git", "-C", vdir, "pull", "-q"], check=False)
        else:
            url = f"https://github.com/{repo}.git"
            r = subprocess.run(["git", "clone", "-q", "--depth", "1", url, vdir])
            if r.returncode != 0:
                report.append(f"!! clone 失败 {repo}，跳过其 {len(metas)} 个 skill")
                continue
        for meta in metas:
            if meta.get("verified"):
                link(os.path.join(vdir, os.path.dirname(meta["skillPath"])),
                     targets, meta["name"], report)

    write_catalog(entries, os.path.join(ROOT, "CATALOG.md"))

    pending = [e["name"] for e in entries if not e.get("verified")]
    for p in pending:
        report.append(f"-- 待验证未安装: {p}")
    print("\n".join(report) if report else "全部就绪")
    bad = [l for l in report if l.startswith("!!")]
    print(f"\n完成: {len(entries)} 个登记（{len(pending)} 个待验证）, {len(bad)} 条异常, CATALOG.md 已生成")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
