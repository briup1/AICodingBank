from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/skills/engineering/wl-git-flow/scripts/wl-git-flow.sh"


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
    assert "codegraph=not-enabled" in output
    assert not (worktree / ".codegraph").exists()
    assert worktree == worktree_root / repo.name / "story-login-redesign"
    assert git(worktree, "branch", "--show-current").stdout == "feature/story/login-redesign\n"


@pytest.mark.parametrize("requirement", ["R-20260910-F001", "R-20260910-F001.md", "R-20261016-login-fix"])
def test_start_reuses_restores_and_tracks_remote_requirement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, requirement: str
) -> None:
    configure_dashboard_env(tmp_path, monkeypatch)
    origin, repo, dev_worktree, _ = init_fixture(tmp_path)
    root = tmp_path / "worktrees"
    requirement_id = requirement.removesuffix(".md")
    branch = f"feature/{requirement_id}"
    worktree = root / repo.name / branch
    args = (SCRIPT, "start", "--repo", repo, "--id", requirement, "--worktree-root", root)
    created = run(*args).stdout
    assert "status=created" in created and "ready=true" in created
    assert f"worktree={worktree}" in created
    assert git(worktree, "branch", "--show-current").stdout.strip() == branch
    assert git(worktree, "rev-parse", "HEAD").stdout == git(repo, "rev-parse", "origin/master").stdout
    assert not (worktree / f"{requirement_id}.md").exists()

    # Reuse must preserve uncommitted work and the recorded test result.
    (worktree / "local.txt").write_text("keep me")
    reused = run(*args).stdout
    assert "status=reused" in reused
    assert (worktree / "local.txt").read_text() == "keep me"
    git(worktree, "add", "local.txt")
    git(worktree, "commit", "-m", "feat: requirement")
    sha = git(worktree, "rev-parse", "HEAD").stdout.strip()
    run(SCRIPT, "integrate-dev", "--repo", repo, "--source", branch,
        "--target", "feature/dev", "--target-worktree", dev_worktree,
        "--push-source", "--push-target")
    run(SCRIPT, "mark-dev-result", "--repo", repo, "--branch", branch, "--result", "passed")
    run(*args)
    state = json.loads((tmp_path / "state/wl-git-flow/state.json").read_text())
    entry = next(item for item in state["requirements"].values() if item["branch"] == branch)
    assert entry["stage"] == "dev-passed" and entry["devPassedSha"] == sha

    run(SCRIPT, "remove-worktree", "--repo", repo, "--worktree", worktree, "--confirm")
    assert not worktree.exists()
    assert git(repo, "rev-parse", branch).stdout.strip() == sha
    assert sha in run("git", "ls-remote", "--heads", origin, branch).stdout
    restored = run(*args).stdout
    assert "status=restored" in restored
    assert git(worktree, "rev-parse", "HEAD").stdout.strip() == sha

    # Another clone has only the remote branch; start must not reset it to master.
    clone = tmp_path / "other-repo"
    run("git", "clone", origin, clone)
    remote_restored = run(SCRIPT, "start", "--repo", clone, "--id", requirement,
                          "--worktree-root", root).stdout
    assert "status=restored" in remote_restored
    assert git(clone, "rev-parse", branch).stdout.strip() == sha
    assert git(clone, "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{branch}").stdout.strip() == f"origin/{branch}"


@pytest.mark.parametrize("case", ["occupied", "mismatch", "invalid"])
def test_start_rejects_requirement_conflicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    configure_dashboard_env(tmp_path, monkeypatch)
    _, repo, _, _ = init_fixture(tmp_path)
    root = tmp_path / "worktrees"
    requirement = "R-20261016-login-fix"
    extra = []
    if case == "occupied":
        (root / repo.name / f"feature/{requirement}").mkdir(parents=True)
    elif case == "mismatch":
        extra = ["--branch", "feature/R-20261016-other"]
    else:
        requirement = "R-20261016-../escape"
    result = run(SCRIPT, "start", "--repo", repo, "--id", requirement,
                 "--worktree-root", root, *extra, check=False)
    assert result.returncode != 0
    assert git(repo, "show-ref", "--verify", "refs/heads/feature/R-20261016-login-fix", check=False).returncode != 0


@pytest.mark.parametrize("mode", ["ready", "build-failed", "partial", "wrong-root", "not-initialized"])
@pytest.mark.parametrize("bootstrap", [False, True])
def test_start_builds_independent_codegraph(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str, bootstrap: bool
) -> None:
    import os

    configure_dashboard_env(tmp_path, monkeypatch)
    _, repo, _, _ = init_fixture(tmp_path)
    (repo / ".codegraph").mkdir()
    (repo / ".codegraph/source-only").write_text("never copy")
    (repo / ".wl-git-flow-bootstrap").write_text(".codegraph\n")
    hooks = Path(git(repo, "rev-parse", "--git-common-dir").stdout.strip())
    if not hooks.is_absolute():
        hooks = repo / hooks
    hook_files = {p.name: p.read_bytes() for p in (hooks / "hooks").iterdir()}
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "codegraph"
    fake.write_text('''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
cmd = sys.argv[1]
p = pathlib.Path(sys.argv[-1])
assert os.environ["CODEGRAPH_DIR"] == ".codegraph"
if cmd == "init":
    assert sys.argv[2] == "--yes"
    assert pathlib.Path.cwd() == p
    hook = subprocess.check_output(["git", "config", "core.hooksPath"], text=True).strip()
    assert hook == str(p / ".codegraph/git-hooks")
    assert not (p / ".codegraph/source-only").exists()
    (p / ".codegraph").mkdir(exist_ok=True)
    (p / ".codegraph/built-here").write_text(str(p))
    sys.exit(1 if os.environ["CG_TEST_MODE"] == "build-failed" else 0)
assert cmd == "status"
mode = os.environ["CG_TEST_MODE"]
print(json.dumps({"initialized": mode != "not-initialized", "projectPath": str(p.parent if mode == "wrong-root" else p),
    "indexPath": str(p / ".codegraph"), "lastIndexed": "now", "pendingChanges": {},
    "index": {"state": "partial" if mode == "partial" else "complete", "pendingRefs": 0}}))
''')
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CG_TEST_MODE", mode)
    result = run(SCRIPT, "start", "--repo", repo, "--id", "cg-test",
                 "--worktree-root", tmp_path / "worktrees",
                 *(["--bootstrap"] if bootstrap else []), check=False)
    worktree = tmp_path / "worktrees/repo/story-cg-test"
    assert worktree.is_dir()
    assert (repo / ".codegraph/source-only").read_text() == "never copy"
    assert (worktree / ".codegraph/built-here").read_text() == str(worktree)
    assert not (worktree / ".codegraph/source-only").exists()
    assert git(worktree, "branch", "--show-current").stdout.strip() == "feature/story/cg-test"
    assert {p.name: p.read_bytes() for p in (hooks / "hooks").iterdir()} == hook_files
    assert git(repo, "config", "--local", "--get", "core.hooksPath", check=False).returncode != 0
    assert (tmp_path / "data/wl-git-flow/dashboard.html").exists()
    if mode == "ready":
        assert result.returncode == 0, result.stdout
        assert "codegraph=ready" in result.stdout
        marker = worktree / ".codegraph/built-here"
        before = marker.stat().st_mtime_ns
        reused = run(SCRIPT, "start", "--repo", repo, "--id", "cg-test",
                     "--worktree-root", tmp_path / "worktrees", "--bootstrap")
        assert "status=reused" in reused.stdout and "ready=true" in reused.stdout
        assert marker.stat().st_mtime_ns == before
        monkeypatch.setenv("CG_TEST_MODE", "partial")
        blocked = run(SCRIPT, "start", "--repo", repo, "--id", "cg-test",
                      "--worktree-root", tmp_path / "worktrees", check=False)
        assert blocked.returncode != 0 and "ready=false" in blocked.stdout
        assert marker.stat().st_mtime_ns == before
    else:
        assert result.returncode != 0
        assert "codegraph=not-ready" in result.stdout
        assert "Do not rerun start" in result.stdout


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

def test_requirement_flow_and_cleanup_keeps_branches(
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
    assert "branch deletion is not supported" in premature_retirement.stdout
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
    assert "recommendation=ASK_REMOVE_WORKTREE_KEEP_BRANCH" in final_plan

    retired = run(
        SCRIPT,
        "remove-worktree",
        "--repo",
        repo,
        "--worktree",
        worktree,
        "--confirm",
    ).stdout
    assert "local_branch_deleted=false" in retired
    assert "remote_branch_deleted=false" in retired
    assert not worktree.exists()
    assert git(repo, "show-ref", "--verify", f"refs/heads/{branch}").returncode == 0
    assert run("git", "ls-remote", "--exit-code", "--heads", origin, branch).returncode == 0
    state_path = tmp_path / "state/wl-git-flow/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    entry = next(item for item in state["requirements"].values() if item["branch"] == branch)
    assert entry["stage"] == "beta-testing"
    assert "cleanedAt" not in entry
    assert entry["cleanup"] == {
        "worktreeRemoved": True,
        "localBranchDeleted": False,
        "remoteBranchDeleted": False,
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
    config = tmp_path / "config/wl-git-flow/config.json"
    html = tmp_path / "data/wl-git-flow/dashboard.html"
    assert config.exists()
    assert html.exists()
    assert "feature/story/44973445_1073308" in html.read_text(encoding="utf-8")


@pytest.mark.parametrize("unsafe", ["dirty", "remote-ahead", "remote-missing"])
def test_cleanup_rechecks_local_and_remote_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unsafe: str
) -> None:
    configure_dashboard_env(tmp_path, monkeypatch)
    origin, repo, _, _ = init_fixture(tmp_path)
    branch = "feature/R-20261016-login-fix"
    root = tmp_path / "worktrees"
    worktree = root / repo.name / branch
    run(SCRIPT, "start", "--repo", repo, "--id", "R-20261016-login-fix", "--worktree-root", root)
    git(worktree, "push", "-u", "origin", branch)
    if unsafe == "dirty":
        (worktree / "unsaved.txt").write_text("keep")
    elif unsafe == "remote-missing":
        run("git", "--git-dir", origin, "update-ref", "-d", f"refs/heads/{branch}")
    else:
        writer = tmp_path / "writer"
        run("git", "clone", origin, writer)
        git(writer, "config", "user.name", "Test")
        git(writer, "config", "user.email", "test@example.com")
        git(writer, "switch", branch)
        (writer / "new.txt").write_text("remote update")
        git(writer, "add", "new.txt")
        git(writer, "commit", "-m", "fix: remote update")
        git(writer, "push", "origin", branch)
    rejected = run(SCRIPT, "remove-worktree", "--repo", repo,
                   "--worktree", worktree, "--confirm", check=False)
    assert rejected.returncode != 0
    assert worktree.exists()
    assert git(repo, "show-ref", "--verify", f"refs/heads/{branch}").returncode == 0


def test_cleanup_rejects_branch_retirement(
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
    state_path = tmp_path / "state/wl-git-flow/state.json"
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
        check=False,
    )
    assert retired.returncode != 0
    assert "branch deletion is not supported" in retired.stdout
    assert git(repo, "show-ref", "--verify", f"refs/heads/{branch}").returncode == 0
    assert run("git", "ls-remote", "--exit-code", "--heads", origin, branch).returncode == 0
