# Daily Review System

30分おきのSlack進捗投稿を、Claude Code CLIが毎晩自動でレビューするシステム。
**Anthropic APIキー不要** — Claude Codeの既存サブスクリプションで動作します。

## フロー

```
[あなた] 30分おきにSlackへ進捗を投稿
         ↓
[cron] 毎日 23:00 JST に run_review.sh を起動
         ↓
[claude -p] Slackから当日メッセージを取得（Slack MCP）
         ↓
[claude -p] Notionから目標・チェックリストを取得（Notion MCP）
         ↓
[claude -p] 過去14日分のレビュー履歴を参照して分析
         ↓
[claude -p] NotionにレビューDB保存 ＋ Slackに投稿
```

## セットアップ

### 1. 環境変数を設定

```bash
cp .env.example .env
# .env を編集して各IDを入力
```

### 2. MCPサーバーの依存をインストール

```bash
npm install -g @modelcontextprotocol/server-slack @notionhq/notion-mcp-server
```

### 3. cronを登録（毎日23:00 JSTに自動実行）

```bash
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh
```

### 4. 動作確認（手動テスト）

```bash
chmod +x scripts/run_review.sh
./scripts/run_review.sh           # 今日のレビュー
./scripts/run_review.sh 2026-05-30  # 特定日を指定
```

## ファイル構成

```
daily-review-system/
├── .claude/
│   └── settings.json          # MCP（Slack・Notion）設定
├── prompts/
│   └── daily_review.md        # Claudeへの指示プロンプト
├── scripts/
│   ├── run_review.sh          # レビュー実行スクリプト
│   └── setup_cron.sh          # cronジョブ登録ヘルパー
├── logs/                      # 実行ログ（自動生成）
└── .env                       # 環境変数（gitignore済み）
```

## Notionデータベースのプロパティ

レビュー保存用DBに以下のプロパティを作成してください：

| プロパティ名 | タイプ |
|---|---|
| Name | タイトル |
| Date | 日付 |
| Summary | テキスト |
| Score | 数値 |
