from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import hashlib
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/wl-git-requirement-flow/scripts/dashboard.py"
SPEC = importlib.util.spec_from_file_location("wl_git_requirement_dashboard", MODULE_PATH)
assert SPEC and SPEC.loader
DASHBOARD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DASHBOARD
SPEC.loader.exec_module(DASHBOARD)


def run(*args: str | Path, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def git(repo: Path, *args: str, check: bool = True) -> str:
    return run("git", "-C", repo, *args, check=check).stdout.strip()


def configure_identity(repo: Path) -> None:
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.com")


def init_repo(tmp_path: Path, name: str = "repo") -> tuple[Path, Path, Path]:
    origin = tmp_path / f"{name}-origin.git"
    seed = tmp_path / f"{name}-seed"
    repo = tmp_path / name
    run("git", "init", "--bare", "--initial-branch=master", origin)
    run("git", "clone", origin, seed)
    configure_identity(seed)
    (seed / "app.txt").write_text("base\n", encoding="utf-8")
    git(seed, "add", "app.txt")
    git(seed, "commit", "-m", "chore: baseline")
    git(seed, "push", "origin", "master")
    git(seed, "switch", "-c", "feature/dev")
    git(seed, "push", "-u", "origin", "feature/dev")
    git(seed, "switch", "-c", "feature/beta", "master")
    git(seed, "push", "-u", "origin", "feature/beta")
    run("git", "clone", origin, repo)
    configure_identity(repo)
    return origin, seed, repo


@pytest.fixture
def xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    roots = {
        "config": tmp_path / "xdg-config",
        "state": tmp_path / "xdg-state",
        "data": tmp_path / "xdg-data",
    }
    monkeypatch.setenv("XDG_CONFIG_HOME", str(roots["config"]))
    monkeypatch.setenv("XDG_STATE_HOME", str(roots["state"]))
    monkeypatch.setenv("XDG_DATA_HOME", str(roots["data"]))
    return roots


def create_story(repo: Path, tmp_path: Path, branch: str = "feature/story/44973445_1073308") -> Path:
    worktree = tmp_path / "worktrees" / branch.rsplit("/", 1)[-1]
    git(repo, "worktree", "add", "-b", branch, worktree, "origin/master")
    git(repo, "config", f"branch.{branch}.requirementFlowBaseSha", git(repo, "rev-parse", "origin/master"))
    with (worktree / "app.txt").open("a", encoding="utf-8") as handle:
        handle.write("story\n")
    git(worktree, "add", "app.txt")
    git(worktree, "commit", "-m", "feat: story")
    git(worktree, "push", "-u", "origin", branch)
    return worktree


def requirement_by_branch(data: dict, branch: str) -> dict:
    return next(
        item
        for item in data["requirements"]
        if item.get("branch") == branch
        or any(candidate["branch"] == branch for candidate in item.get("branches", []))
    )


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_register_refresh_and_render_user_level_html(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073308"
    create_story(repo, tmp_path, branch)
    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    item, changed = DASHBOARD.register_repository(config, repo, "Compass Test")
    assert changed is True
    DASHBOARD.save_json(paths.config_file, config)

    data = DASHBOARD.refresh_dashboard(paths)
    requirement = requirement_by_branch(data, branch)
    assert requirement["projectName"] == "Compass Test"
    assert requirement["stage"] == "ready-dev"
    assert requirement["worktreePath"]
    assert "outside-worktree-root" in {item["code"] for item in requirement["anomalies"]}
    assert data["summary"]["active"] == 1
    assert data["summary"]["dev"] == 1
    assert paths.html_file.exists()
    html = paths.html_file.read_text(encoding="utf-8")
    assert "{{DATA_JSON}}" not in html
    assert branch in html
    assert "http://" not in html and "https://" not in html
    assert json.loads(paths.config_file.read_text(encoding="utf-8"))["repositories"][0]["id"] == item["id"]

    updated, changed = DASHBOARD.register_repository(
        config,
        repo,
        base_ref="origin/main",
        dev_ref="origin/develop",
        worktree_root=str(tmp_path / "custom-worktrees"),
        patterns=[r"^story/[0-9]+$"],
    )
    assert changed is True
    assert updated["baseRef"] == "origin/main"
    assert updated["devRef"] == "origin/develop"
    assert updated["requirementPatterns"] == [r"^story/[0-9]+$"]


def test_linked_worktree_registers_as_the_same_project(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    story = create_story(repo, tmp_path)
    config = DASHBOARD.default_config()
    main_project, _ = DASHBOARD.register_repository(config, repo)
    linked_project, changed = DASHBOARD.register_repository(config, story)
    assert changed is False
    assert main_project["id"] == linked_project["id"]
    assert len(config["repositories"]) == 1
    assert Path(config["repositories"][0]["path"]) == repo.resolve()


def test_refresh_does_not_rewrite_worktree_index(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    story = create_story(repo, tmp_path)
    git_dir = Path(git(story, "rev-parse", "--git-dir"))
    if not git_dir.is_absolute():
        git_dir = (story / git_dir).resolve()
    index = git_dir / "index"
    before_hash = file_hash(index)
    before_mtime = index.stat().st_mtime_ns

    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    DASHBOARD.refresh_dashboard(paths)

    assert file_hash(index) == before_hash
    assert index.stat().st_mtime_ns == before_mtime


def test_git_lifecycle_online_archive_and_reopen(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073308"
    story = create_story(repo, tmp_path, branch)
    dev = tmp_path / "dev-worktree"
    git(repo, "worktree", "add", "-b", "feature/dev", dev, "origin/feature/dev")
    git(dev, "merge", "--no-ff", "--no-edit", branch)
    git(dev, "push", "origin", "feature/dev")
    story_sha = git(repo, "rev-parse", branch)
    git(repo, "config", f"branch.{branch}.requirementFlowStage", "dev-passed")
    git(repo, "config", f"branch.{branch}.requirementFlowLastDevSha", story_sha)
    git(repo, "config", f"branch.{branch}.requirementFlowDevPassedSha", story_sha)

    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    data = DASHBOARD.refresh_dashboard(paths)
    assert requirement_by_branch(data, branch)["stage"] == "dev-passed"

    with (story / "app.txt").open("a", encoding="utf-8") as handle:
        handle.write("after-test\n")
    git(story, "add", "app.txt")
    git(story, "commit", "-m", "fix: after dev")
    git(story, "push", "origin", branch)
    data = DASHBOARD.refresh_dashboard(paths)
    stale = requirement_by_branch(data, branch)
    assert stale["stage"] == "ready-dev"
    assert "stale-dev-test" in {item["code"] for item in stale["anomalies"]}

    git(repo, "merge", "--no-ff", "--no-edit", branch)
    git(repo, "push", "origin", "master")
    git(repo, "fetch", "origin")
    data = DASHBOARD.refresh_dashboard(paths)
    assert requirement_by_branch(data, branch)["stage"] == "merged-master"

    DASHBOARD.mark_online(paths, str(repo), branch, "人工确认上线")
    data = DASHBOARD.refresh_dashboard(paths)
    online = requirement_by_branch(data, branch)
    assert online["stage"] == "online"
    assert online["visibility"] == "recently-online"

    state = DASHBOARD.load_json(paths.state_file, DASHBOARD.default_state())
    key = DASHBOARD.requirement_key(online["projectId"], online["primaryBranch"])
    state["requirements"][key]["onlineAt"] = (
        datetime.now(timezone.utc) - timedelta(days=8)
    ).isoformat(timespec="seconds")
    DASHBOARD.save_json(paths.state_file, state)
    data = DASHBOARD.refresh_dashboard(paths)
    assert requirement_by_branch(data, branch)["stage"] == "archived"

    with (story / "app.txt").open("a", encoding="utf-8") as handle:
        handle.write("reopen\n")
    git(story, "add", "app.txt")
    git(story, "commit", "-m", "fix: reopen")
    data = DASHBOARD.refresh_dashboard(paths)
    reopened = requirement_by_branch(data, branch)
    assert reopened["visibility"] == "active"
    assert "reopened" in {item["code"] for item in reopened["anomalies"]}


def test_detached_and_unmanaged_worktrees_are_attention_items(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    detached = tmp_path / "detached"
    unmanaged = tmp_path / "integration"
    git(repo, "worktree", "add", "--detach", detached, "origin/master")
    git(repo, "worktree", "add", "-b", "integration/h001-dev", unmanaged, "origin/master")

    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    data = DASHBOARD.refresh_dashboard(paths)
    codes = {item["code"] for item in data["anomalies"]}
    assert "detached-worktree" in codes
    assert "unmanaged-worktree" in codes
    assert data["summary"]["attention"] >= 2


def test_repository_unavailable_keeps_error_visible(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073308"
    create_story(repo, tmp_path, branch)
    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    project, _ = DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    first = DASHBOARD.refresh_dashboard(paths)
    assert requirement_by_branch(first, branch)["stage"] == "ready-dev"
    missing = tmp_path / "repo-moved"
    repo.rename(missing)
    data = DASHBOARD.refresh_dashboard(paths)
    assert data["errors"]
    assert "仓库路径不存在" in data["errors"][0]["message"]
    stale = requirement_by_branch(data, branch)
    assert stale["sha"]
    assert "missing-repository" in {item["code"] for item in stale["anomalies"]}
    assert stale["projectId"] == project["id"]


def test_remote_only_historical_branches_do_not_clutter_active_board(
    tmp_path: Path, xdg: dict[str, Path]
) -> None:
    _, seed, repo = init_repo(tmp_path)
    git(seed, "switch", "-c", "feature/story/44973445_1000001", "master")
    git(seed, "push", "origin", "feature/story/44973445_1000001")
    git(repo, "fetch", "origin")

    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    data = DASHBOARD.refresh_dashboard(paths)
    assert not any(item["branch"].endswith("1000001") for item in data["requirements"])


def test_invalid_branch_pattern_is_reported_without_overwriting_state(
    tmp_path: Path, xdg: dict[str, Path]
) -> None:
    _, _, repo = init_repo(tmp_path)
    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    item, _ = DASHBOARD.register_repository(config, repo)
    item["requirementPatterns"] = ["["]
    DASHBOARD.save_json(paths.config_file, config)
    data = DASHBOARD.refresh_dashboard(paths)
    assert data["errors"]
    assert "无效的需求分支正则" in data["errors"][0]["message"]


def test_relative_xdg_paths_are_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", ".config")
    with pytest.raises(DASHBOARD.DashboardError, match="必须是绝对路径"):
        DASHBOARD.runtime_paths()


def test_structurally_invalid_json_is_rejected_without_rewrite(
    tmp_path: Path, xdg: dict[str, Path]
) -> None:
    paths = DASHBOARD.runtime_paths()
    paths.config_file.parent.mkdir(parents=True)
    paths.config_file.write_text("[]\n", encoding="utf-8")
    before = paths.config_file.read_bytes()
    with pytest.raises(DASHBOARD.DashboardError, match="根节点必须是对象"):
        DASHBOARD.refresh_dashboard(paths)
    assert paths.config_file.read_bytes() == before


def test_embedded_json_escapes_html_breakout_sequences(
    tmp_path: Path, xdg: dict[str, Path]
) -> None:
    _, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073308"
    create_story(repo, tmp_path, branch)
    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    project, _ = DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    DASHBOARD.refresh_dashboard(paths)
    state = DASHBOARD.load_json(paths.state_file, DASHBOARD.default_state())
    key = DASHBOARD.requirement_metadata_key(project["id"], "44973445_1073308")
    state["requirementMetadata"][key] = {
        "title": "</script><img src=x onerror=alert(1)>"
    }
    DASHBOARD.save_json(paths.state_file, state)
    DASHBOARD.refresh_dashboard(paths)
    html = paths.html_file.read_text(encoding="utf-8")
    assert "</script><img" not in html
    assert "\\u003c/script\\u003e" in html


def test_online_confirmation_survives_final_branch_cleanup(tmp_path: Path, xdg: dict[str, Path]) -> None:
    origin, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073308"
    story = create_story(repo, tmp_path, branch)
    git(repo, "merge", "--no-ff", "--no-edit", branch)
    git(repo, "push", "origin", "master")
    git(repo, "fetch", "origin")

    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    before = DASHBOARD.refresh_dashboard(paths)
    assert requirement_by_branch(before, branch)["stage"] == "merged-master"

    git(repo, "worktree", "remove", story)
    git(repo, "push", "origin", "--delete", branch)
    git(repo, "branch", "-d", branch)
    git(repo, "fetch", "--prune", "origin")
    after_cleanup = DASHBOARD.refresh_dashboard(paths)
    assert requirement_by_branch(after_cleanup, branch)["stage"] == "merged-master"

    state = DASHBOARD.load_json(paths.state_file, DASHBOARD.default_state())
    project_id = after_cleanup["requirements"][0]["projectId"]
    entry = state["requirements"][DASHBOARD.requirement_key(project_id, branch)]
    entry["stage"] = "cleaned"
    entry["cleanedAt"] = DASHBOARD.iso_now()
    DASHBOARD.save_json(paths.state_file, state)
    cleaned = DASHBOARD.refresh_dashboard(paths)
    assert requirement_by_branch(cleaned, branch)["stage"] == "cleaned"

    online = DASHBOARD.mark_online(paths, str(repo), branch, "发布确认")
    item = requirement_by_branch(online, branch)
    assert item["stage"] == "online"
    assert item["onlineEvidence"] == "发布确认"
    assert run("git", "ls-remote", "--exit-code", "--heads", origin, branch, check=False).returncode != 0

    archived = DASHBOARD.archive_requirement(paths, str(repo), branch)
    assert requirement_by_branch(archived, branch)["stage"] == "archived"


def test_existing_duplicate_project_records_are_merged(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    story = create_story(repo, tmp_path)
    paths = DASHBOARD.runtime_paths()
    primary = DASHBOARD.default_repo_config(repo)
    duplicate = dict(primary, id="legacy-duplicate", path=str(story))
    config = DASHBOARD.default_config()
    config["repositories"] = [primary, duplicate]
    state = DASHBOARD.default_state()
    branch = "feature/story/44973445_1073308"
    state["requirements"][DASHBOARD.requirement_key(duplicate["id"], branch)] = {
        "projectId": duplicate["id"],
        "repoPath": duplicate["path"],
        "branch": branch,
        "managed": True,
        "stage": "dev-passed",
        "devPassedSha": git(repo, "rev-parse", branch),
    }
    DASHBOARD.save_json(paths.config_file, config)
    DASHBOARD.save_json(paths.state_file, state)
    DASHBOARD.refresh_dashboard(paths)
    config = DASHBOARD.load_json(paths.config_file, DASHBOARD.default_config())
    state = DASHBOARD.load_json(paths.state_file, DASHBOARD.default_state())
    assert len(config["repositories"]) == 1
    assert all(entry["projectId"] == primary["id"] for entry in state["requirements"].values())


def test_unmerged_branch_disappearance_is_marked_missing(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073308"
    story = create_story(repo, tmp_path, branch)
    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    DASHBOARD.refresh_dashboard(paths)

    git(repo, "worktree", "remove", story)
    git(repo, "push", "origin", "--delete", branch)
    git(repo, "branch", "-D", branch)
    git(repo, "fetch", "--prune", "origin")
    data = DASHBOARD.refresh_dashboard(paths)
    missing = requirement_by_branch(data, branch)
    assert missing["stage"] == "missing"
    assert "missing-branch" in {item["code"] for item in missing["anomalies"]}


def test_same_requirement_branches_are_grouped_and_active_worktree_is_primary(
    tmp_path: Path, xdg: dict[str, Path]
) -> None:
    _, _, repo = init_repo(tmp_path)
    original = "feature/story/44973445_1073445"
    original_wt = create_story(repo, tmp_path, original)
    dev = tmp_path / "dev-group"
    git(repo, "worktree", "add", "-b", "feature/dev", dev, "origin/feature/dev")
    git(dev, "merge", "--no-ff", "--no-edit", original)
    git(dev, "push", "origin", "feature/dev")
    git(repo, "worktree", "remove", original_wt)

    clean = "feature/story/44973445_1073445-clean-20260920"
    clean_wt = tmp_path / "clean-worktree"
    git(repo, "worktree", "add", "-b", clean, clean_wt, "origin/master")
    with (clean_wt / "topic.txt").open("w", encoding="utf-8") as handle:
        handle.write("topic\n")
    git(clean_wt, "add", "topic.txt")
    git(clean_wt, "commit", "-m", "feat(h005): 航线代码和运输条款展示与查询")

    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    data = DASHBOARD.refresh_dashboard(paths)
    matches = [item for item in data["requirements"] if item["requirementId"] == "44973445_1073445"]
    assert len(matches) == 1
    requirement = matches[0]
    assert requirement["branchCount"] == 2
    assert requirement["primaryBranch"] == clean
    assert requirement["stage"] == "active"
    assert requirement["title"] == "航线代码和运输条款展示与查询"
    assert "multiple-requirement-branches" in {item["code"] for item in requirement["anomalies"]}
    assert "secondary-branch-in-dev" in {item["code"] for item in requirement["anomalies"]}

    changed = DASHBOARD.set_primary_branch(
        paths, str(repo), "44973445_1073445", original
    )
    requirement = next(item for item in changed["requirements"] if item["requirementId"] == "44973445_1073445")
    assert requirement["primaryBranch"] == original
    assert requirement["stage"] == "dev-testing"


def test_tapd_title_sync_is_explicit_and_cached(tmp_path: Path, xdg: dict[str, Path]) -> None:
    _, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073445"
    create_story(repo, tmp_path, branch)
    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    DASHBOARD.refresh_dashboard(paths)
    calls = []

    def fake_fetcher(workspace: str, item_id: str, item_type: str) -> tuple[str, str]:
        calls.append((workspace, item_id, item_type))
        return (
            "航线代码和运输条款展示与查询",
            "L3 [R-20260910-H005] 航线代码和运输条款展示与查询",
        )

    data, errors = DASHBOARD.sync_requirement_titles(
        paths,
        str(repo),
        "44973445_1073445",
        fetcher=fake_fetcher,
    )
    assert errors == []
    assert calls == [("44973445", "1073445", "story")]
    requirement = next(item for item in data["requirements"] if item["requirementId"] == "44973445_1073445")
    assert requirement["title"] == "航线代码和运输条款展示与查询"
    assert requirement["titleSource"] == "tapd"


def test_cross_process_lock_prevents_refresh_from_overwriting_new_event(
    tmp_path: Path, xdg: dict[str, Path]
) -> None:
    _, _, repo = init_repo(tmp_path)
    branch = "feature/story/44973445_1073308"
    create_story(repo, tmp_path, branch)
    paths = DASHBOARD.runtime_paths()
    config = DASHBOARD.default_config()
    DASHBOARD.register_repository(config, repo)
    DASHBOARD.save_json(paths.config_file, config)
    DASHBOARD.refresh_dashboard(paths)
    sha = git(repo, "rev-parse", branch)

    script = tmp_path / "hold_refresh_lock.py"
    script.write_text(
        f"""
import importlib.util, sys, time
from pathlib import Path
spec=importlib.util.spec_from_file_location('dashboard_lock_child', {str(MODULE_PATH)!r})
module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
paths=module.RuntimePaths(Path({str(paths.config_file)!r}), Path({str(paths.state_file)!r}), Path({str(paths.html_file)!r}))
with module.dashboard_state_lock(paths):
    print('locked', flush=True)
    time.sleep(0.8)
    module._refresh_dashboard_unlocked(paths)
""",
        encoding="utf-8",
    )
    child = subprocess.Popen(
        [str(Path(sys.executable)), str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert child.stdout is not None
    assert child.stdout.readline().strip() == "locked"
    args = type(
        "Args",
        (),
        {
            "repo": str(repo),
            "branch": branch,
            "event": "dev-result",
            "sha": sha,
            "base_sha": None,
            "worktree": None,
            "target": None,
            "result": "passed",
            "stage": None,
            "pushed": False,
            "worktree_removed": False,
            "local_branch_deleted": False,
            "remote_branch_deleted": False,
        },
    )()
    started = time.monotonic()
    DASHBOARD.record_event(paths, args)
    elapsed = time.monotonic() - started
    stdout, stderr = child.communicate(timeout=5)
    assert child.returncode == 0, stderr
    assert elapsed >= 0.5
    state = DASHBOARD.load_json(paths.state_file, DASHBOARD.default_state())
    entry = next(item for item in state["requirements"].values() if item["branch"] == branch)
    assert entry["stage"] == "dev-passed"
    assert entry["devPassedSha"] == sha
