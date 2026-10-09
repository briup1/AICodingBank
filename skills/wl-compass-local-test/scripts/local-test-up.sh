#!/usr/bin/env bash
# compass 本地自测 · 一键启动（wl-compass-local-test）
# 用法: local-test-up.sh [worktree目录] [--no-build]
# 默认构建后端 jar（约40s）；改了代码必跑，没改可 --no-build 复用旧 jar
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$PWD"; BUILD=1
for a in "$@"; do
  case "$a" in
    --no-build) BUILD=0 ;;
    *) [ -d "$a" ] && WT="$(cd "$a" && pwd)" ;;
  esac
done
[ -f "$WT/backend-service/pom.xml" ] || { echo "❌ $WT 不是 compass-platform worktree（缺 backend-service/pom.xml）"; exit 1; }
SLUG="$(basename "$WT")"
LT="${COMPASS_LOCAL_TEST_HOME:-$HOME/.local/state/compass-local-test}/$SLUG"
mkdir -p "$LT/logs" "$LT/artifacts"

echo "== 0. dev 网络检查（FAIL 项会导致起不来或查询无数据）=="
for t in "dev-mysql8.hgj.net 3306" "dev-middle.hgj.net 6379" "10.10.10.145 27017" "iter-apisix.hgj.com 443"; do
  nc -z -w 2 $t >/dev/null 2>&1 && echo "  OK   $t" || echo "  FAIL $t"
done

echo "== 1. 端口检查 =="
for port in 18080 9967; do
  p=$(lsof -nP -tiTCP:$port -sTCP:LISTEN 2>/dev/null || true)
  if [ -n "$p" ]; then
    echo "❌ 端口 $port 被 pid=$p 占用：$(ps -p "$p" -o command= | cut -c1-80)"
    echo "   如是残留请先跑 local-test-down.sh $SLUG"; exit 1
  fi
done
echo "  18080/9967 空闲"

echo "== 2. RocketMQ（共享件，已有则复用）=="
if docker ps --format '{{.Names}}' | grep -q '^wl-rocketmq-broker$'; then
  echo "  已在运行"
elif docker ps -a --format '{{.Names}}' | grep -q '^wl-rocketmq-broker$'; then
  docker start wl-rocketmq-namesrv wl-rocketmq-broker >/dev/null && echo "  已启动（复用）"
else
  docker compose -f "$SCRIPT_DIR/docker-compose.mq.yml" --profile init run --rm conf-init >/dev/null \
    && docker compose -f "$SCRIPT_DIR/docker-compose.mq.yml" up -d >/dev/null && echo "  已创建（首次）"
fi

echo "== 3. 构建后端 jar =="
if [ "$BUILD" = 1 ]; then
  (cd "$WT/backend-service" && mvn package -Pdev -Dmaven.test.skip=true -q) || { echo "❌ 构建失败"; exit 1; }
  echo "  构建完成"
else
  [ -f "$WT/backend-service/target/compass-backend-service.jar" ] || { echo "❌ 无 jar 且 --no-build"; exit 1; }
  echo "  复用现有 jar"
fi

echo "== 4. 启动后端 :18080 =="
nohup java -jar "$WT/backend-service/target/compass-backend-service.jar" \
  --spring.profiles.active=local \
  --spring.cloud.nacos.config.enabled=false \
  --spring.cloud.nacos.discovery.enabled=false \
  --server.port=18080 \
  --rocketmq.name-server=127.0.0.1:19876 \
  --spring.data.redis.database=3 \
  > "$LT/logs/backend.log" 2>&1 &
echo "  pid=$! 日志: $LT/logs/backend.log"
for i in $(seq 1 30); do
  sleep 2
  curl -sf -m 2 localhost:18080/actuator/health 2>/dev/null | grep -q '"UP"' && { echo "  健康检查通过 (${i}x2s)"; break; }
  [ "$i" = 30 ] && { echo "❌ 后端 60s 未就绪，看日志"; exit 1; }
done

echo "== 5. 启动前端 :9967 =="
[ -d "$WT/agents-web/node_modules" ] || (cd "$WT/agents-web" && pnpm install --prefer-offline >/dev/null 2>&1)
cp -n "$SCRIPT_DIR/../assets/env.wl-local" "$WT/agents-web/.env.wl-local" 2>/dev/null || true
(cd "$WT/agents-web" && nohup pnpm dev -- --mode wl-local --port 9967 --no-open > "$LT/logs/frontend.log" 2>&1 &)
for i in $(seq 1 30); do
  sleep 2
  curl -sf -o /dev/null -m 2 localhost:9967/ && { echo "  前端就绪 (${i}x2s)"; break; }
  [ "$i" = 30 ] && { echo "❌ 前端 60s 未就绪，看日志"; exit 1; }
done

cat <<SUMMARY

✅ 本地自测环境就绪（需求: $SLUG）
  后端      http://127.0.0.1:18080   (日志 $LT/logs/backend.log)
  前端      http://localhost:9967
  产物目录  $LT/artifacts/
  登录态    浏览器打开 http://localhost:9967 → 跳 dev-login 登录一次（14天有效）
  API smoke 按 SKILL.md「验证链路」执行
  清理      local-test-down.sh $SLUG
SUMMARY
