import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL = "claude-opus-4-8"

# Slack
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_LOG_CHANNEL_ID = os.environ["SLACK_LOG_CHANNEL_ID"]       # 進捗を投稿するチャンネル
SLACK_REVIEW_CHANNEL_ID = os.environ["SLACK_REVIEW_CHANNEL_ID"] # レビューを投稿するチャンネル

# Notion
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_GOALS_PAGE_ID = os.environ["NOTION_GOALS_PAGE_ID"]           # 目標・チェックリストページ
NOTION_REVIEW_DATABASE_ID = os.environ["NOTION_REVIEW_DATABASE_ID"] # レビュー結果DB

# Timezone (JST)
TIMEZONE = "Asia/Tokyo"

# Review schedule: 何時に実行するか（GitHub Actions cron は UTC）
# 23:00 JST = 14:00 UTC
REVIEW_HOUR_UTC = 14
