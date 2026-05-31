#!/bin/bash
# cronジョブを登録するスクリプト
# 使い方: ./scripts/setup_cron.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
RUNNER="$SCRIPT_DIR/run_review.sh"
LOG_FILE="$PROJECT_DIR/logs/review.log"

mkdir -p "$PROJECT_DIR/logs"
chmod +x "$RUNNER"

# 毎日 23:00 JST に実行（TZ=Asia/Tokyo を cron に設定）
CRON_LINE="0 23 * * * TZ=Asia/Tokyo $RUNNER >> $LOG_FILE 2>&1"

# 既存のエントリを確認・重複登録を防ぐ
if crontab -l 2>/dev/null | grep -qF "$RUNNER"; then
  echo "すでにcronジョブが登録されています。"
  crontab -l | grep "$RUNNER"
else
  (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
  echo "cronジョブを登録しました:"
  echo "  $CRON_LINE"
fi
