#!/usr/bin/env bash
set -euo pipefail

PROGRAM=${0##*/}
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
DASHBOARD_SCRIPT="$SCRIPT_DIR/dashboard.py"

usage() {
  cat <<'USAGE'
Usage:
  wl-git-flow.sh start --repo PATH --id REQUIREMENT_ID [--worktree-root PATH] [--branch NAME]
      REQUIREMENT_ID: TAPD PROJECT_STORY (数字_数字) 或私人项目 slug (如 login-redesign)
  wl-git-flow.sh integrate-dev --repo PATH --source BRANCH --target BRANCH --target-worktree PATH [--push-source] [--push-target]
  wl-git-flow.sh promote --repo PATH --source BRANCH --target BRANCH --target-worktree PATH [--push-target] [--base origin/master] [--dev origin/feature/dev]
  wl-git-flow.sh mark-dev-result --repo PATH --branch BRANCH --result passed|failed
  wl-git-flow.sh mark-stage --repo PATH --branch BRANCH --stage paused|beta-testing|beta-passed|released
  wl-git-flow.sh audit --repo PATH --branch BRANCH [--base origin/master] [--dev origin/feature/dev]
  wl-git-flow.sh cleanup-plan --repo PATH --branch BRANCH [--dev feature/dev] [--beta BRANCH] [--base origin/master]
  wl-git-flow.sh remove-worktree --repo PATH --worktree PATH --confirm [--delete-local-branch] [--delete-remote-branch] [--final-target REF]
  wl-git-flow.sh retire-branch --repo PATH --branch BRANCH --confirm --final-target REF
  wl-git-flow.sh dashboard register|refresh|open|serve|watch|mark-online|archive|show-path [OPTIONS]
  wl-git-flow.sh dashboard serve [--port 0] [--open]

The script never force-pushes. Normal cleanup removes only the Worktree directory and keeps branches.
USAGE
}

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
note() { printf '%s\n' "$*"; }

run_dashboard() {
  command -v uv >/dev/null 2>&1 || fail "uv is required for the dashboard (Python 3.12.9)"
  uv run --no-project --python 3.12.9 python "$DASHBOARD_SCRIPT" "$@"
}

dashboard_sync_repo() {
  [[ "${WL_GIT_REQUIREMENT_DASHBOARD_DISABLE:-0}" != 1 ]] || return 0
  if ! run_dashboard sync-repo --repo "$1" >/dev/null; then
    printf 'WARNING: Git operation succeeded, but dashboard refresh failed for %s\n' "$1" >&2
  fi
}

repo=""
require_repo() {
  [[ -n "$repo" ]] || fail "--repo is required"
  repo=$(cd "$repo" 2>/dev/null && pwd -P) || fail "repo path does not exist: $repo"
  git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 || fail "not a Git repository: $repo"
  local main_worktree
  main_worktree=$(git -C "$repo" worktree list --porcelain | awk '/^worktree /{print substr($0,10); exit}')
  [[ -n "$main_worktree" ]] && repo=$main_worktree
}

require_ref() {
  git -C "$repo" rev-parse --verify --quiet "$1^{commit}" >/dev/null || fail "ref not found: $1"
}

require_story_branch() {
  [[ "$1" =~ ^feature/story/[a-z0-9][a-z0-9._-]*$ ]] || fail "invalid story branch: $1 (expected feature/story/<requirement-id>)"
}

operation_in_progress() {
  local git_dir
  git_dir=$(git -C "$1" rev-parse --git-dir)
  [[ "$git_dir" = /* ]] || git_dir="$(cd "$1" && pwd -P)/$git_dir"
  [[ -e "$git_dir/MERGE_HEAD" || -d "$git_dir/rebase-merge" || -d "$git_dir/rebase-apply" || -e "$git_dir/CHERRY_PICK_HEAD" ]]
}

worktree_for_branch() {
  local wanted="refs/heads/$1" path="" branch=""
  while IFS= read -r line; do
    case "$line" in
      worktree\ *) path=${line#worktree } ;;
      branch\ *)
        branch=${line#branch }
        if [[ "$branch" == "$wanted" ]]; then printf '%s\n' "$path"; return 0; fi
        ;;
      '') path=""; branch="" ;;
    esac
  done < <(git -C "$repo" worktree list --porcelain; printf '\n')
  return 1
}

branch_stage_get() {
  run_dashboard state-get --repo "$repo" --branch "$1" --field stage 2>/dev/null || true
}

branch_meta_get() {
  run_dashboard state-get --repo "$repo" --branch "$1" --field "$2" 2>/dev/null || true
}

fetch_branch_if_remote_exists() {
  local branch=$1
  if git -C "$repo" ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
    git -C "$repo" fetch --quiet origin "$branch:refs/remotes/origin/$branch"
    return 0
  fi
  return 1
}

cmd_start() {
  local id="" root="${GIT_REQUIREMENT_WORKTREE_ROOT:-$HOME/workdir/worktrees}" branch=""
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --id) id=$2; shift 2 ;;
      --worktree-root) root=$2; shift 2 ;;
      --branch) branch=$2; shift 2 ;;
      *) fail "unknown start argument: $1" ;;
    esac
  done
  require_repo
  run_dashboard preflight --repo "$repo" >/dev/null
  [[ "$id" =~ ^[a-z0-9][a-z0-9._-]*$ ]] || fail "--id must contain only lowercase letters, numbers, dot, underscore, or hyphen"
  branch=${branch:-feature/story/$id}
  require_story_branch "$branch"
  local repo_name path
  repo_name=$(basename "$(git -C "$repo" rev-parse --show-toplevel)")
  path="$root/$repo_name/story-$id"
  [[ ! -e "$path" ]] || fail "worktree path already exists: $path"
  git -C "$repo" show-ref --verify --quiet "refs/heads/$branch" && fail "local branch already exists: $branch"
  git -C "$repo" fetch --prune origin master
  git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$branch" && fail "remote branch already exists: origin/$branch"
  mkdir -p "$(dirname "$path")"
  git -C "$repo" worktree add -b "$branch" "$path" origin/master
  path=$(git -C "$path" rev-parse --show-toplevel)
  local base_sha
  base_sha=$(git -C "$repo" rev-parse origin/master)
  run_dashboard record --repo "$repo" --branch "$branch" --event start --base-sha "$base_sha" --worktree "$path" >/dev/null
  note "status=created"
  note "branch=$branch"
  note "worktree=$path"
  note "base=origin/master"
  note "base_sha=$base_sha"
  dashboard_sync_repo "$repo"
}

cmd_integrate_dev() {
  local source="" target="" target_wt="" push_source=0 push_target=0
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --source) source=$2; shift 2 ;;
      --target) target=$2; shift 2 ;;
      --target-worktree) target_wt=$2; shift 2 ;;
      --push-source) push_source=1; shift ;;
      --push-target) push_target=1; shift ;;
      *) fail "unknown integrate-dev argument: $1" ;;
    esac
  done
  require_repo
  run_dashboard preflight --repo "$repo" >/dev/null
  require_story_branch "$source"
  [[ -n "$target" && -n "$target_wt" ]] || fail "--source, --target and --target-worktree are required"
  [[ "$source" != "$target" ]] || fail "source and target must differ"
  require_ref "$source"
  target_wt=$(cd "$target_wt" 2>/dev/null && pwd -P) || fail "target worktree does not exist"
  local actual_branch
  actual_branch=$(git -C "$target_wt" symbolic-ref --quiet --short HEAD || true)
  [[ "$actual_branch" == "$target" ]] || fail "target worktree is on '$actual_branch', expected '$target'"
  [[ -z "$(git -C "$target_wt" status --porcelain)" ]] || fail "target worktree is not clean: $target_wt"
  operation_in_progress "$target_wt" && fail "target worktree has an in-progress Git operation"

  git -C "$repo" fetch --prune origin master "$target"
  local source_sha
  source_sha=$(git -C "$repo" rev-parse "$source")

  if ((push_source)); then
    git -C "$repo" push -u origin "refs/heads/$source:refs/heads/$source"
  fi
  fetch_branch_if_remote_exists "$source" || fail "source is not present on origin; rerun with --push-source"
  [[ "$(git -C "$repo" rev-parse "$source")" == "$(git -C "$repo" rev-parse "origin/$source")" ]] || fail "source differs from origin/$source; push or reconcile it first"

  git -C "$target_wt" merge --ff-only "origin/$target"
  git -C "$target_wt" merge --no-ff --no-edit "$source"

  [[ "$(git -C "$repo" rev-parse "$source")" == "$source_sha" ]] || fail "source SHA changed during target integration"
  git -C "$repo" merge-base --is-ancestor "$source_sha" "$target" || fail "target does not contain source SHA after merge"

  if ((push_target)); then
    git -C "$target_wt" push origin "HEAD:refs/heads/$target"
  fi
  local record_args=(record --repo "$repo" --branch "$source" --event dev-integration --sha "$source_sha" --target "$target")
  if ((push_target)); then record_args+=(--pushed); fi
  run_dashboard "${record_args[@]}" >/dev/null
  note "status=$([[ $push_target -eq 1 ]] && echo dev-testing || echo checkpointed)"
  note "source=$source"
  note "source_sha=$source_sha"
  note "target=$target"
  note "target_sha=$(git -C "$repo" rev-parse "$target")"
  note "source_unchanged=true"
  note "source_pushed=$([[ $push_source -eq 1 ]] && echo true || echo false)"
  note "target_pushed=$([[ $push_target -eq 1 ]] && echo true || echo false)"
  dashboard_sync_repo "$repo"
}

cmd_promote() {
  local source="" target="" target_wt="" push_target=0 base="origin/master" dev="origin/feature/dev"
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --source) source=$2; shift 2 ;;
      --target) target=$2; shift 2 ;;
      --target-worktree) target_wt=$2; shift 2 ;;
      --push-target) push_target=1; shift ;;
      --base) base=$2; shift 2 ;;
      --dev) dev=$2; shift 2 ;;
      *) fail "unknown promote argument: $1" ;;
    esac
  done
  require_repo
  run_dashboard preflight --repo "$repo" >/dev/null
  require_story_branch "$source"
  [[ -n "$target" && -n "$target_wt" ]] || fail "--source, --target and --target-worktree are required"
  [[ "$source" != "$target" ]] || fail "source and target must differ"
  "$0" audit --repo "$repo" --branch "$source" --base "$base" --dev "$dev"
  fetch_branch_if_remote_exists "$source" || fail "source is not present on origin"
  [[ "$(git -C "$repo" rev-parse "$source")" == "$(git -C "$repo" rev-parse "origin/$source")" ]] || fail "source differs from origin/$source"

  target_wt=$(cd "$target_wt" 2>/dev/null && pwd -P) || fail "target worktree does not exist"
  local actual_branch source_sha
  actual_branch=$(git -C "$target_wt" symbolic-ref --quiet --short HEAD || true)
  [[ "$actual_branch" == "$target" ]] || fail "target worktree is on '$actual_branch', expected '$target'"
  [[ -z "$(git -C "$target_wt" status --porcelain)" ]] || fail "target worktree is not clean: $target_wt"
  operation_in_progress "$target_wt" && fail "target worktree has an in-progress Git operation"
  git -C "$repo" fetch --prune origin "+refs/heads/$target:refs/remotes/origin/$target"
  source_sha=$(git -C "$repo" rev-parse "$source")
  git -C "$target_wt" merge --ff-only "origin/$target"
  git -C "$target_wt" merge --no-ff --no-edit "$source"
  [[ "$(git -C "$repo" rev-parse "$source")" == "$source_sha" ]] || fail "source SHA changed during promotion"
  git -C "$repo" merge-base --is-ancestor "$source_sha" "$target" || fail "target does not contain source SHA after promotion"
  if ((push_target)); then
    git -C "$target_wt" push origin "HEAD:refs/heads/$target"
  fi
  local record_args=(record --repo "$repo" --branch "$source" --event beta-integration --sha "$source_sha" --target "$target")
  if ((push_target)); then record_args+=(--pushed); fi
  run_dashboard "${record_args[@]}" >/dev/null
  note "status=$([[ $push_target -eq 1 ]] && echo beta-testing || echo promoted-locally)"
  note "source=$source"
  note "source_sha=$source_sha"
  note "target=$target"
  note "target_sha=$(git -C "$repo" rev-parse "$target")"
  note "source_unchanged=true"
  note "target_pushed=$([[ $push_target -eq 1 ]] && echo true || echo false)"
  dashboard_sync_repo "$repo"
}

cmd_mark_dev_result() {
  local branch="" result=""
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --branch) branch=$2; shift 2 ;;
      --result) result=$2; shift 2 ;;
      *) fail "unknown mark-dev-result argument: $1" ;;
    esac
  done
  require_repo
  run_dashboard preflight --repo "$repo" >/dev/null
  require_story_branch "$branch"
  require_ref "$branch"
  [[ "$result" == passed || "$result" == failed ]] || fail "--result must be passed or failed"
  local current_sha last_dev_sha
  current_sha=$(git -C "$repo" rev-parse "$branch")
  last_dev_sha=$(branch_meta_get "$branch" lastDevSha)
  [[ -n "$last_dev_sha" ]] || fail "no recorded Dev integration for $branch"
  [[ "$current_sha" == "$last_dev_sha" ]] || fail "branch advanced after the last Dev integration; integrate the current SHA before recording a result"
  run_dashboard record --repo "$repo" --branch "$branch" --event dev-result --sha "$current_sha" --result "$result" >/dev/null
  note "status=dev-$result"
  note "branch=$branch"
  note "sha=$current_sha"
  dashboard_sync_repo "$repo"
}

cmd_mark_stage() {
  local branch="" stage=""
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --branch) branch=$2; shift 2 ;;
      --stage) stage=$2; shift 2 ;;
      *) fail "unknown mark-stage argument: $1" ;;
    esac
  done
  require_repo
  run_dashboard preflight --repo "$repo" >/dev/null
  require_story_branch "$branch"
  require_ref "$branch"
  case "$stage" in paused|beta-testing|beta-passed|released) ;; *) fail "unsupported stage: $stage" ;; esac
  if [[ "$stage" == beta-passed ]]; then
    local last_beta_sha current_sha
    last_beta_sha=$(branch_meta_get "$branch" lastBetaSha)
    current_sha=$(git -C "$repo" rev-parse "$branch")
    [[ -n "$last_beta_sha" && "$last_beta_sha" == "$current_sha" ]] || fail "current SHA was not the last recorded Beta integration"
  fi
  local record_args=(record --repo "$repo" --branch "$branch" --event stage --stage "$stage")
  if [[ "$stage" == beta-passed ]]; then record_args+=(--sha "$current_sha"); fi
  run_dashboard "${record_args[@]}" >/dev/null
  note "status=$stage"
  note "branch=$branch"
  note "sha=$(git -C "$repo" rev-parse "$branch")"
  dashboard_sync_repo "$repo"
}

cmd_audit() {
  local branch="" base="origin/master" dev="origin/feature/dev"
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --branch) branch=$2; shift 2 ;;
      --base) base=$2; shift 2 ;;
      --dev) dev=$2; shift 2 ;;
      *) fail "unknown audit argument: $1" ;;
    esac
  done
  require_repo
  require_story_branch "$branch"
  git -C "$repo" fetch --prune origin
  require_ref "$branch"; require_ref "$base"
  local failed=0 merge parents parent passed_sha current_sha
  current_sha=$(git -C "$repo" rev-parse "$branch")
  note "branch=$branch"
  note "branch_sha=$current_sha"
  note "base=$base"
  note "unique_commits=$(git -C "$repo" rev-list --count "$base..$branch")"

  if git -C "$repo" rev-parse --verify --quiet "$dev^{commit}" >/dev/null && git -C "$repo" merge-base --is-ancestor "$dev" "$branch"; then
    note "ERROR: full Dev ref is an ancestor of the requirement branch"
    failed=1
  fi

  while IFS= read -r merge; do
    [[ -n "$merge" ]] || continue
    read -r -a parents <<<"$(git -C "$repo" show -s --format='%P' "$merge")"
    for parent in "${parents[@]:1}"; do
      if ! git -C "$repo" merge-base --is-ancestor "$parent" "$base"; then
        note "ERROR: foreign merge parent merge=$merge parent=$parent"
        failed=1
      fi
    done
  done < <(git -C "$repo" rev-list --merges "$base..$branch")

  passed_sha=$(branch_meta_get "$branch" devPassedSha)
  if [[ -n "$passed_sha" && "$passed_sha" != "$current_sha" ]]; then
    note "ERROR: Dev-passed SHA is stale: passed=$passed_sha current=$current_sha"
    failed=1
  fi

  note "--- commits unique to branch ---"
  git -C "$repo" log --oneline --decorate "$base..$branch"
  note "--- diff stat ---"
  git -C "$repo" diff --stat "$base...$branch"
  ((failed == 0)) || fail "audit failed; do not promote this branch"
  note "audit=passed"
}

cmd_cleanup_plan() {
  local branch="" dev="feature/dev" beta="" base="origin/master"
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --branch) branch=$2; shift 2 ;;
      --dev) dev=$2; shift 2 ;;
      --beta) beta=$2; shift 2 ;;
      --base) base=$2; shift 2 ;;
      *) fail "unknown cleanup-plan argument: $1" ;;
    esac
  done
  require_repo
  require_story_branch "$branch"
  git -C "$repo" fetch --prune origin >/dev/null
  require_ref "$branch"
  local wt="" dirty=false in_progress=false upstream="" sync_state="no-upstream" stage current_sha passed_sha
  wt=$(worktree_for_branch "$branch" || true)
  if [[ -n "$wt" ]]; then
    [[ -z "$(git -C "$wt" status --porcelain)" ]] || dirty=true
    operation_in_progress "$wt" && in_progress=true
  fi
  upstream=$(git -C "$repo" for-each-ref --format='%(upstream:short)' "refs/heads/$branch")
  if [[ -n "$upstream" ]] && git -C "$repo" rev-parse --verify --quiet "$upstream^{commit}" >/dev/null; then
    local counts ahead behind
    counts=$(git -C "$repo" rev-list --left-right --count "$upstream...$branch")
    behind=${counts%%[[:space:]]*}; ahead=${counts##*[[:space:]]}
    sync_state="ahead=$ahead,behind=$behind"
  fi
  stage=$(branch_stage_get "$branch")
  current_sha=$(git -C "$repo" rev-parse "$branch")
  passed_sha=$(branch_meta_get "$branch" devPassedSha)

  note "branch=$branch"
  note "sha=$current_sha"
  note "stage=${stage:-unknown}"
  note "worktree=${wt:-none}"
  note "dirty=$dirty"
  note "operation_in_progress=$in_progress"
  note "upstream=${upstream:-none}"
  note "sync=$sync_state"

  if [[ "$dirty" == true || "$in_progress" == true ]]; then
    note "recommendation=KEEP"
    note "reason=worktree has local state or an in-progress Git operation"
    return
  fi
  if [[ -z "$upstream" || "$sync_state" != "ahead=0,behind=0" ]]; then
    note "recommendation=KEEP"
    note "reason=branch is not fully synchronized with its upstream"
    return
  fi
  if git -C "$repo" rev-parse --verify --quiet "$base^{commit}" >/dev/null && git -C "$repo" merge-base --is-ancestor "$current_sha" "$base"; then
    note "recommendation=ASK_REMOVE_WORKTREE_KEEP_BRANCH"
    note "reason=current requirement SHA is contained in $base; remove the worktree directory only and keep local and remote branches"
    return
  fi
  if [[ -n "$beta" ]] && git -C "$repo" rev-parse --verify --quiet "$beta^{commit}" >/dev/null && git -C "$repo" merge-base --is-ancestor "$current_sha" "$beta"; then
    note "recommendation=ASK_REMOVE_WORKTREE_KEEP_BRANCH"
    note "reason=current requirement SHA is contained in Beta but not final base"
    return
  fi
  if [[ "$stage" == dev-testing || "$stage" == dev-failed || "$stage" == checkpointed || "$stage" == active ]]; then
    note "recommendation=KEEP"
    note "reason=lifecycle stage still expects development or Dev feedback"
    return
  fi
  if [[ "$stage" == dev-passed && -n "$passed_sha" && "$passed_sha" == "$current_sha" ]]; then
    note "recommendation=ASK_REMOVE_WORKTREE_KEEP_BRANCH"
    note "reason=Dev passed for the current SHA; keep by default if Beta promotion is imminent"
    return
  fi
  if [[ "$stage" == dev-passed && -n "$passed_sha" && "$passed_sha" != "$current_sha" ]]; then
    note "recommendation=KEEP"
    note "reason=the branch advanced after the recorded Dev pass; integrate and retest the current SHA"
    return
  fi
  if [[ "$stage" == paused ]]; then
    note "recommendation=ASK_REMOVE_WORKTREE_KEEP_BRANCH"
    note "reason=paused and fully synchronized"
    return
  fi
  if git -C "$repo" rev-parse --verify --quiet "$dev^{commit}" >/dev/null && git -C "$repo" merge-base --is-ancestor "$current_sha" "$dev"; then
    note "recommendation=ASK_TEST_STATUS"
    note "reason=Git shows the SHA in Dev, but environment test result is unknown"
    return
  fi
  note "recommendation=KEEP"
  note "reason=no verified cleanup milestone"
}

cmd_remove_worktree() {
  local wt="" confirm=0 delete_local=0 delete_remote=0 final_target=""
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --worktree) wt=$2; shift 2 ;;
      --confirm) confirm=1; shift ;;
      --delete-local-branch) delete_local=1; shift ;;
      --delete-remote-branch) delete_remote=1; shift ;;
      --final-target) final_target=$2; shift 2 ;;
      *) fail "unknown remove-worktree argument: $1" ;;
    esac
  done
  require_repo
  run_dashboard preflight --repo "$repo" >/dev/null
  ((confirm)) || fail "--confirm is required after user approval"
  [[ -n "$wt" ]] || fail "--worktree is required"
  wt=$(cd "$wt" 2>/dev/null && pwd -P) || fail "worktree path does not exist"
  local main_root branch registered=false
  main_root=$(git -C "$repo" rev-parse --show-toplevel)
  [[ "$wt" != "$main_root" ]] || fail "refusing to remove the main worktree"
  branch=$(git -C "$wt" symbolic-ref --quiet --short HEAD || true)
  [[ -n "$branch" ]] || fail "refusing to remove a detached worktree"
  while IFS= read -r line; do [[ "$line" == "worktree $wt" ]] && registered=true; done < <(git -C "$repo" worktree list --porcelain)
  [[ "$registered" == true ]] || fail "path is not a registered worktree: $wt"
  [[ -z "$(git -C "$wt" status --porcelain)" ]] || fail "worktree is not clean"
  operation_in_progress "$wt" && fail "worktree has an in-progress Git operation"
  local upstream counts ahead behind
  upstream=$(git -C "$repo" for-each-ref --format='%(upstream:short)' "refs/heads/$branch")
  [[ -n "$upstream" ]] || fail "branch has no upstream; refusing cleanup"
  counts=$(git -C "$repo" rev-list --left-right --count "$upstream...$branch")
  behind=${counts%%[[:space:]]*}; ahead=${counts##*[[:space:]]}
  [[ "$ahead" == 0 && "$behind" == 0 ]] || fail "branch is not synchronized with upstream: ahead=$ahead behind=$behind"

  if ((delete_local || delete_remote)); then
    [[ -n "$final_target" ]] || fail "--final-target is required when deleting a branch"
    require_ref "$final_target"
    git -C "$repo" merge-base --is-ancestor "$branch" "$final_target" || fail "branch tip is not contained in final target: $final_target"
  fi
  if ((delete_remote)); then
    [[ "$upstream" == "origin/$branch" ]] || fail "remote deletion requires the same-name origin upstream"
    git -C "$repo" ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1 || fail "remote branch not found: origin/$branch"
  fi

  run_dashboard sync-repo --repo "$repo" >/dev/null
  local final_sha
  final_sha=$(git -C "$repo" rev-parse "$branch")
  local pending_args=(record --repo "$repo" --branch "$branch" --event cleanup-pending --sha "$final_sha" --worktree-removed)
  if ((delete_local)); then pending_args+=(--local-branch-deleted); fi
  if ((delete_remote)); then pending_args+=(--remote-branch-deleted); fi
  run_dashboard "${pending_args[@]}" >/dev/null

  git -C "$repo" worktree remove "$wt"
  git -C "$repo" worktree prune
  if ((delete_remote)); then git -C "$repo" push origin --delete "$branch"; fi
  if ((delete_local)); then git -C "$repo" branch -d "$branch"; fi
  local cleanup_args=(record --repo "$repo" --branch "$branch" --event cleanup --sha "$final_sha" --worktree-removed)
  if ((delete_local)); then cleanup_args+=(--local-branch-deleted); fi
  if ((delete_remote)); then cleanup_args+=(--remote-branch-deleted); fi
  run_dashboard "${cleanup_args[@]}" >/dev/null
  note "status=removed"
  note "worktree=$wt"
  note "branch=$branch"
  note "local_branch_deleted=$([[ $delete_local -eq 1 ]] && echo true || echo false)"
  note "remote_branch_deleted=$([[ $delete_remote -eq 1 ]] && echo true || echo false)"
  dashboard_sync_repo "$repo"
}

cmd_retire_branch() {
  local branch="" confirm=0 final_target=""
  while (($#)); do
    case "$1" in
      --repo) repo=$2; shift 2 ;;
      --branch) branch=$2; shift 2 ;;
      --confirm) confirm=1; shift ;;
      --final-target) final_target=$2; shift 2 ;;
      *) fail "unknown retire-branch argument: $1" ;;
    esac
  done
  require_repo
  run_dashboard preflight --repo "$repo" >/dev/null
  ((confirm)) || fail "--confirm is required after user approval"
  require_story_branch "$branch"
  [[ -n "$final_target" ]] || fail "--final-target is required"
  require_ref "$branch"
  require_ref "$final_target"
  if worktree_for_branch "$branch" >/dev/null 2>&1; then
    fail "branch still has a Worktree; use remove-worktree for final retirement"
  fi
  local upstream counts ahead behind final_sha
  upstream=$(git -C "$repo" for-each-ref --format='%(upstream:short)' "refs/heads/$branch")
  [[ "$upstream" == "origin/$branch" ]] || fail "branch must track the same-name origin branch"
  counts=$(git -C "$repo" rev-list --left-right --count "$upstream...$branch")
  behind=${counts%%[[:space:]]*}; ahead=${counts##*[[:space:]]}
  [[ "$ahead" == 0 && "$behind" == 0 ]] || fail "branch is not synchronized with upstream: ahead=$ahead behind=$behind"
  git -C "$repo" merge-base --is-ancestor "$branch" "$final_target" || fail "branch tip is not contained in final target: $final_target"
  git -C "$repo" ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1 || fail "remote branch not found: origin/$branch"
  run_dashboard sync-repo --repo "$repo" >/dev/null
  final_sha=$(git -C "$repo" rev-parse "$branch")
  run_dashboard record --repo "$repo" --branch "$branch" --event cleanup-pending --sha "$final_sha" --worktree-removed --local-branch-deleted --remote-branch-deleted >/dev/null
  git -C "$repo" push origin --delete "$branch"
  git -C "$repo" branch -d "$branch"
  run_dashboard record --repo "$repo" --branch "$branch" --event cleanup --sha "$final_sha" --worktree-removed --local-branch-deleted --remote-branch-deleted >/dev/null
  note "status=retired"
  note "branch=$branch"
  note "local_branch_deleted=true"
  note "remote_branch_deleted=true"
  dashboard_sync_repo "$repo"
}

(($#)) || { usage; exit 1; }
command=$1; shift
case "$command" in
  start) cmd_start "$@" ;;
  integrate-dev) cmd_integrate_dev "$@" ;;
  promote) cmd_promote "$@" ;;
  mark-dev-result) cmd_mark_dev_result "$@" ;;
  mark-stage) cmd_mark_stage "$@" ;;
  audit) cmd_audit "$@" ;;
  cleanup-plan) cmd_cleanup_plan "$@" ;;
  remove-worktree) cmd_remove_worktree "$@" ;;
  retire-branch) cmd_retire_branch "$@" ;;
  dashboard) run_dashboard "$@" ;;
  -h|--help|help) usage ;;
  *) usage >&2; fail "unknown command: $command" ;;
esac
