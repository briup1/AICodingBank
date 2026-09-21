from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/wl-git-requirement-flow/scripts/wl-git-requirement-flow.sh"


def run(*args: str | Path, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("git", "-C", repo, *args, check=check)


def init_fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    repo = tmp_path / "repo"
    dev_worktree = tmp_path / "dev-worktree"
    beta_worktree = tmp_path / "beta-worktree"

    run("git", "init", "--bare", "--initial-branch=master", origin)
    run("git", "clone", origin, seed)
    git(seed, "config", "user.name", "Test")
    git(seed, "config", "user.email", "test@example.com")
    (seed / "app.txt").write_text("base\n", encoding="utf-8")
    git(seed, "add", "app.txt")
    git(seed, "commit", "-m", "chore: baseline")
    git(seed, "push", "origin", "master")
    git(seed, "switch", "-c", "feature/dev")
    git(seed, "push", "-u", "origin", "feature/dev")
    git(seed, "switch", "-c", "feature/beta", "master")
    git(seed, "push", "-u", "origin", "feature/beta")

    run("git", "clone", origin, repo)
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "worktree", "add", "-b", "feature/dev", dev_worktree, "origin/feature/dev")
    git(repo, "worktree", "add", "-b", "feature/beta", beta_worktree, "origin/feature/beta")
    return origin, repo, dev_worktree, beta_worktree


def configure_dashboard_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))



def test_private_project_slug_uses_shared_worktree_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_dashboard_env(tmp_path, monkeypatch)
    _, repo, _, _ = init_fixture(tmp_path)
    worktree_root = tmp_path / "worktrees"
    output = run(
        SCRIPT,
        "start",
        "--repo",
        repo,
        "--id",
        "login-redesign",
        "--worktree-root",
        worktree_root,
    ).stdout
    worktree = Path(next(line.split("=", 1)[1] for line in output.splitlines() if line.startswith("worktree=")))
    assert worktree == worktree_root / repo.name / "story-login-redesign"
    assert git(worktree, "branch", "--show-current").stdout == "feature/story/login-redesign\n"


def test_private_requirement_is_not_a_tapd_title_sync_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_dashboard_env(tmp_path, monkeypatch)
    _, repo, _, _ = init_fixture(tmp_path)
    run(
        SCRIPT,
        "start",
        "--repo",
        repo,
        "--id",
        "login-redesign",
        "--worktree-root",
        tmp_path / "worktrees",
    )
    synced = run(SCRIPT, "dashboard", "sync-titles", "--repo", repo).stdout
    assert "WARNING:" not in synced

def test_requirement_flow_and_final_retirement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_dashboard_env(tmp_path, monkeypatch)
    origin, repo, dev_worktree, beta_worktree = init_fixture(tmp_path)
    start = run(
        SCRIPT,
        "start",
        "--repo",
        repo,
        "--id",
        "44973445_1073308",
        "--worktree-root",
        tmp_path / "worktrees",
    ).stdout
    worktree = Path(next(line.split("=", 1)[1] for line in start.splitlines() if line.startswith("worktree=")))
    branch = "feature/story/44973445_1073308"
    with (worktree / "app.txt").open("a", encoding="utf-8") as handle:
        handle.write("story\n")
    git(worktree, "add", "app.txt")
    git(worktree, "commit", "-m", "feat: story change --story=1073308@tapd-44973445")

    integrated = run(
        SCRIPT,
        "integrate-dev",
        "--repo",
        repo,
        "--source",
        branch,
        "--target",
        "feature/dev",
        "--target-worktree",
        dev_worktree,
        "--push-source",
        "--push-target",
    ).stdout
    assert "source_unchanged=true" in integrated
    run(SCRIPT, "mark-dev-result", "--repo", repo, "--branch", branch, "--result", "passed")
    legacy = git(
        repo,
        "config",
        "--local",
        "--get-regexp",
        rf"^branch\.{branch}\.requirementFlow",
        check=False,
    )
    assert legacy.returncode != 0
    plan = run(SCRIPT, "cleanup-plan", "--repo", repo, "--branch", branch).stdout
    assert "recommendation=ASK_REMOVE_WORKTREE_KEEP_BRANCH" in plan

    premature_retirement = run(
        SCRIPT,
        "remove-worktree",
        "--repo",
        repo,
        "--worktree",
        worktree,
        "--confirm",
        "--delete-local-branch",
        "--delete-remote-branch",
        "--final-target",
        "origin/master",
        check=False,
    )
    assert premature_retirement.returncode != 0
    assert "not contained in final target" in premature_retirement.stdout
    assert worktree.exists()
    assert run("git", "ls-remote", "--exit-code", "--heads", origin, branch).returncode == 0

    audit = run(SCRIPT, "audit", "--repo", repo, "--branch", branch).stdout
    assert "audit=passed" in audit
    promoted = run(
        SCRIPT,
        "promote",
        "--repo",
        repo,
        "--source",
        branch,
        "--target",
        "feature/beta",
        "--target-worktree",
        beta_worktree,
        "--push-target",
    ).stdout
    assert "source_unchanged=true" in promoted

    git(repo, "merge", "--no-ff", "--no-edit", branch)
    git(repo, "push", "origin", "master")
    git(repo, "fetch", "origin")
    final_plan = run(SCRIPT, "cleanup-plan", "--repo", repo, "--branch", branch).stdout
    assert "recommendation=ASK_FINAL_RETIRE" in final_plan

    retired = run(
        SCRIPT,
        "remove-worktree",
        "--repo",
        repo,
        "--worktree",
        worktree,
        "--confirm",
        "--delete-local-branch",
        "--delete-remote-branch",
        "--final-target",
        "origin/master",
    ).stdout
    assert "local_branch_deleted=true" in retired
    assert "remote_branch_deleted=true" in retired
    assert not worktree.exists()
    assert git(repo, "show-ref", "--verify", f"refs/heads/{branch}", check=False).returncode != 0
    assert run("git", "ls-remote", "--exit-code", "--heads", origin, branch, check=False).returncode != 0
    state_path = tmp_path / "state/wl-git-requirement-flow/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    entry = next(item for item in state["requirements"].values() if item["branch"] == branch)
    assert entry["stage"] == "cleaned"
    assert entry["cleanup"] == {
        "worktreeRemoved": True,
        "localBranchDeleted": True,
        "remoteBranchDeleted": True,
    }


def test_audit_rejects_dev_merged_back_into_story(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_dashboard_env(tmp_path, monkeypatch)
    _, repo, dev_worktree, _ = init_fixture(tmp_path)
    foreign = tmp_path / "foreign"
    git(dev_worktree, "switch", "feature/dev")
    (dev_worktree / "dev-only.txt").write_text("unapproved\n", encoding="utf-8")
    git(dev_worktree, "add", "dev-only.txt")
    git(dev_worktree, "commit", "-m", "feat: unrelated dev change")
    git(dev_worktree, "push", "origin", "feature/dev")

    git(repo, "worktree", "add", "-b", "feature/story/44973445_999999", foreign, "origin/master")
    git(foreign, "merge", "--no-ff", "--no-edit", "feature/dev")
    audit = run(
        SCRIPT,
        "audit",
        "--repo",
        repo,
        "--branch",
        "feature/story/44973445_999999",
        check=False,
    )
    assert audit.returncode != 0
    assert "full Dev ref is an ancestor" in audit.stdout
    assert "audit failed" in audit.stdout


def test_start_auto_registers_and_refreshes_dashboard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo, _, _ = init_fixture(tmp_path)
    configure_dashboard_env(tmp_path, monkeypatch)
    run(
        SCRIPT,
        "start",
        "--repo",
        repo,
        "--id",
        "44973445_1073308",
        "--worktree-root",
        tmp_path / "worktrees",
    )
    config = tmp_path / "config/wl-git-requirement-flow/config.json"
    html = tmp_path / "data/wl-git-requirement-flow/dashboard.html"
    assert config.exists()
    assert html.exists()
    assert "feature/story/44973445_1073308" in html.read_text(encoding="utf-8")


def test_soft_cleanup_then_retire_branch_without_recreating_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    origin, repo, _, _ = init_fixture(tmp_path)
    configure_dashboard_env(tmp_path, monkeypatch)
    output = run(
        SCRIPT,
        "start",
        "--repo",
        repo,
        "--id",
        "44973445_1073308",
        "--worktree-root",
        tmp_path / "worktrees",
    ).stdout
    worktree = Path(next(line.split("=", 1)[1] for line in output.splitlines() if line.startswith("worktree=")))
    branch = "feature/story/44973445_1073308"
    with (worktree / "app.txt").open("a", encoding="utf-8") as handle:
        handle.write("story\n")
    git(worktree, "add", "app.txt")
    git(worktree, "commit", "-m", "feat: story")
    git(worktree, "push", "-u", "origin", branch)
    git(repo, "merge", "--no-ff", "--no-edit", branch)
    git(repo, "push", "origin", "master")
    git(repo, "fetch", "origin")

    run(SCRIPT, "remove-worktree", "--repo", repo, "--worktree", worktree, "--confirm")
    state_path = tmp_path / "state/wl-git-requirement-flow/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    entry = next(item for item in state["requirements"].values() if item["branch"] == branch)
    assert "cleanedAt" not in entry
    assert entry["cleanup"]["worktreeRemoved"] is True

    retired = run(
        SCRIPT,
        "retire-branch",
        "--repo",
        repo,
        "--branch",
        branch,
        "--confirm",
        "--final-target",
        "origin/master",
    ).stdout
    assert "status=retired" in retired
    assert run("git", "ls-remote", "--exit-code", "--heads", origin, branch, check=False).returncode != 0
    state = json.loads(state_path.read_text(encoding="utf-8"))
    entry = next(item for item in state["requirements"].values() if item["branch"] == branch)
    assert entry["stage"] == "cleaned"
