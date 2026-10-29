#!/usr/bin/env bash
# compass 本地自测 · 定点清理（wl-compass-local-test）
#
# 生成物位置约定（可控制）：
#   根目录 = ${COMPASS_LOCAL_TEST_HOME:-~/.local/state/compass-local-test}/<worktree-slug>
#   每次测试的所有产出只落在这个根下：logs/ artifacts/ mq/
#
# 用法：
#   local-test-down.sh [slug]     停本需求进程，默认保留全部证据且不动共享 MQ
#   --delete-artifacts           独立显式授权删除本 slug 生成物（不影响外部证据目录）
#   --stop-shared-mq --confirm-shared-unused   确认无其他使用者后停共享 MQ
#   --purge                      在以上共享件授权基础上删 MQ 容器/volume，不删证据
#   slug 缺省时取当前目录名；参数校验在任何停机/删除前完成
set -uo pipefail
BASE="${COMPASS_LOCAL_TEST_HOME:-$HOME/.local/state/compass-local-test}"
PURGE=0 DELETE_ARTIFACTS=0 STOP_SHARED=0 SHARED_UNUSED=0
SLUG="$(basename "$PWD")"
SLUG_SET=0
fail() { echo "拒绝操作: $*" >&2; exit 1; }
for a in "$@"; do
  case "$a" in
    --purge) PURGE=1 ;;
    --delete-artifacts) DELETE_ARTIFACTS=1 ;;
    --stop-shared-mq) STOP_SHARED=1 ;;
    --confirm-shared-unused) SHARED_UNUSED=1 ;;
    --*) fail "未知参数 $a" ;;
    *) [ "$SLUG_SET" = 0 ] || fail '只允许一个 slug'; SLUG="$a"; SLUG_SET=1 ;;
  esac
done
[[ "$SLUG" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]] || fail 'slug 必须是单个安全目录名'
[[ "$BASE" = /* && "$BASE" != / ]] || fail 'BASE 必须为非根绝对路径'
case "$BASE/" in *'/../'*|*'/./'*|*'//'*) fail 'BASE 不得含路径穿越或空段' ;; esac
if [ "$STOP_SHARED" = 1 ] || [ "$PURGE" = 1 ]; then
  [ "$STOP_SHARED" = 1 ] && [ "$SHARED_UNUSED" = 1 ] || fail '共享 MQ 操作须 --stop-shared-mq --confirm-shared-unused，先确认其他使用者'
fi
ROOT="$BASE/$SLUG"
# 不跟随 BASE 任一祖先或目标的符号链接；删除时也拒绝内部符号链接。
check="$ROOT"
while [ "$check" != / ]; do
  [ ! -L "$check" ] || fail "符号链接: $check"
  check="$(dirname "$check")"
done
if [ -e "$ROOT" ]; then
  [ -d "$ROOT" ] || fail '生成物目标不是目录'
  if [ "$DELETE_ARTIFACTS" = 1 ]; then
    links="$(find "$ROOT" -type l -print -quit)" || fail '无法检查生成物目录'
    [ -z "$links" ] || fail "生成物含符号链接: $links"
  fi
fi

stop_by_port() { # $1=端口 $2=命令行特征串（防误杀别的任务的进程）
  local port="$1" pat="$2" p cwd cmd
  for p in $(lsof -nP -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null); do
    # 启动器的后端用绝对 jar 路径，cwd 可能在 worktree 外：两种路径都核对。
    cwd="$(lsof -a -p "$p" -d cwd -Fn 2>/dev/null | grep '^n' | cut -c2-)"
    cmd="$(ps -p "$p" -o command= 2>/dev/null)"
    if { [[ "$cwd/" = *"/$SLUG/"* ]] || [[ "$cmd" = *"/$SLUG/"* ]]; } && printf '%s\n' "$cmd" | grep -Eq "$pat"; then
      kill "$p" && echo "stopped pid=$p (port $port)"
    else
      echo "skip pid=$p (port $port, 不匹配 '$pat')"
    fi
  done
}

echo "== 1. 停本需求进程 =="
stop_by_port 18080 'compass-backend-service\.jar'
stop_by_port 9967  'wl-local'
stop_by_port 8010  'assist-bot|main:app'

echo "== 2. 共享 MQ（默认不操作）=="
if [ "$STOP_SHARED" = 1 ]; then
  docker stop wl-rocketmq-broker wl-rocketmq-namesrv || fail 'MQ 停止失败'
fi
if [ "$PURGE" = 1 ]; then
  docker rm -v wl-rocketmq-broker wl-rocketmq-namesrv || fail 'MQ 容器删除失败'
  docker volume rm wl-rmq-conf || fail 'MQ volume 删除失败'
  echo "MQ 容器与 volume 已显式删除，证据不受此参数影响"
fi

echo "== 3. 生成物: $ROOT =="
if [ "$DELETE_ARTIFACTS" = 1 ] && [ -d "$ROOT" ]; then
  du -sh "$ROOT" 2>/dev/null
  rm -rf -- "$ROOT" || fail '生成物删除失败'
  echo "已按独立显式授权删除本 slug 生成物"
else
  echo "默认保留全部日志/产物；预览以上目录，删除另需 --delete-artifacts"
fi

echo "== 4. 残留检查 =="
ls "$BASE" 2>/dev/null
du -sh "$BASE" 2>/dev/null
echo "done."
