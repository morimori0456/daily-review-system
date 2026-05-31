# Daily Review System

30分おきのSlack進捗投稿を1日の終わりにAIが自動レビューするシステム。

## フロー

```
[あなた] 30分おきにSlackへ進捗投稿
         ↓
[GitHub Actions] 毎日23:00 JSTに自動起動
         ↓
[Slack API] 当日のメッセージを取得
         ↓
[Notion API] 事前登録済みの目標・チェックリストを取得
         ↓
[Claude API] AIがレビューを生成（過去14日分も考慮した時系列分析付き）
         ↓
[Notion] レビューをデータベースに保存
[Slack]  レビュー結果を指定チャンネルに投稿
```

## セットアップ

### 1. Notion の準備

**目標・チェックリストページ**
- Notionに新しいページを作成し、目標やノウハウチェックリストを記載する
- ページIDをコピーしておく（URLの末尾32文字）

**レビュー結果データベース**
- 以下のプロパティを持つデータベースを作成：

| プロパティ名 | タイプ |
|---|---|
| Name | タイトル |
| Date | 日付 |
| Summary | テキスト |
| Score | 数値 |

### 2. Slack Bot の準備

1. [Slack API](https://api.slack.com/apps) でAppを作成
2. 以下の Bot Token Scopes を付与：
   - `channels:history` / `groups:history` — メッセージ取得
   - `chat:write` — 投稿
3. ワークスペースにインストールし Bot Token をコピー
4. 進捗投稿チャンネルと、レビュー受信チャンネルにBotを招待

### 3. GitHub Secrets の設定

リポジトリの `Settings > Secrets and variables > Actions` に以下を登録：

| Secret名 | 内容 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic APIキー |
| `SLACK_BOT_TOKEN` | `xoxb-...` で始まるBot Token |
| `SLACK_LOG_CHANNEL_ID` | 進捗を投稿するチャンネルのID |
| `SLACK_REVIEW_CHANNEL_ID` | レビュー結果を投稿するチャンネルのID |
| `NOTION_API_KEY` | Notion Integration Token |
| `NOTION_GOALS_PAGE_ID` | 目標・チェックリストページのID |
| `NOTION_REVIEW_DATABASE_ID` | レビュー結果データベースのID |

### 4. 手動実行（テスト）

GitHub Actions の `workflow_dispatch` で任意の日付を指定して手動実行できます。

```bash
# ローカルでテスト実行する場合
cp .env.example .env  # 環境変数を設定
python src/main.py 2026-05-31
```

## 使い方

1. 毎日、作業中に30分ごとにSlackの進捗チャンネルへ投稿：
   ```
   プレゼン資料のスライド3〜5を完成。競合分析のデータを追加できた。
   想定より時間がかかっているが品質は上がっている。
   ```

2. 毎日23時にAIが自動でレビューし、Slackに結果が届く

3. Notionのレビューデータベースで過去の推移を確認できる
