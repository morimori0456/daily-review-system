"""Claude API を使って1日の行動ログをレビューする"""
import json
import anthropic
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def run_daily_review(
    date_str: str,
    messages: list[dict],
    goals_text: str,
    past_reviews: list[dict],
) -> dict:
    """
    1日のレビューを実行して結果を返す。

    Returns:
        {
            "review_markdown": str,   # Notion/Slack向けの詳細レビュー
            "summary": str,           # 1〜2文の要約
            "score": int,             # 今日の総合スコア (1-10)
        }
    """
    activity_log = _format_activity_log(messages)
    past_context = _format_past_reviews(past_reviews)

    system_prompt = """あなたは生産性コーチです。ユーザーの1日の行動ログを分析し、
事前に設定された目標・ノウハウチェックリストと照合して、建設的で具体的なレビューを行います。
レビューは日本語で行い、以下のJSONフォーマットで返してください：

{
  "review_markdown": "# 日次レビュー\\n## 今日の成果\\n...",
  "summary": "1〜2文の要約",
  "score": 7
}

review_markdownのフォーマット：
# {date} 日次レビュー
## 今日の成果サマリー
（主な成果を箇条書き）
## 目標・チェックリスト達成度
（各目標/チェック項目に対してどう取り組んだか）
## 良かった点
（具体的な行動を褒める）
## 改善ポイント
（具体的な改善提案、批判ではなく建設的に）
## 明日へのアクションプラン
（明日最優先でやることを3つ）
## 成長トレンド分析
（過去のデータがある場合は時系列での変化を分析）"""

    user_message = f"""【対象日】{date_str}

【目標・ノウハウチェックリスト（Notionより）】
{goals_text}

【今日の行動ログ（30分おき報告）】
{activity_log}

【過去{len(past_reviews)}日間のレビュー履歴】
{past_context}

上記をもとに、今日のレビューをJSONで返してください。"""

    client = _get_client()
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    # JSONブロックを抽出
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    result = json.loads(raw)
    return {
        "review_markdown": result.get("review_markdown", ""),
        "summary": result.get("summary", ""),
        "score": int(result.get("score", 5)),
    }


def _format_activity_log(messages: list[dict]) -> str:
    if not messages:
        return "（本日のログなし）"
    return "\n".join(f"[{m['time']}] {m['text']}" for m in messages)


def _format_past_reviews(past_reviews: list[dict]) -> str:
    if not past_reviews:
        return "（過去のデータなし）"
    lines = []
    for r in past_reviews:
        score_str = f"スコア: {r['score']}/10" if r.get("score") is not None else ""
        lines.append(f"- {r['date']} {score_str}: {r.get('summary', '')}")
    return "\n".join(lines)
