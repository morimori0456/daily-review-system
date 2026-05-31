"""Slack からメッセージを読み取り、レビュー結果を投稿する"""
from datetime import datetime, timedelta
import pytz
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def _get_client() -> WebClient:
    return WebClient(token=config.SLACK_BOT_TOKEN)


def fetch_today_messages(date: datetime | None = None) -> list[dict]:
    """指定日（デフォルト: 今日）のログチャンネルメッセージを取得する"""
    tz = pytz.timezone(config.TIMEZONE)
    if date is None:
        date = datetime.now(tz)

    day_start = tz.localize(datetime(date.year, date.month, date.day, 0, 0, 0))
    day_end = day_start + timedelta(days=1)

    oldest = str(day_start.timestamp())
    latest = str(day_end.timestamp())

    client = _get_client()
    messages = []
    cursor = None

    while True:
        try:
            resp = client.conversations_history(
                channel=config.SLACK_LOG_CHANNEL_ID,
                oldest=oldest,
                latest=latest,
                limit=200,
                cursor=cursor,
            )
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response['error']}") from e

        for msg in resp["messages"]:
            if msg.get("type") == "message" and not msg.get("bot_id"):
                ts = float(msg["ts"])
                local_dt = datetime.fromtimestamp(ts, tz=tz)
                messages.append({
                    "time": local_dt.strftime("%H:%M"),
                    "text": msg.get("text", ""),
                })

        if not resp.get("has_more"):
            break
        cursor = resp["response_metadata"]["next_cursor"]

    # 時刻順に並べ替え
    messages.sort(key=lambda m: m["time"])
    return messages


def post_review(review_text: str, date_str: str) -> str:
    """レビュー結果をSlackに投稿してメッセージTSを返す"""
    client = _get_client()
    header = f":bar_chart: *{date_str} 日次レビュー*\n\n"
    try:
        resp = client.chat_postMessage(
            channel=config.SLACK_REVIEW_CHANNEL_ID,
            text=header + review_text,
            mrkdwn=True,
        )
        return resp["ts"]
    except SlackApiError as e:
        raise RuntimeError(f"Slack post error: {e.response['error']}") from e
