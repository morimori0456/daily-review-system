#!/bin/bash
# 日次レビューを実行するスクリプト
# 使い方: ./scripts/run_review.sh [YYYY-MM-DD]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 環境変数を読み込む（.envファイルがあれば）
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  source "$PROJECT_DIR/.env"
  set +a
fi

# 必須環境変数チェック
: "${SLACK_LOG_CHANNEL_ID:?SLACK_LOG_CHANNEL_ID が未設定です}"
: "${SLACK_REVIEW_CHANNEL_ID:?SLACK_REVIEW_CHANNEL_ID が未設定です}"
: "${NOTION_GOALS_PAGE_ID:?NOTION_GOALS_PAGE_ID が未設定です}"
: "${NOTION_REVIEW_DATABASE_ID:?NOTION_REVIEW_DATABASE_ID が未設定です}"

# 対象日（引数で指定、なければ今日のJST日付）
DATE="${1:-$(TZ='Asia/Tokyo' date +%Y-%m-%d)}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日次レビュー開始: $DATE"

# プロンプトテンプレートを読み込んで変数を置換
PROMPT=$(sed \
  -e "s/{{DATE}}/$DATE/g" \
  -e "s/{{SLACK_LOG_CHANNEL_ID}}/$SLACK_LOG_CHANNEL_ID/g" \
  -e "s/{{SLACK_REVIEW_CHANNEL_ID}}/$SLACK_REVIEW_CHANNEL_ID/g" \
  -e "s/{{NOTION_GOALS_PAGE_ID}}/$NOTION_GOALS_PAGE_ID/g" \
  -e "s/{{NOTION_REVIEW_DATABASE_ID}}/$NOTION_REVIEW_DATABASE_ID/g" \
  "$PROJECT_DIR/prompts/daily_review.md"
)

# Claude Code CLI で実行（MCPツールを使用）
cd "$PROJECT_DIR"
claude -p "$PROMPT"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完了"
