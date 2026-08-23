#!/usr/bin/env python3
"""读 skills.yaml，把自研和第三方 skill 软链到各 agent 的加载位置。

用法: python3 install.py
可重复运行：第三方仓库 git pull 到最新，软链幂等重建。
"""
import json
import os
import subprocess
import sys

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
        report.append(f"ok {name} -> {dst}")


def main():
    cfg = yaml.safe_load(open(os.path.join(ROOT, "skills.yaml")))
    targets = [os.path.expanduser(t) for t in cfg["targets"]]
    for t in targets:
        os.makedirs(t, exist_ok=True)
    report = []

    # 自研
    for s in cfg.get("self") or []:
        link(os.path.join(ROOT, s["path"]), targets, s["name"], report)

    # 第三方：clone/pull 上游仓库到 vendor/，按 lock 逐个软链
    lock_path = os.path.join(ROOT, cfg["third_party"]["lock"])
    lock = json.load(open(lock_path))["skills"]
    repos = {}
    for name, meta in lock.items():
        if meta.get("sourceType") != "github":
            report.append(f"!! 跳过 {name}: 未知 sourceType {meta.get('sourceType')}")
            continue
        repos.setdefault(meta["source"], []).append((name, meta["skillPath"]))

    os.makedirs(VENDOR, exist_ok=True)
    for repo, entries in repos.items():
        vdir = os.path.join(VENDOR, repo.replace("/", "__"))
        if os.path.isdir(os.path.join(vdir, ".git")):
            subprocess.run(["git", "-C", vdir, "pull", "-q"], check=False)
        else:
            url = f"https://github.com/{repo}.git"
            r = subprocess.run(["git", "clone", "-q", "--depth", "1", url, vdir])
            if r.returncode != 0:
                report.append(f"!! clone 失败 {repo}，跳过其 {len(entries)} 个 skill")
                continue
        for name, skill_path in entries:
            link(os.path.join(vdir, os.path.dirname(skill_path)), targets, name, report)

    print("\n".join(report))
    bad = [l for l in report if l.startswith("!!")]
    print(f"\n完成: {len(report) - len(bad)} 条成功, {len(bad)} 条需处理")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
