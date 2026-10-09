#!/usr/bin/env bash
# compass 本地自测 · 定点清理（wl-compass-local-test）
#
# 生成物位置约定（可控制）：
#   根目录 = ${COMPASS_LOCAL_TEST_HOME:-~/.local/state/compass-local-test}/<worktree-slug>
#   每次测试的所有产出只落在这个根下：logs/ artifacts/ mq/
#
# 用法：
#   local-test-down.sh [slug]      停本需求进程 + 删本需求生成物根目录（默认留最新一份日志）
#   local-test-down.sh --purge     额外删除共享 MQ 容器与 volume（下次起环境需重建 broker.conf）
#   slug 缺省时取当前目录名
set -uo pipefail
BASE="${COMPASS_LOCAL_TEST_HOME:-$HOME/.local/state/compass-local-test}"
PURGE=0
for a in "$@"; do [ "$a" = "--purge" ] && PURGE=1; done
SLUG="$(pwd | xargs basename)"
[ $# -ge 1 ] && [ "$1" != "--purge" ] && SLUG="$1"
ROOT="$BASE/$SLUG"

stop_by_port() { # $1=端口 $2=命令行特征串（防误杀别的任务的进程）
  local port="$1" pat="$2" p
  for p in $(lsof -nP -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null); do
    if ps -p "$p" -o command= 2>/dev/null | grep -q "$pat"; then
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

echo "== 2. 停共享 MQ 容器（volume 保留，docker start 可复用）=="
docker stop wl-rocketmq-broker wl-rocketmq-namesrv 2>/dev/null || true
if [ "$PURGE" = 1 ]; then
  docker rm -v wl-rocketmq-broker wl-rocketmq-namesrv 2>/dev/null || true
  docker volume rm wl-rmq-conf 2>/dev/null || true
  echo "MQ 容器与 volume 已删除"
fi

echo "== 3. 定点清理生成物: $ROOT =="
if [ -d "$ROOT" ]; then
  # 默认保留最新一份 backend.log 便于复盘（--purge 不保留）
  if [ "$PURGE" = 0 ]; then
    mkdir -p "$BASE/_last_logs/$SLUG"
    newest=$(ls -t "$ROOT"/logs/*.log 2>/dev/null | head -1)
    [ -n "$newest" ] && cp "$newest" "$BASE/_last_logs/$SLUG/"
  fi
  du -sh "$ROOT" 2>/dev/null
  rm -rf "$ROOT"
  echo "已删除"
else
  echo "目录不存在，无需清理"
fi

echo "== 4. 残留检查 =="
ls "$BASE" 2>/dev/null
du -sh "$BASE" 2>/dev/null
echo "done."
