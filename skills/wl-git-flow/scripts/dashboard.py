#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import http.server
import json
import os
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

APP = "wl-git-flow"
VERSION = 1
DEFAULT_PATTERNS = [
    r"^feature/story/[a-z0-9][a-z0-9._-]*$",
    r"^feature/bug/[a-z0-9][a-z0-9._-]*$",
]
LEGACY_FIELDS = {
    "stage": "requirementFlowStage",
    "baseSha": "requirementFlowBaseSha",
    "lastDevSha": "requirementFlowLastDevSha",
    "devPassedSha": "requirementFlowDevPassedSha",
    "devTarget": "requirementFlowDevTarget",
    "lastBetaSha": "requirementFlowLastBetaSha",
    "betaPassedSha": "requirementFlowBetaPassedSha",
    "betaTarget": "requirementFlowBetaTarget",
}
STAGE_LABELS = {
    "active": "开发中",
    "paused": "已暂停",
    "ready-dev": "待合入 Dev",
    "dev-testing": "Dev 测试中",
    "dev-failed": "Dev 失败待修",
    "dev-passed": "Dev 通过待 Beta",
    "beta-testing": "Beta 测试中",
    "beta-passed": "Beta 通过待主干",
    "merged-master": "已合主干 / 待上线",
    "cleaned": "已清理 / 待上线",
    "online": "最近上线",
    "archived": "历史归档",
    "missing": "分支失联",
}


class DashboardError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimePaths:
    config_file: Path
    state_file: Path
    html_file: Path


STATE_THREAD_LOCK = threading.RLock()


@contextmanager
def dashboard_state_lock(paths: RuntimePaths):
    lock_file = paths.state_file.parent / ".dashboard.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(lock_file.parent, 0o700)
    with STATE_THREAD_LOCK, lock_file.open("a+", encoding="utf-8") as handle:
        os.chmod(lock_file, 0o600)
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def runtime_paths() -> RuntimePaths:
    home = Path.home()
    def xdg_home(name: str, fallback: Path) -> Path:
        raw = os.environ.get(name)
        value = Path(raw).expanduser() if raw else fallback
        if not value.is_absolute():
            raise DashboardError(f"{name} 必须是绝对路径：{value}")
        return value

    config_home = xdg_home("XDG_CONFIG_HOME", home / ".config")
    state_home = xdg_home("XDG_STATE_HOME", home / ".local/state")
    data_home = xdg_home("XDG_DATA_HOME", home / ".local/share")
    return RuntimePaths(
        config_file=config_home / APP / "config.json",
        state_file=state_home / APP / "state.json",
        html_file=data_home / APP / "dashboard.html",
    )


def default_config() -> dict[str, Any]:
    return {"version": VERSION, "recentlyOnlineDays": 7, "repositories": []}


def default_state() -> dict[str, Any]:
    return {
        "version": VERSION,
        "updatedAt": None,
        "requirements": {},
        "requirementMetadata": {},
    }


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return json.loads(json.dumps(default))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DashboardError(f"无法读取 JSON：{path}: {exc}") from exc
    if not isinstance(data, dict):
        raise DashboardError(f"JSON 根节点必须是对象：{path}")
    if data.get("version") != VERSION:
        raise DashboardError(
            f"不支持的数据版本：{path} version={data.get('version')!r}，期望 {VERSION}"
        )
    if "repositories" in default and not isinstance(data.get("repositories"), list):
        raise DashboardError(f"repositories 必须是数组：{path}")
    if "requirements" in default and not isinstance(data.get("requirements"), dict):
        raise DashboardError(f"requirements 必须是对象：{path}")
    if "requirementMetadata" in default and not isinstance(
        data.get("requirementMetadata", {}), dict
    ):
        raise DashboardError(f"requirementMetadata 必须是对象：{path}")
    data.setdefault("requirementMetadata", {})
    return data


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def save_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def git_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def run_git(repo: Path, *args: str, check: bool = True, timeout: int = 15) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=git_environment(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DashboardError(f"Git 命令失败：git -C {repo} {shlex.join(args)}: {exc}") from exc
    if check and completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise DashboardError(
            f"Git 命令失败：git -C {repo} {shlex.join(args)}: {message}"
        )
    return completed.stdout.strip()


def common_git_dir(path: str | Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    value = Path(run_git(candidate, "rev-parse", "--git-common-dir"))
    if not value.is_absolute():
        value = (candidate / value).resolve()
    return value


def canonical_repo(path: str | Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    raw = run_git(candidate, "worktree", "list", "--porcelain")
    first = next(
        (line.removeprefix("worktree ") for line in raw.splitlines() if line.startswith("worktree ")),
        None,
    )
    if first:
        return Path(first).resolve()
    root = run_git(candidate, "rev-parse", "--show-toplevel")
    return Path(root).resolve()


def repo_id(path: Path, identity: Path | None = None) -> str:
    slug = re.sub(r"[^a-z0-9._-]+", "-", path.name.lower()).strip("-") or "repo"
    digest = hashlib.sha256(str(identity or path).encode()).hexdigest()[:8]
    return f"{slug}-{digest}"


def default_repo_config(path: Path, name: str | None = None) -> dict[str, Any]:
    identity = common_git_dir(path)
    return {
        "id": repo_id(path, identity),
        "name": name or path.name,
        "path": str(path),
        "identity": str(identity),
        "baseRef": "origin/master",
        "devRef": "origin/feature/dev",
        "requirementPatterns": list(DEFAULT_PATTERNS),
        "worktreeRoot": str(Path.home() / "workdir/worktrees" / path.name),
        "onlineEvidence": {"type": "manual"},
    }


def register_repository(
    config: dict[str, Any],
    repo_path: str | Path,
    name: str | None = None,
    *,
    base_ref: str | None = None,
    dev_ref: str | None = None,
    worktree_root: str | None = None,
    patterns: list[str] | None = None,
) -> tuple[dict[str, Any], bool]:
    path = canonical_repo(repo_path)
    identity = common_git_dir(repo_path)
    repositories = config.setdefault("repositories", [])
    for item in repositories:
        changed = False
        item_identity = item.get("identity")
        if not item_identity and Path(item["path"]).expanduser().exists():
            try:
                item_identity = str(common_git_dir(item["path"]))
            except DashboardError:
                item_identity = None
        if item_identity == str(identity) or Path(item["path"]).expanduser().resolve() == path:
            if item.get("path") != str(path):
                item["path"] = str(path)
                changed = True
            if item.get("identity") != str(identity):
                item["identity"] = str(identity)
                changed = True
            if name and item.get("name") != name:
                item["name"] = name
                changed = True
            updates = {
                "baseRef": base_ref,
                "devRef": dev_ref,
                "worktreeRoot": str(Path(worktree_root).expanduser()) if worktree_root else None,
                "requirementPatterns": patterns,
            }
            for key, value in updates.items():
                if value is not None and item.get(key) != value:
                    item[key] = value
                    changed = True
            return item, changed
    item = default_repo_config(path, name)
    if base_ref:
        item["baseRef"] = base_ref
    if dev_ref:
        item["devRef"] = dev_ref
    if worktree_root:
        item["worktreeRoot"] = str(Path(worktree_root).expanduser())
    if patterns:
        item["requirementPatterns"] = patterns
    repositories.append(item)
    repositories.sort(key=lambda value: (value.get("name", "").lower(), value["path"]))
    return item, True


def requirement_key(project_id: str, branch: str) -> str:
    return f"{project_id}::{branch}"


def requirement_metadata_key(project_id: str, requirement_id: str) -> str:
    return f"{project_id}::{requirement_id}"


def dedupe_repositories(config: dict[str, Any], state: dict[str, Any]) -> None:
    groups: dict[str, list[dict[str, Any]]] = {}
    for project in config.get("repositories", []):
        identity = project.get("identity")
        if not identity and Path(project.get("path", "")).expanduser().exists():
            try:
                identity = str(common_git_dir(project["path"]))
                project["identity"] = identity
            except DashboardError:
                identity = None
        groups.setdefault(identity or f"id:{project.get('id')}", []).append(project)
    duplicates: set[str] = set()
    requirements = state.setdefault("requirements", {})
    requirement_metadata = state.setdefault("requirementMetadata", {})
    for projects in groups.values():
        if len(projects) < 2:
            continue
        canonical = projects[0]
        for duplicate in projects[1:]:
            duplicate_id = duplicate["id"]
            duplicates.add(duplicate_id)
            for key, entry in list(requirements.items()):
                if entry.get("projectId") != duplicate_id:
                    continue
                branch = entry.get("branch")
                if not branch:
                    requirements.pop(key, None)
                    continue
                new_key = requirement_key(canonical["id"], branch)
                target = requirements.setdefault(new_key, {})
                for field, value in entry.items():
                    if target.get(field) in (None, "", [], {}):
                        target[field] = value
                target["projectId"] = canonical["id"]
                target["repoPath"] = canonical["path"]
                requirements.pop(key, None)
            for key, entry in list(requirement_metadata.items()):
                if not key.startswith(f"{duplicate_id}::"):
                    continue
                requirement_id = key.split("::", 1)[1]
                new_key = requirement_metadata_key(canonical["id"], requirement_id)
                target = requirement_metadata.setdefault(new_key, {})
                for field, value in entry.items():
                    if target.get(field) in (None, "", [], {}):
                        target[field] = value
                requirement_metadata.pop(key, None)
    if duplicates:
        config["repositories"] = [
            project for project in config.get("repositories", []) if project["id"] not in duplicates
        ]


def parse_worktrees(repo: Path) -> list[dict[str, Any]]:
    raw = run_git(repo, "worktree", "list", "--porcelain")
    worktrees: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in [*raw.splitlines(), ""]:
        if not line:
            if current:
                worktrees.append(current)
            current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current["path"] = str(Path(value).resolve())
        elif key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "detached":
            current["detached"] = True
        elif key == "prunable":
            current["prunable"] = value or True
    return worktrees


def parse_refs(repo: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    fmt = "%(refname)|%(objectname)|%(upstream:short)|%(committerdate:iso8601-strict)|%(subject)"
    raw = run_git(repo, "for-each-ref", f"--format={fmt}", "refs/heads", "refs/remotes/origin")
    local: dict[str, dict[str, str]] = {}
    remote: dict[str, dict[str, str]] = {}
    for line in raw.splitlines():
        refname, sha, upstream, committed, subject = (
            line.split("|", 4) + ["", "", "", "", ""]
        )[:5]
        if refname == "refs/remotes/origin/HEAD":
            continue
        value = {
            "sha": sha,
            "upstream": upstream,
            "committedAt": committed,
            "subject": subject,
        }
        if refname.startswith("refs/heads/"):
            local[refname.removeprefix("refs/heads/")] = value
        elif refname.startswith("refs/remotes/"):
            remote[refname.removeprefix("refs/remotes/")] = value
    return local, remote


def matches_requirement(branch: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, branch) for pattern in patterns)


def validate_patterns(patterns: Iterable[str]) -> list[str]:
    values = list(patterns)
    try:
        for pattern in values:
            re.compile(pattern)
    except re.error as exc:
        raise DashboardError(f"无效的需求分支正则：{pattern}: {exc}") from exc
    return values


def short_sha(value: str | None) -> str | None:
    return value[:10] if value else None


def git_config(repo: Path, branch: str, key: str) -> str | None:
    value = run_git(
        repo,
        "config",
        "--local",
        "--get",
        f"branch.{branch}.{key}",
        check=False,
    )
    return value or None


def ref_exists(repo: Path, ref: str | None) -> bool:
    if not ref:
        return False
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=git_environment(),
    )
    return completed.returncode == 0


def is_ancestor(repo: Path, ancestor: str | None, descendant: str | None) -> bool:
    if not ancestor or not descendant or not ref_exists(repo, ancestor) or not ref_exists(repo, descendant):
        return False
    completed = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", ancestor, descendant],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=git_environment(),
    )
    return completed.returncode == 0


def ahead_behind(repo: Path, upstream: str | None, branch: str) -> tuple[int | None, int | None]:
    if not upstream or not ref_exists(repo, upstream) or not ref_exists(repo, branch):
        return None, None
    raw = run_git(repo, "rev-list", "--left-right", "--count", f"{upstream}...{branch}")
    behind_text, ahead_text = raw.split()
    return int(ahead_text), int(behind_text)


def worktree_status(path: str) -> dict[str, Any]:
    worktree = Path(path)
    result = {
        "path": path,
        "exists": worktree.exists(),
        "dirty": False,
        "temporary": path.startswith("/tmp/") or path.startswith("/private/tmp/"),
        "operationInProgress": False,
    }
    if not worktree.exists():
        return result
    result["dirty"] = bool(run_git(worktree, "status", "--porcelain", check=False))
    git_dir_text = run_git(worktree, "rev-parse", "--git-dir", check=False)
    if git_dir_text:
        git_dir = Path(git_dir_text)
        if not git_dir.is_absolute():
            git_dir = (worktree / git_dir).resolve()
        result["operationInProgress"] = any(
            candidate.exists()
            for candidate in [
                git_dir / "MERGE_HEAD",
                git_dir / "CHERRY_PICK_HEAD",
                git_dir / "rebase-merge",
                git_dir / "rebase-apply",
            ]
        )
    return result


def requirement_id_from_branch(branch: str) -> str:
    tail = branch.rsplit("/", 1)[-1]
    match = re.match(r"([0-9]+_[0-9]+)(?:-|$)", tail)
    return match.group(1) if match else tail


def migrate_legacy_metadata(repo: Path, branch: str, entry: dict[str, Any]) -> None:
    if entry.get("legacyMigrated"):
        return
    for field, legacy_key in LEGACY_FIELDS.items():
        value = git_config(repo, branch, legacy_key)
        if value is not None and field not in entry:
            entry[field] = value
    entry["legacyMigrated"] = True


def stage_metadata(repo: Path, branch: str, entry: dict[str, Any]) -> dict[str, str | None]:
    migrate_legacy_metadata(repo, branch, entry)
    return {field: entry.get(field) for field in LEGACY_FIELDS}


def add_anomaly(items: list[dict[str, str]], code: str, label: str, severity: str = "warning") -> None:
    if not any(item["code"] == code for item in items):
        items.append({"code": code, "label": label, "severity": severity})


def compute_requirement(
    repo: Path,
    project: dict[str, Any],
    branch: str,
    local: dict[str, dict[str, str]],
    remote: dict[str, dict[str, str]],
    branch_worktrees: list[dict[str, Any]],
    entry: dict[str, Any],
    recently_online_days: int,
) -> dict[str, Any]:
    local_ref = local.get(branch)
    remote_ref = remote.get(f"origin/{branch}")
    has_current_ref = bool(local_ref or remote_ref or branch_worktrees)
    current_tip = (local_ref or remote_ref or {}).get("sha")
    tip = current_tip or entry.get("lastSnapshot", {}).get("sha")
    metadata = stage_metadata(repo, branch, entry)
    for field, value in metadata.items():
        if value is not None and entry.get(field) is None:
            entry[field] = value
    statuses = [worktree_status(item["path"]) for item in branch_worktrees]
    dirty = any(item["dirty"] for item in statuses)
    operation = any(item["operationInProgress"] for item in statuses)
    upstream = local_ref.get("upstream") if local_ref else None
    ahead, behind = ahead_behind(repo, upstream, branch) if local_ref else (None, None)
    base_ref = project.get("baseRef", "origin/master")
    dev_ref = project.get("devRef", "origin/feature/dev")
    beta_target = metadata.get("betaTarget") or entry.get("lastSnapshot", {}).get("betaTarget")
    beta_ref = None
    if beta_target:
        beta_ref = beta_target if str(beta_target).startswith("origin/") else f"origin/{beta_target}"
        if not ref_exists(repo, beta_ref) and ref_exists(repo, str(beta_target)):
            beta_ref = str(beta_target)
    in_dev = bool(tip and is_ancestor(repo, tip, dev_ref))
    in_beta = bool(tip and beta_ref and is_ancestor(repo, tip, beta_ref))
    base_contains = bool(tip and is_ancestor(repo, tip, base_ref))
    progressed = bool(
        metadata.get("stage")
        or entry.get("lastSnapshot", {}).get("stage") in {
            "dev-testing",
            "dev-failed",
            "dev-passed",
            "beta-testing",
            "beta-passed",
            "merged-master",
        }
    )
    in_master = base_contains and bool(
        (metadata.get("baseSha") and tip != metadata.get("baseSha")) or progressed or entry.get("onlineAt")
    )
    if not has_current_ref and entry.get("lastSnapshot", {}).get("inMaster"):
        in_master = True

    anomalies: list[dict[str, str]] = []
    if dirty:
        add_anomaly(anomalies, "dirty", "Worktree 有未提交内容", "danger")
    if operation:
        add_anomaly(anomalies, "git-operation", "存在进行中的 Git 操作", "danger")
    if ahead:
        add_anomaly(anomalies, "unpushed", f"本地领先远端 {ahead} 个提交", "danger")
    if behind:
        add_anomaly(anomalies, "behind", f"本地落后远端 {behind} 个提交")
    if local_ref and not upstream:
        add_anomaly(anomalies, "no-upstream", "本地分支没有 upstream")
    if len(statuses) > 1:
        add_anomaly(anomalies, "duplicate-worktree", "同一需求存在多个 Worktree", "danger")
    if any(item["temporary"] for item in statuses):
        add_anomaly(anomalies, "temporary-path", "长期 Worktree 位于临时目录")
    expected_root = Path(project.get("worktreeRoot") or "").expanduser()
    if expected_root:
        expected_root = expected_root.resolve()
        outside_root = []
        for item in statuses:
            try:
                Path(item["path"]).resolve().relative_to(expected_root)
            except ValueError:
                outside_root.append(item["path"])
        if outside_root:
            add_anomaly(anomalies, "outside-worktree-root", "Worktree 不在统一需求目录")
    if statuses and not all(item["exists"] for item in statuses):
        add_anomaly(anomalies, "missing-path", "Worktree 路径不存在", "danger")
    dev_passed_sha = metadata.get("devPassedSha") or entry.get("lastSnapshot", {}).get("devPassedSha")
    stale_dev = bool(dev_passed_sha and tip and dev_passed_sha != tip)
    if stale_dev:
        add_anomaly(anomalies, "stale-dev-test", "Dev 通过结果已被新提交覆盖", "danger")
    if entry.get("pendingCleanup"):
        add_anomaly(anomalies, "pending-cleanup-event", "最终清理尚未完成或状态待恢复", "danger")
    if not has_current_ref and not in_master and not entry.get("onlineAt") and not entry.get("cleanedAt"):
        add_anomaly(anomalies, "missing-branch", "需求分支和 Worktree 均已消失", "danger")

    online_at = entry.get("onlineAt")
    online_sha = entry.get("onlineSha")
    reopened = bool(has_current_ref and online_at and tip and online_sha and tip != online_sha)
    if reopened:
        entry.pop("onlineAt", None)
        entry.pop("onlineSha", None)
        entry.pop("onlineEvidence", None)
        entry.pop("archivedAt", None)
        online_at = None
        add_anomaly(anomalies, "reopened", "上线后发现新的提交，需求已重新打开", "danger")

    git_stage = "missing"
    if tip:
        if entry.get("onlineAt"):
            online_time = parse_time(entry.get("onlineAt"))
            archive_after = timedelta(days=recently_online_days)
            if entry.get("archivedAt") or (online_time and now_utc() - online_time >= archive_after):
                git_stage = "archived"
                entry.setdefault("archivedAt", iso_now())
            else:
                git_stage = "online"
        elif entry.get("cleanedAt"):
            git_stage = "cleaned"
        elif in_master:
            git_stage = "merged-master"
        elif in_beta:
            git_stage = "beta-passed" if metadata.get("betaPassedSha") == tip else "beta-testing"
        elif metadata.get("stage") == "dev-failed" and metadata.get("lastDevSha") == tip:
            git_stage = "dev-failed"
        elif in_dev:
            git_stage = "dev-passed" if dev_passed_sha == tip else "dev-testing"
        elif not has_current_ref:
            git_stage = "missing"
        elif not branch_worktrees and remote_ref:
            git_stage = "paused"
        elif remote_ref and not dirty and not ahead:
            git_stage = "ready-dev"
        else:
            git_stage = "active"

    if git_stage == "merged-master" and (branch_worktrees or local_ref or remote_ref):
        add_anomaly(anomalies, "pending-cleanup", "已合主干但需求分支或 Worktree 尚未清理")

    verification = "未测试"
    if metadata.get("stage") == "dev-failed" and metadata.get("lastDevSha") == tip:
        verification = "Dev 失败"
    elif dev_passed_sha == tip:
        verification = "Dev 通过"
    elif in_dev:
        verification = "Dev 结果未知"
    if metadata.get("betaPassedSha") == tip:
        verification = "Beta 通过"
    elif in_beta:
        verification = "Beta 结果未知"
    if in_master and not entry.get("onlineAt"):
        verification = "待上线"
    if entry.get("cleanedAt") and not entry.get("onlineAt"):
        verification = "已清理，待上线"
    if entry.get("onlineAt"):
        verification = "已上线"

    next_actions = {
        "active": "继续开发、提交并推送需求分支",
        "paused": "需要时重建 Worktree，或确认是否继续",
        "ready-dev": "将当前需求 SHA 单向合入 Dev",
        "dev-testing": "等待 Dev 实测结果",
        "dev-failed": "回需求 Worktree 修复并重新集成",
        "dev-passed": "执行 Beta 前污染审计并晋级",
        "beta-testing": "等待 Beta 实测结果",
        "beta-passed": "按发布流程合入主干",
        "merged-master": "等待上线确认；完成后最终清理",
        "cleaned": "等待上线确认",
        "online": "核对清理状态，最近上线期结束后归档",
        "archived": "无需处理",
        "missing": "核对分支是否被意外删除",
    }
    if anomalies:
        next_action = anomalies[0]["label"]
    else:
        next_action = next_actions[git_stage]

    requirement = {
        "key": requirement_key(project["id"], branch),
        "projectId": project["id"],
        "projectName": project.get("name") or Path(project["path"]).name,
        "repoPath": project["path"],
        "requirementId": requirement_id_from_branch(branch),
        "title": entry.get("title") or "",
        "branch": branch,
        "stage": git_stage,
        "stageLabel": STAGE_LABELS[git_stage],
        "verification": verification,
        "visibility": "archived" if git_stage == "archived" else "recently-online" if git_stage == "online" else "active",
        "sha": tip,
        "shortSha": short_sha(tip),
        "localSha": local_ref.get("sha") if local_ref else None,
        "remoteSha": remote_ref.get("sha") if remote_ref else None,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "worktrees": statuses,
        "worktreePath": statuses[0]["path"] if statuses else None,
        "dirty": dirty,
        "inDev": in_dev,
        "inBeta": in_beta,
        "inMaster": in_master,
        "betaTarget": beta_target,
        "devPassedSha": dev_passed_sha,
        "onlineAt": entry.get("onlineAt"),
        "onlineEvidence": entry.get("onlineEvidence"),
        "anomalies": anomalies,
        "attention": any(item["severity"] in {"warning", "danger"} for item in anomalies),
        "nextAction": next_action,
        "firstSeenAt": entry.get("firstSeenAt"),
        "lastSeenAt": entry.get("lastSeenAt"),
        "lastCommitAt": (local_ref or remote_ref or {}).get("committedAt"),
        "lastCommitSubject": (local_ref or remote_ref or {}).get("subject"),
    }
    return requirement


def stale_requirements_for_project(
    project: dict[str, Any], state: dict[str, Any], message: str
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for entry in state.get("requirements", {}).values():
        if entry.get("projectId") != project["id"] or not entry.get("branch"):
            continue
        snapshot = entry.get("lastSnapshot", {})
        stage = snapshot.get("stage") or "missing"
        if entry.get("archivedAt"):
            stage = "archived"
        elif entry.get("onlineAt"):
            stage = "online"
        anomaly = {
            "code": "missing-repository",
            "label": message,
            "severity": "danger",
        }
        results.append(
            {
                "key": requirement_key(project["id"], entry["branch"]),
                "projectId": project["id"],
                "projectName": project.get("name") or Path(project["path"]).name,
                "repoPath": project["path"],
                "requirementId": requirement_id_from_branch(entry["branch"]),
                "title": entry.get("title") or "",
                "branch": entry["branch"],
                "stage": stage,
                "stageLabel": STAGE_LABELS.get(stage, STAGE_LABELS["missing"]),
                "verification": "仓库不可达，显示最后快照",
                "visibility": "archived" if stage == "archived" else "recently-online" if stage == "online" else "active",
                "sha": snapshot.get("sha"),
                "shortSha": short_sha(snapshot.get("sha")),
                "localSha": None,
                "remoteSha": None,
                "upstream": None,
                "ahead": None,
                "behind": None,
                "worktrees": [],
                "worktreePath": snapshot.get("worktreePath"),
                "dirty": False,
                "inDev": stage.startswith("dev-") or stage.startswith("beta-") or snapshot.get("inMaster", False),
                "inBeta": stage.startswith("beta-") or snapshot.get("inMaster", False),
                "inMaster": snapshot.get("inMaster", False),
                "betaTarget": snapshot.get("betaTarget"),
                "devPassedSha": snapshot.get("devPassedSha"),
                "onlineAt": entry.get("onlineAt"),
                "onlineEvidence": entry.get("onlineEvidence"),
                "anomalies": [anomaly],
                "attention": True,
                "nextAction": "恢复仓库路径后重新扫描",
                "firstSeenAt": entry.get("firstSeenAt"),
                "lastSeenAt": entry.get("lastSeenAt"),
                "lastCommitAt": None,
            }
        )
    return results


def scan_repository(
    project: dict[str, Any], state: dict[str, Any], recently_online_days: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    repo = Path(project["path"]).expanduser()
    errors: list[dict[str, str]] = []
    global_anomalies: list[dict[str, Any]] = []
    if not repo.exists():
        message = f"仓库路径不存在：{repo}"
        errors.append({"projectId": project["id"], "message": message})
        return stale_requirements_for_project(project, state, message), global_anomalies, errors
    try:
        repo = canonical_repo(repo)
        local, remote = parse_refs(repo)
        worktrees = parse_worktrees(repo)
    except DashboardError as exc:
        errors.append({"projectId": project["id"], "message": str(exc)})
        return stale_requirements_for_project(project, state, str(exc)), global_anomalies, errors

    try:
        patterns = validate_patterns(project.get("requirementPatterns") or DEFAULT_PATTERNS)
    except DashboardError as exc:
        errors.append({"projectId": project["id"], "message": str(exc)})
        return stale_requirements_for_project(project, state, str(exc)), global_anomalies, errors
    by_branch: dict[str, list[dict[str, Any]]] = {}
    for worktree in worktrees:
        branch = worktree.get("branch")
        if branch:
            by_branch.setdefault(branch, []).append(worktree)
        elif worktree.get("detached"):
            global_anomalies.append(
                {
                    "projectId": project["id"],
                    "projectName": project.get("name"),
                    "code": "detached-worktree",
                    "severity": "warning",
                    "label": "发现 detached Worktree",
                    "path": worktree.get("path"),
                    "sha": short_sha(worktree.get("head")),
                }
            )

    candidates = {branch for branch in local if matches_requirement(branch, patterns)}
    candidates.update(branch for branch in by_branch if matches_requirement(branch, patterns))
    persisted = state.setdefault("requirements", {})
    candidates.update(
        entry.get("branch")
        for entry in persisted.values()
        if entry.get("projectId") == project["id"]
        and entry.get("branch")
        and (entry.get("managed") or entry.get("onlineAt") or entry.get("archivedAt"))
    )

    for branch, branch_worktrees in by_branch.items():
        if not matches_requirement(branch, patterns) and branch.startswith(("feature/", "integration/", "sync/")):
            for worktree in branch_worktrees:
                global_anomalies.append(
                    {
                        "projectId": project["id"],
                        "projectName": project.get("name"),
                        "code": "unmanaged-worktree",
                        "severity": "warning",
                        "label": "发现未纳入需求规则的开发 Worktree",
                        "path": worktree.get("path"),
                        "branch": branch,
                        "sha": short_sha(worktree.get("head")),
                    }
                )

    results: list[dict[str, Any]] = []
    current_time = iso_now()
    for branch in sorted(value for value in candidates if value):
        key = requirement_key(project["id"], branch)
        entry = persisted.setdefault(
            key,
            {
                "projectId": project["id"],
                "repoPath": str(repo),
                "branch": branch,
                "firstSeenAt": current_time,
            },
        )
        entry["lastScannedAt"] = current_time
        if branch in local or f"origin/{branch}" in remote or branch in by_branch:
            entry["lastSeenAt"] = current_time
        if branch in local or branch in by_branch:
            entry["managed"] = True
        result = compute_requirement(
            repo,
            project,
            branch,
            local,
            remote,
            by_branch.get(branch, []),
            entry,
            recently_online_days,
        )
        entry["lastSnapshot"] = {
            "sha": result["sha"],
            "stage": result["stage"],
            "betaTarget": result["betaTarget"],
            "devPassedSha": result["devPassedSha"],
            "worktreePath": result["worktreePath"],
            "inMaster": result["inMaster"],
        }
        results.append(result)

    stale_keys = [
        key
        for key, entry in persisted.items()
        if entry.get("projectId") == project["id"]
        and not entry.get("managed")
        and not entry.get("onlineAt")
        and not entry.get("archivedAt")
    ]
    for key in stale_keys:
        persisted.pop(key, None)
    return results, global_anomalies, errors


def concise_git_title(subject: str | None) -> str:
    if not subject:
        return ""
    value = re.sub(r"^--(?:story|bug)=[^ ]+\s+", "", subject.strip())
    value = re.sub(
        r"^(?:feat|fix|chore|refactor|perf|test|docs|style|build|ci)(?:\([^)]*\))?!?:\s*",
        "",
        value,
        flags=re.I,
    )
    value = re.sub(r"\s+--(?:story|bug)=[^ ]+.*$", "", value).strip()
    return value


def select_primary_branch(
    branches: list[dict[str, Any]], metadata: dict[str, Any]
) -> dict[str, Any]:
    explicit = metadata.get("primaryBranch")
    if explicit:
        match = next((item for item in branches if item["branch"] == explicit), None)
        if match:
            return match
    with_worktree = [item for item in branches if item.get("worktreePath")]
    if with_worktree:
        return max(with_worktree, key=lambda item: item.get("lastCommitAt") or "")
    requirement_id = branches[0]["requirementId"]
    exact_names = {
        f"feature/story/{requirement_id}",
        f"feature/bug/{requirement_id}",
    }
    exact = next((item for item in branches if item["branch"] in exact_names), None)
    if exact:
        return exact
    return max(branches, key=lambda item: item.get("lastCommitAt") or "")


def group_requirements(
    branch_records: list[dict[str, Any]], state: dict[str, Any]
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in branch_records:
        key = requirement_metadata_key(item["projectId"], item["requirementId"])
        grouped.setdefault(key, []).append(item)
    metadata_store = state.setdefault("requirementMetadata", {})
    results: list[dict[str, Any]] = []
    for key, branches in grouped.items():
        metadata = metadata_store.setdefault(key, {})
        primary = select_primary_branch(branches, metadata)
        grouped_item = dict(primary)
        grouped_item["key"] = key
        grouped_item["primaryBranch"] = primary["branch"]
        grouped_item["branchCount"] = len(branches)
        grouped_item["branches"] = [
            {
                "branch": item["branch"],
                "primary": item is primary,
                "stage": item["stage"],
                "stageLabel": item["stageLabel"],
                "sha": item["sha"],
                "shortSha": item["shortSha"],
                "worktreePath": item["worktreePath"],
                "inDev": item["inDev"],
                "inBeta": item["inBeta"],
                "inMaster": item["inMaster"],
                "anomalies": item["anomalies"],
            }
            for item in sorted(branches, key=lambda value: value["branch"])
        ]
        anomalies = list(primary["anomalies"])
        if len(branches) > 1:
            add_anomaly(
                anomalies,
                "multiple-requirement-branches",
                f"同一需求存在 {len(branches)} 个开发分支",
                "danger",
            )
        secondary_in_dev = not primary["inDev"] and any(
            item["inDev"] for item in branches if item is not primary
        )
        if secondary_in_dev:
            add_anomaly(
                anomalies,
                "secondary-branch-in-dev",
                "旧分支已进入 Dev，当前主分支仍需重新集成",
                "danger",
            )
        grouped_item["anomalies"] = anomalies
        grouped_item["attention"] = bool(anomalies)
        if secondary_in_dev:
            grouped_item["nextAction"] = "当前主分支尚未进入 Dev，请重新集成并测试"
        elif anomalies:
            grouped_item["nextAction"] = anomalies[0]["label"]
        git_title = next(
            (
                concise_git_title(item.get("lastCommitSubject"))
                for item in [primary, *branches]
                if concise_git_title(item.get("lastCommitSubject"))
            ),
            "",
        )
        grouped_item["title"] = metadata.get("title") or git_title or primary["requirementId"]
        grouped_item["fullTitle"] = metadata.get("fullTitle") or grouped_item["title"]
        grouped_item["titleSource"] = metadata.get("titleSource") or (
            "git" if git_title else "requirement-id"
        )
        results.append(grouped_item)
    return results


def build_dashboard(config: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    branch_records: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    days = int(config.get("recentlyOnlineDays", 7))
    for project in config.get("repositories", []):
        project_requirements, project_anomalies, project_errors = scan_repository(
            project, state, days
        )
        branch_records.extend(project_requirements)
        anomalies.extend(project_anomalies)
        errors.extend(project_errors)
    requirements = group_requirements(branch_records, state)
    requirements.sort(
        key=lambda item: (
            item["visibility"] != "active",
            not item["attention"],
            item["projectName"].lower(),
            item["requirementId"],
        )
    )
    summary = {
        "active": sum(item["visibility"] == "active" for item in requirements),
        "attention": sum(item["attention"] for item in requirements) + len(anomalies) + len(errors),
        "dev": sum(
            item["stage"] == "ready-dev" or item["stage"].startswith("dev-")
            for item in requirements
        ),
        "beta": sum(item["stage"].startswith("beta-") for item in requirements),
        "pendingOnline": sum(item["stage"] == "merged-master" for item in requirements),
        "recentlyOnline": sum(item["visibility"] == "recently-online" for item in requirements),
        "archived": sum(item["visibility"] == "archived" for item in requirements),
    }
    return {
        "version": VERSION,
        "generatedAt": iso_now(),
        "summary": summary,
        "projects": config.get("repositories", []),
        "requirements": requirements,
        "anomalies": anomalies,
        "errors": errors,
    }


def template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "assets/dashboard-template.html"


def build_html(data: dict[str, Any]) -> str:
    template = template_path().read_text(encoding="utf-8")
    if template.count("{{DATA_JSON}}") != 1 or template.count("{{GENERATED_AT}}") != 1:
        raise DashboardError("HTML 模板必须且只能包含一个 DATA_JSON 和 GENERATED_AT 占位符")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return template.replace("{{DATA_JSON}}", payload).replace(
        "{{GENERATED_AT}}", data["generatedAt"]
    )


def render_html(data: dict[str, Any], output: Path) -> None:
    atomic_write(output, build_html(data))


LIVE_CONFIG_ELEMENT_ID = "wlDashboardLiveConfig"
LIVE_CONFIG_ANCHOR = '<script id="dashboardData" type="application/json">'
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": (
        "default-src 'none'; "
        "style-src 'unsafe-inline'; "
        "script-src 'unsafe-inline'; "
        "img-src data:; "
        "connect-src 'self'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}


@dataclass
class DashboardServerState:
    paths: RuntimePaths
    token: str
    origin: str
    latest_data: dict[str, Any]
    refresh_lock: threading.Lock = field(default_factory=threading.Lock)


def build_live_html(data: dict[str, Any], state: DashboardServerState) -> str:
    html = build_html(data)
    if html.count(LIVE_CONFIG_ANCHOR) != 1:
        raise DashboardError("HTML 缺少稳定的 dashboardData 脚本锚点")
    config = {
        "mode": "live",
        "api": {
            "state": "/api/state",
            "refresh": "/api/refresh",
            "health": "/api/health",
        },
        "token": state.token,
        "refreshIntervals": [0, 15, 30, 60],
    }
    payload = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    live_config = (
        f'<script id="{LIVE_CONFIG_ELEMENT_ID}" type="application/json">'
        f"{payload}</script>\n  "
    )
    return html.replace(LIVE_CONFIG_ANCHOR, live_config + LIVE_CONFIG_ANCHOR, 1)


class DashboardHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        state: DashboardServerState,
    ) -> None:
        self.dashboard_state = state
        super().__init__(server_address, DashboardRequestHandler)


class DashboardRequestHandler(http.server.BaseHTTPRequestHandler):
    server: DashboardHTTPServer

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(
        self, status: int, payload: bytes, content_type: str
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, status: int, data: dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._send(status, payload, "application/json; charset=utf-8")

    def _send_error(self, status: int, code: str, message: str) -> None:
        self._send_json(
            status,
            {"ok": False, "error": {"code": code, "message": message}},
        )

    def _host_is_valid(self) -> bool:
        expected = self.server.dashboard_state.origin.removeprefix("http://")
        return self.headers.get("Host") == expected

    def _authorized(self, *, require_origin: bool) -> bool:
        state = self.server.dashboard_state
        if not self._host_is_valid():
            return False
        token = self.headers.get("X-WL-Dashboard-Token")
        if token is None or not secrets.compare_digest(token, state.token):
            return False
        origin = self.headers.get("Origin")
        if require_origin:
            return origin == state.origin
        return origin is None or origin == state.origin

    def _require_authorization(self, *, require_origin: bool) -> bool:
        if self._authorized(require_origin=require_origin):
            return True
        self._send_error(403, "forbidden", "请求未通过本地看板安全校验")
        return False

    def do_GET(self) -> None:
        state = self.server.dashboard_state
        if self.path == "/":
            if not self._host_is_valid():
                self._send_error(403, "forbidden", "Host 与本地看板地址不匹配")
                return
            try:
                html = build_live_html(state.latest_data, state).encode("utf-8")
            except DashboardError as exc:
                self._send_error(500, "render-failed", str(exc))
                return
            self._send(200, html, "text/html; charset=utf-8")
            return
        if self.path == "/api/state":
            if not self._require_authorization(require_origin=False):
                return
            self._send_json(200, state.latest_data)
            return
        if self.path == "/api/health":
            if not self._host_is_valid():
                self._send_error(403, "forbidden", "Host 与本地看板地址不匹配")
                return
            self._send_json(
                200,
                {
                    "ok": True,
                    "mode": "live",
                    "generatedAt": state.latest_data.get("generatedAt"),
                    "refreshing": state.refresh_lock.locked(),
                },
            )
            return
        if self.path == "/api/refresh":
            self._send_error(405, "method-not-allowed", "刷新接口仅接受 POST")
            return
        self._send_error(404, "not-found", "接口不存在")

    def do_POST(self) -> None:
        if self.path != "/api/refresh":
            self._send_error(404, "not-found", "接口不存在")
            return
        if not self._require_authorization(require_origin=True):
            return
        if self.headers.get("Transfer-Encoding"):
            self._send_error(400, "request-body-not-allowed", "刷新请求体必须为空")
            return
        raw_length = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_length)
        except ValueError:
            self._send_error(400, "invalid-content-length", "Content-Length 无效")
            return
        if content_length != 0:
            self._send_error(400, "request-body-not-allowed", "刷新请求体必须为空")
            return

        state = self.server.dashboard_state
        if not state.refresh_lock.acquire(blocking=False):
            self._send_error(409, "refresh-in-progress", "已有刷新正在执行")
            return
        started = time.monotonic()
        try:
            data = refresh_dashboard(state.paths)
            state.latest_data = data
        except DashboardError as exc:
            self._send_error(500, "refresh-failed", str(exc))
            return
        except Exception:
            self._send_error(500, "refresh-failed", "刷新失败")
            return
        finally:
            state.refresh_lock.release()
        duration_ms = max(0, round((time.monotonic() - started) * 1000))
        self._send_json(200, {"ok": True, "data": data, "durationMs": duration_ms})

    def do_OPTIONS(self) -> None:
        self._send_error(405, "method-not-allowed", "不支持跨源请求")


def create_dashboard_server(
    paths: RuntimePaths,
    port: int = 0,
    *,
    token: str | None = None,
    initial_data: dict[str, Any] | None = None,
) -> DashboardHTTPServer:
    if not 0 <= port <= 65535:
        raise DashboardError("port 必须在 0 到 65535 之间")
    data = refresh_dashboard(paths) if initial_data is None else initial_data
    state = DashboardServerState(
        paths=paths,
        token=token or secrets.token_urlsafe(32),
        origin="",
        latest_data=data,
    )
    server = DashboardHTTPServer(("127.0.0.1", port), state)
    host, actual_port = server.server_address
    state.origin = f"http://{host}:{actual_port}"
    return server


def serve_dashboard(paths: RuntimePaths, port: int = 0, open_browser: bool = False) -> None:
    server = create_dashboard_server(paths, port)
    host, actual_port = server.server_address
    url = f"http://{host}:{actual_port}/"
    print(f"url={url}")
    print(f"projects={len(server.dashboard_state.latest_data.get('projects', []))}")
    print("security=127.0.0.1-only token+origin protected no-cors read-only-git")
    print("stop=Ctrl+C")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    finally:
        server.server_close()


def _refresh_dashboard_unlocked(
    paths: RuntimePaths, only_repo: str | None = None
) -> dict[str, Any]:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    dedupe_repositories(config, state)
    if only_repo:
        register_repository(config, only_repo)
    dashboard = build_dashboard(config, state)
    html = build_html(dashboard)
    state["updatedAt"] = dashboard["generatedAt"]
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)
    atomic_write(paths.html_file, html)
    return dashboard


def refresh_dashboard(paths: RuntimePaths, only_repo: str | None = None) -> dict[str, Any]:
    with dashboard_state_lock(paths):
        return _refresh_dashboard_unlocked(paths, only_repo)


def find_project(config: dict[str, Any], repo_path: str | Path) -> dict[str, Any]:
    target = canonical_repo(repo_path)
    for item in config.get("repositories", []):
        if Path(item["path"]).expanduser().resolve() == target:
            return item
    item, _ = register_repository(config, target)
    return item


def ensure_requirement_entry(
    config: dict[str, Any], state: dict[str, Any], repo_path: str, branch: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    project = find_project(config, repo_path)
    key = requirement_key(project["id"], branch)
    entry = state.setdefault("requirements", {}).setdefault(
        key,
        {
            "projectId": project["id"],
            "repoPath": project["path"],
            "branch": branch,
            "firstSeenAt": iso_now(),
        },
    )
    entry["managed"] = True
    entry["lastSeenAt"] = iso_now()
    return project, entry


def _record_event_unlocked(paths: RuntimePaths, args: argparse.Namespace) -> None:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    dedupe_repositories(config, state)
    project, entry = ensure_requirement_entry(config, state, args.repo, args.branch)
    migrate_legacy_metadata(Path(project["path"]), args.branch, entry)
    event = args.event
    if event == "start":
        if not args.base_sha or not args.worktree:
            raise DashboardError("record start 需要 --base-sha 和 --worktree")
        entry.update(stage="active", baseSha=args.base_sha, worktree=args.worktree)
    elif event == "dev-integration":
        if not args.sha or not args.target:
            raise DashboardError("record dev-integration 需要 --sha 和 --target")
        entry.update(
            stage="dev-testing" if args.pushed else "checkpointed",
            lastDevSha=args.sha,
            devTarget=args.target,
        )
        if entry.get("devPassedSha") != args.sha:
            entry.pop("devPassedSha", None)
    elif event == "dev-result":
        if not args.sha or args.result not in {"passed", "failed"}:
            raise DashboardError("record dev-result 需要 --sha 和 --result passed|failed")
        entry["lastDevSha"] = args.sha
        entry["stage"] = f"dev-{args.result}"
        if args.result == "passed":
            entry["devPassedSha"] = args.sha
        else:
            entry.pop("devPassedSha", None)
    elif event == "beta-integration":
        if not args.sha or not args.target:
            raise DashboardError("record beta-integration 需要 --sha 和 --target")
        entry.update(
            stage="beta-testing" if args.pushed else "promoted-locally",
            lastBetaSha=args.sha,
            betaTarget=args.target,
        )
        if entry.get("betaPassedSha") != args.sha:
            entry.pop("betaPassedSha", None)
    elif event == "stage":
        if args.stage not in {"paused", "beta-testing", "beta-passed", "released"}:
            raise DashboardError("record stage 的 --stage 不受支持")
        entry["stage"] = args.stage
        if args.stage == "beta-passed":
            if not args.sha:
                raise DashboardError("beta-passed 需要 --sha")
            entry["betaPassedSha"] = args.sha
    elif event == "cleanup-pending":
        if not args.sha:
            raise DashboardError("record cleanup-pending 需要 --sha")
        entry["pendingCleanup"] = {
            "sha": args.sha,
            "createdAt": iso_now(),
            "worktreeRemoved": args.worktree_removed,
            "localBranchDeleted": args.local_branch_deleted,
            "remoteBranchDeleted": args.remote_branch_deleted,
        }
    elif event == "cleanup":
        if not args.sha:
            raise DashboardError("record cleanup 需要 --sha")
        cleanup = {
            "worktreeRemoved": args.worktree_removed,
            "localBranchDeleted": args.local_branch_deleted,
            "remoteBranchDeleted": args.remote_branch_deleted,
        }
        entry["cleanup"] = cleanup
        entry["worktreeRemovedAt"] = iso_now()
        if args.local_branch_deleted and args.remote_branch_deleted:
            entry.update(stage="cleaned", cleanedAt=iso_now(), finalSha=args.sha)
        entry.pop("pendingCleanup", None)
    else:
        raise DashboardError(f"未知记录事件：{event}")
    state["updatedAt"] = iso_now()
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)


def _state_field_unlocked(paths: RuntimePaths, repo_path: str, branch: str, field: str) -> str | None:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    dedupe_repositories(config, state)
    project = find_project(config, repo_path)
    entry = state.get("requirements", {}).get(requirement_key(project["id"], branch), {})
    migrate_legacy_metadata(Path(project["path"]), branch, entry)
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)
    value = entry.get(field)
    if value is not None:
        return str(value)
    return None


def _mark_online_unlocked(paths: RuntimePaths, repo_path: str, branch: str, evidence: str | None) -> dict[str, Any]:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    dedupe_repositories(config, state)
    project = find_project(config, repo_path)
    dashboard = build_dashboard(config, state)
    match = next(
        (
            item
            for item in dashboard["requirements"]
            if item["projectId"] == project["id"] and item["branch"] == branch
        ),
        None,
    )
    if not match or not match.get("sha"):
        raise DashboardError(f"看板中找不到可上线的需求分支：{branch}")
    if match["stage"] not in {"merged-master", "cleaned"} or not match.get("inMaster"):
        raise DashboardError(
            f"需求尚未达到已合主干状态：{branch} stage={match['stage']}"
        )
    key = requirement_key(project["id"], branch)
    entry = state["requirements"][key]
    entry["onlineAt"] = iso_now()
    entry["onlineSha"] = match["sha"]
    entry["onlineEvidence"] = evidence or "用户确认"
    entry.pop("archivedAt", None)
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)
    return _refresh_dashboard_unlocked(paths)


def _archive_requirement_unlocked(paths: RuntimePaths, repo_path: str, branch: str) -> dict[str, Any]:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    dedupe_repositories(config, state)
    project = find_project(config, repo_path)
    key = requirement_key(project["id"], branch)
    entry = state.get("requirements", {}).get(key)
    if not entry or not entry.get("onlineAt"):
        raise DashboardError("只有已上线需求可以手动归档")
    entry["archivedAt"] = iso_now()
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)
    return _refresh_dashboard_unlocked(paths)


def requirement_metadata_entry(
    config: dict[str, Any], state: dict[str, Any], repo_path: str, requirement_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    project = find_project(config, repo_path)
    key = requirement_metadata_key(project["id"], requirement_id)
    return project, state.setdefault("requirementMetadata", {}).setdefault(key, {})


def _set_requirement_title_unlocked(
    paths: RuntimePaths, repo_path: str, requirement_id: str, title: str
) -> dict[str, Any]:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    _, metadata = requirement_metadata_entry(config, state, repo_path, requirement_id)
    metadata.update(
        title=title.strip(),
        fullTitle=title.strip(),
        titleSource="manual",
        titleUpdatedAt=iso_now(),
    )
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)
    return _refresh_dashboard_unlocked(paths)


def _set_primary_branch_unlocked(
    paths: RuntimePaths, repo_path: str, requirement_id: str, branch: str
) -> dict[str, Any]:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    project, metadata = requirement_metadata_entry(config, state, repo_path, requirement_id)
    dashboard = build_dashboard(config, state)
    group = next(
        (
            item
            for item in dashboard["requirements"]
            if item["projectId"] == project["id"] and item["requirementId"] == requirement_id
        ),
        None,
    )
    if not group or branch not in {item["branch"] for item in group.get("branches", [])}:
        raise DashboardError(f"分支不属于该需求：{branch}")
    metadata["primaryBranch"] = branch
    metadata["primaryUpdatedAt"] = iso_now()
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)
    return _refresh_dashboard_unlocked(paths)


def fetch_tapd_title(workspace: str, item_id: str, item_type: str) -> tuple[str, str]:
    executable = shutil.which("agent-tools")
    if not executable:
        raise DashboardError("未安装 agent-tools，无法同步 TAPD 标题")
    command = [executable, "tapd", "story" if item_type == "story" else "show", item_id, "--workspace", workspace, "--json"]
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if completed.returncode != 0:
        raise DashboardError(completed.stderr.strip() or completed.stdout.strip())
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise DashboardError("TAPD 返回的不是有效 JSON") from exc
    full_title = str(payload.get("title") or "").strip()
    if not full_title:
        raise DashboardError("TAPD 未返回需求标题")
    title = re.sub(r"^(?:L\d+\s*)?\[[^]]+\]\s*", "", full_title).strip() or full_title
    return title, full_title


def _sync_requirement_titles_unlocked(
    paths: RuntimePaths,
    repo_path: str | None = None,
    requirement_id: str | None = None,
    force: bool = False,
    fetcher=fetch_tapd_title,
) -> tuple[dict[str, Any], list[str]]:
    config = load_json(paths.config_file, default_config())
    state = load_json(paths.state_file, default_state())
    dashboard = build_dashboard(config, state)
    project_filter = canonical_repo(repo_path) if repo_path else None
    errors: list[str] = []
    for item in dashboard["requirements"]:
        project = next(project for project in config["repositories"] if project["id"] == item["projectId"])
        if project_filter and Path(project["path"]).resolve() != project_filter:
            continue
        if requirement_id and item["requirementId"] != requirement_id:
            continue
        key = requirement_metadata_key(item["projectId"], item["requirementId"])
        metadata = state.setdefault("requirementMetadata", {}).setdefault(key, {})
        if metadata.get("title") and not force:
            continue
        match = re.fullmatch(r"([0-9]+)_([0-9]+)", item["requirementId"])
        if not match:
            # 私人项目没有 TAPD 编号；保留 Git 看板数据，不把它当成同步错误。
            continue
        item_type = "bug" if any("/bug/" in branch["branch"] for branch in item["branches"]) else "story"
        try:
            title, full_title = fetcher(match.group(1), match.group(2), item_type)
        except DashboardError as exc:
            errors.append(f"{item['requirementId']}: {exc}")
            continue
        metadata.update(
            title=title,
            fullTitle=full_title,
            titleSource="tapd",
            titleUpdatedAt=iso_now(),
        )
    save_json(paths.config_file, config)
    save_json(paths.state_file, state)
    return _refresh_dashboard_unlocked(paths), errors


def record_event(paths: RuntimePaths, args: argparse.Namespace) -> None:
    with dashboard_state_lock(paths):
        _record_event_unlocked(paths, args)


def state_field(paths: RuntimePaths, repo_path: str, branch: str, field: str) -> str | None:
    with dashboard_state_lock(paths):
        return _state_field_unlocked(paths, repo_path, branch, field)


def mark_online(
    paths: RuntimePaths, repo_path: str, branch: str, evidence: str | None
) -> dict[str, Any]:
    with dashboard_state_lock(paths):
        return _mark_online_unlocked(paths, repo_path, branch, evidence)


def archive_requirement(
    paths: RuntimePaths, repo_path: str, branch: str
) -> dict[str, Any]:
    with dashboard_state_lock(paths):
        return _archive_requirement_unlocked(paths, repo_path, branch)


def set_requirement_title(
    paths: RuntimePaths, repo_path: str, requirement_id: str, title: str
) -> dict[str, Any]:
    with dashboard_state_lock(paths):
        return _set_requirement_title_unlocked(paths, repo_path, requirement_id, title)


def set_primary_branch(
    paths: RuntimePaths, repo_path: str, requirement_id: str, branch: str
) -> dict[str, Any]:
    with dashboard_state_lock(paths):
        return _set_primary_branch_unlocked(paths, repo_path, requirement_id, branch)


def sync_requirement_titles(
    paths: RuntimePaths,
    repo_path: str | None = None,
    requirement_id: str | None = None,
    force: bool = False,
    fetcher=fetch_tapd_title,
) -> tuple[dict[str, Any], list[str]]:
    with dashboard_state_lock(paths):
        return _sync_requirement_titles_unlocked(
            paths, repo_path, requirement_id, force, fetcher
        )


def print_summary(data: dict[str, Any], html_path: Path) -> None:
    summary = data["summary"]
    print(f"dashboard={html_path}")
    print(f"generated_at={data['generatedAt']}")
    print(f"projects={len(data['projects'])}")
    print(f"requirements={len(data['requirements'])}")
    print(f"active={summary['active']}")
    print(f"attention={summary['attention']}")
    print(f"recently_online={summary['recentlyOnline']}")
    print(f"archived={summary['archived']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="用户级 Git 需求开发看板")
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="登记一个 Git 仓库")
    register.add_argument("--repo", required=True)
    register.add_argument("--name")
    register.add_argument("--base-ref")
    register.add_argument("--dev-ref")
    register.add_argument("--worktree-root")
    register.add_argument("--pattern", action="append", dest="patterns")
    register.add_argument("--recently-online-days", type=int)

    refresh = sub.add_parser("refresh", help="扫描并生成 HTML")
    refresh.add_argument("--repo", help="登记并优先扫描指定仓库")

    sync = sub.add_parser("sync-repo", help="工作流动作后登记仓库并刷新")
    sync.add_argument("--repo", required=True)

    sub.add_parser("open", help="刷新并用默认浏览器打开")

    serve = sub.add_parser("serve", help="启动本地实时看板服务")
    serve.add_argument("--port", type=int, default=0)
    serve.add_argument("--open", action="store_true")

    watch = sub.add_parser("watch", help="前台周期刷新")
    watch.add_argument("--interval", type=float, default=10.0)
    watch.add_argument("--open", action="store_true")

    online = sub.add_parser("mark-online", help="确认需求已上线")
    online.add_argument("--repo", required=True)
    online.add_argument("--branch", required=True)
    online.add_argument("--evidence")

    archive = sub.add_parser("archive", help="手动归档已上线需求")
    archive.add_argument("--repo", required=True)
    archive.add_argument("--branch", required=True)

    title = sub.add_parser("set-title", help="手工设置需求主题")
    title.add_argument("--repo", required=True)
    title.add_argument("--requirement", required=True)
    title.add_argument("--title", required=True)

    primary = sub.add_parser("set-primary", help="设置需求主分支")
    primary.add_argument("--repo", required=True)
    primary.add_argument("--requirement", required=True)
    primary.add_argument("--branch", required=True)

    sync_titles = sub.add_parser("sync-titles", help="显式从 TAPD 同步需求标题")
    sync_titles.add_argument("--repo")
    sync_titles.add_argument("--requirement")
    sync_titles.add_argument("--force", action="store_true")

    record = sub.add_parser("record", help=argparse.SUPPRESS)
    record.add_argument("--repo", required=True)
    record.add_argument("--branch", required=True)
    record.add_argument(
        "--event",
        required=True,
        choices=["start", "dev-integration", "dev-result", "beta-integration", "stage", "cleanup-pending", "cleanup"],
    )
    record.add_argument("--sha")
    record.add_argument("--base-sha")
    record.add_argument("--worktree")
    record.add_argument("--target")
    record.add_argument("--result")
    record.add_argument("--stage")
    record.add_argument("--pushed", action="store_true")
    record.add_argument("--worktree-removed", action="store_true")
    record.add_argument("--local-branch-deleted", action="store_true")
    record.add_argument("--remote-branch-deleted", action="store_true")

    get_state = sub.add_parser("state-get", help=argparse.SUPPRESS)
    get_state.add_argument("--repo", required=True)
    get_state.add_argument("--branch", required=True)
    get_state.add_argument("--field", required=True)

    preflight = sub.add_parser("preflight", help=argparse.SUPPRESS)
    preflight.add_argument("--repo", required=True)

    sub.add_parser("show-path", help="输出 HTML 路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        paths = runtime_paths()
        if args.command == "register":
            with dashboard_state_lock(paths):
                config = load_json(paths.config_file, default_config())
                if args.recently_online_days is not None:
                    if args.recently_online_days < 0:
                        raise DashboardError("recently-online-days 不能小于 0")
                    config["recentlyOnlineDays"] = args.recently_online_days
                item, changed = register_repository(
                    config,
                    args.repo,
                    args.name,
                    base_ref=args.base_ref,
                    dev_ref=args.dev_ref,
                    worktree_root=args.worktree_root,
                    patterns=validate_patterns(args.patterns) if args.patterns else None,
                )
                save_json(paths.config_file, config)
                data = _refresh_dashboard_unlocked(paths)
            print(f"registered={str(changed).lower()}")
            print(f"project_id={item['id']}")
            print_summary(data, paths.html_file)
        elif args.command in {"refresh", "sync-repo"}:
            repo = args.repo if hasattr(args, "repo") else None
            data = refresh_dashboard(paths, repo)
            print_summary(data, paths.html_file)
        elif args.command == "open":
            data = refresh_dashboard(paths)
            webbrowser.open(paths.html_file.resolve().as_uri())
            print_summary(data, paths.html_file)
        elif args.command == "serve":
            serve_dashboard(paths, args.port, args.open)
        elif args.command == "watch":
            if args.interval < 1:
                raise DashboardError("watch interval 不能小于 1 秒")
            first = True
            try:
                while True:
                    data = refresh_dashboard(paths)
                    if first and args.open:
                        webbrowser.open(paths.html_file.resolve().as_uri())
                    first = False
                    print_summary(data, paths.html_file)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("watch=stopped")
        elif args.command == "mark-online":
            data = mark_online(paths, args.repo, args.branch, args.evidence)
            print_summary(data, paths.html_file)
        elif args.command == "archive":
            data = archive_requirement(paths, args.repo, args.branch)
            print_summary(data, paths.html_file)
        elif args.command == "set-title":
            data = set_requirement_title(paths, args.repo, args.requirement, args.title)
            print_summary(data, paths.html_file)
        elif args.command == "set-primary":
            data = set_primary_branch(paths, args.repo, args.requirement, args.branch)
            print_summary(data, paths.html_file)
        elif args.command == "sync-titles":
            data, errors = sync_requirement_titles(
                paths, args.repo, args.requirement, args.force
            )
            print_summary(data, paths.html_file)
            for error in errors:
                print(f"WARNING: {error}", file=sys.stderr)
            if args.requirement and errors:
                return 1
        elif args.command == "record":
            record_event(paths, args)
            print("recorded=true")
        elif args.command == "state-get":
            value = state_field(paths, args.repo, args.branch, args.field)
            if value is not None:
                print(value)
        elif args.command == "preflight":
            with dashboard_state_lock(paths):
                config = load_json(paths.config_file, default_config())
                state = load_json(paths.state_file, default_state())
                dedupe_repositories(config, state)
                register_repository(config, args.repo)
                save_json(paths.config_file, config)
                save_json(paths.state_file, state)
            print("preflight=passed")
        elif args.command == "show-path":
            print(paths.html_file)
        return 0
    except DashboardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
