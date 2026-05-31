"""Notion から目標・チェックリストを取得し、レビュー結果を書き込む"""
from datetime import datetime
import sys
import os

from notion_client import Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def _get_client() -> Client:
    return Client(auth=config.NOTION_API_KEY)


def fetch_goals_and_checklist() -> str:
    """目標・チェックリストページのテキスト内容を取得する"""
    client = _get_client()
    blocks = []
    cursor = None

    while True:
        resp = client.blocks.children.list(
            block_id=config.NOTION_GOALS_PAGE_ID,
            start_cursor=cursor,
            page_size=100,
        )
        blocks.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]

    lines = []
    for block in blocks:
        btype = block["type"]
        rich_texts = block.get(btype, {}).get("rich_text", [])
        text = "".join(rt.get("plain_text", "") for rt in rich_texts)
        if text:
            prefix = {
                "heading_1": "# ",
                "heading_2": "## ",
                "heading_3": "### ",
                "bulleted_list_item": "- ",
                "numbered_list_item": "1. ",
                "to_do": "[ ] " if not block.get(btype, {}).get("checked") else "[x] ",
            }.get(btype, "")
            lines.append(prefix + text)

    return "\n".join(lines)


def fetch_past_reviews(limit: int = 14) -> list[dict]:
    """過去のレビュー記録をNotionDBから取得する（直近N日分）"""
    client = _get_client()
    resp = client.databases.query(
        database_id=config.NOTION_REVIEW_DATABASE_ID,
        sorts=[{"property": "Date", "direction": "descending"}],
        page_size=limit,
    )

    reviews = []
    for page in resp["results"]:
        props = page["properties"]
        date_val = props.get("Date", {}).get("date", {})
        date_str = date_val.get("start", "") if date_val else ""

        # Summaryプロパティを取得
        summary_rt = props.get("Summary", {}).get("rich_text", [])
        summary = "".join(rt.get("plain_text", "") for rt in summary_rt)

        # Scoreプロパティを取得
        score = props.get("Score", {}).get("number")

        reviews.append({"date": date_str, "summary": summary, "score": score})

    reviews.reverse()  # 古い順に
    return reviews


def save_review(date_str: str, review_text: str, summary: str, score: int) -> str:
    """レビュー結果をNotionデータベースに保存してページIDを返す"""
    client = _get_client()

    resp = client.pages.create(
        parent={"database_id": config.NOTION_REVIEW_DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": f"{date_str} 日次レビュー"}}]},
            "Date": {"date": {"start": date_str}},
            "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
            "Score": {"number": score},
        },
        children=_markdown_to_notion_blocks(review_text),
    )
    return resp["id"]


def _markdown_to_notion_blocks(text: str) -> list[dict]:
    """マークダウンテキストをNotionブロックリストに変換する"""
    blocks = []
    for line in text.split("\n"):
        if line.startswith("# "):
            blocks.append(_heading(1, line[2:]))
        elif line.startswith("## "):
            blocks.append(_heading(2, line[3:]))
        elif line.startswith("### "):
            blocks.append(_heading(3, line[4:]))
        elif line.startswith("- "):
            blocks.append(_bullet(line[2:]))
        elif line.strip():
            blocks.append(_paragraph(line))
        # 空行はスキップ（Notionは段落間に自動スペース）

    # Notion は1リクエストで100ブロックまで
    return blocks[:100]


def _heading(level: int, text: str) -> dict:
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _bullet(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _paragraph(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }
