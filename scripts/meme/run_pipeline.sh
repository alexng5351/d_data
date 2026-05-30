#!/usr/bin/env bash
set -euo pipefail

log() {
  printf "[%s] %s\n" "$(date "+%Y-%m-%d %H:%M:%S")" "$1"
}

run_step() {
  local description="$1"
  shift
  log "▶️  ${description}"
  if ! "$@"; then
    log "❌ 步骤失败：${description}"
    exit 1
  fi
  log "✅ 完成：${description}"
}

run_scrape_and_enrich() {
  run_step "抓取热梗 meme 数据" python3 scripts/meme/scrape_memes.py --env "$ENVIRONMENT"
  log "▶️  AI 筛选并评分 meme 候选"
  set +e
  python3 scripts/meme/enrich_memes.py --env "$ENVIRONMENT"
  local enrich_exit_code=$?
  set -e
  if [ "$enrich_exit_code" -ne 0 ]; then
    log "❌ 步骤失败：AI 筛选并评分 meme 候选（exit ${enrich_exit_code}）"
    exit "$enrich_exit_code"
  fi
  log "✅ 完成：AI 筛选并评分 meme 候选"
}

run_generate() {
  # 检查候选池 pending 数量
  CANDIDATES_JSON="public/data/meme/meme_candidates${ENV_SUFFIX}.json"
  PENDING_COUNT=$(python3 -c "
import json, sys
try:
    data = json.load(open('$CANDIDATES_JSON'))
    candidates = data.get('candidates') or data.get('items', [])
    print(len([x for x in candidates if x.get('status') == 'pending']))
except Exception as e:
    print(0)
" 2>/dev/null)

  log "📊 当前候选池 pending 数量：$PENDING_COUNT"

  if [ "${PENDING_COUNT:-0}" -lt 3 ]; then
    log "⚠️ 候选池不足 3 条（当前 $PENDING_COUNT 条），自动触发 enrich 补充候选池..."
    # 先跑 enrich 模式补充
    bash "$0" --env "$ENVIRONMENT" --mode enrich
  fi

  log "▶️  生成 meme sticker 图片"
  set +e
  python3 scripts/meme/generate_stickers.py --env "$ENVIRONMENT" --limit 5
  local generate_exit_code=$?
  set -e
  if [ "$generate_exit_code" -ne 0 ]; then
    log "❌ 步骤失败：生成 meme sticker 图片（exit ${generate_exit_code}）"
    exit "$generate_exit_code"
  fi
  log "✅ 完成：生成 meme sticker 图片"
}

git_push_updates() {
  log "▶️  提交并推送 meme 数据更新"
  if [ "$ENVIRONMENT" != "prod" ]; then
    log "ℹ️  dev 环境不提交不推送，避免测试数据污染正式数据"
    return 0
  fi

  git add public/data/meme/meme_candidates.json public/images/meme
  if git diff --cached --quiet; then
    log "ℹ️  meme 数据没有变更，跳过 commit 和 push"
  else
    current_branch="$(git branch --show-current)"
    git commit -m "chore: auto update meme stickers $(date +%Y-%m-%d)"
    git pull --rebase origin "$current_branch" || true
    if git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
      git push || echo "WARNING: git push failed, continuing..."
    else
      git push --set-upstream origin "$current_branch" || echo "WARNING: git push failed, continuing..."
    fi
    log "✅ 完成：提交并推送 meme 数据更新"
  fi
}


archive_candidates() {
  if [ "$ENVIRONMENT" != "prod" ]; then
    return 0
  fi

  local ARCHIVE_DIR="public/data/meme/archives"
  mkdir -p "$ARCHIVE_DIR"

  local TIMESTAMP=$(date +%Y%m%d_%H%M)
  local SOURCE_FILE="public/data/meme/meme_candidates.json"
  local TARGET_FILE="$ARCHIVE_DIR/meme_candidates_$TIMESTAMP.json"

  if [ -f "$SOURCE_FILE" ]; then
    cp "$SOURCE_FILE" "$TARGET_FILE"
    log "[archive] 已归档到 archives/meme_candidates_$TIMESTAMP.json"
  fi
}

ENVIRONMENT="prod"
MODE="full"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --env)
      ENVIRONMENT="${2:-}"
      shift 2
      ;;
    --env=*)
      ENVIRONMENT="${1#*=}"
      shift
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    *)
      log "❌ 未知参数：$1"
      exit 1
      ;;
  esac
done

if [ "$ENVIRONMENT" != "prod" ] && [ "$ENVIRONMENT" != "dev" ]; then
  log "❌ --env 只能是 prod 或 dev"
  exit 1
fi

if [ "$ENVIRONMENT" = "dev" ]; then
  ENV_SUFFIX="_dev"
else
  ENV_SUFFIX=""
fi

if [ "$MODE" != "enrich" ] && [ "$MODE" != "generate" ] && [ "$MODE" != "full" ]; then
  log "❌ --mode 只能是 enrich、generate 或 full"
  exit 1
fi

if [ ! -d "scripts" ] || [ ! -d "public/data/meme" ]; then
  log "❌ 请在项目根目录执行 scripts/meme/run_pipeline.sh"
  exit 1
fi

log "当前数据环境：${ENVIRONMENT}"
log "当前运行模式：${MODE}"

case "$MODE" in
  enrich)
    run_scrape_and_enrich
    ;;
  generate)
    run_generate
    archive_candidates
    git_push_updates
    ;;
  full)
    run_scrape_and_enrich
    run_generate
    archive_candidates
    git_push_updates
    ;;
esac

log "🏁 热梗 meme 自动化流程运行完成"
