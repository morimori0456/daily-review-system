"""日次レビューシステム エントリーポイント"""
import sys
import os
from datetime import datetime
import pytz

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src import slack_client, notion_client as nc, reviewer


def run(target_date: datetime | None = None) -> None:
    tz = pytz.timezone(config.TIMEZONE)
    if target_date is None:
        target_date = datetime.now(tz)

    date_str = target_date.strftime("%Y-%m-%d")
    print(f"[{date_str}] 日次レビュー開始")

    # 1. 今日のSlackログを取得
    print("  Slackメッセージを取得中...")
    messages = slack_client.fetch_today_messages(target_date)
    print(f"  {len(messages)}件のメッセージを取得")

    # 2. Notionから目標・チェックリストを取得
    print("  Notionから目標を取得中...")
    goals_text = nc.fetch_goals_and_checklist()
    print(f"  目標テキスト取得完了 ({len(goals_text)}文字)")

    # 3. 過去のレビュー履歴を取得（直近14日）
    print("  過去のレビュー履歴を取得中...")
    past_reviews = nc.fetch_past_reviews(limit=14)
    print(f"  {len(past_reviews)}件の過去レビューを取得")

    # 4. Claude APIでレビュー実行
    print("  AIレビューを実行中...")
    result = reviewer.run_daily_review(
        date_str=date_str,
        messages=messages,
        goals_text=goals_text,
        past_reviews=past_reviews,
    )
    print(f"  レビュー完了 (スコア: {result['score']}/10)")

    # 5. Notionにレビューを保存
    print("  Notionにレビューを保存中...")
    notion_page_id = nc.save_review(
        date_str=date_str,
        review_text=result["review_markdown"],
        summary=result["summary"],
        score=result["score"],
    )
    print(f"  Notionページ作成: {notion_page_id}")

    # 6. Slackにレビューを投稿
    print("  Slackにレビューを投稿中...")
    slack_ts = slack_client.post_review(
        review_text=result["review_markdown"],
        date_str=date_str,
    )
    print(f"  Slack投稿完了: ts={slack_ts}")

    print(f"[{date_str}] 日次レビュー完了")


if __name__ == "__main__":
    # コマンドライン引数で日付を指定可能: python src/main.py 2026-05-30
    tz = pytz.timezone(config.TIMEZONE)
    if len(sys.argv) > 1:
        date = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=tz)
    else:
        date = None
    run(date)
