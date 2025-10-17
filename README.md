# 🎥 YouTube Live Notifier for Discord

> OBS 配信開始 または 定期監視をトリガーに  
> YouTube のライブ配信 URL を自動で Discord に通知する Python ツール

---

## 📘 概要

このリポジトリでは、YouTube チャンネルの**配信開始を自動検知**し、  
指定した**Discord チャンネルへ通知を送る**システムを提供します。

**OBS 配信開始をトリガーに通知**（リアルタイム・推奨）

**限定配信を含む YouTube Live**を検知できます。  
複数人で共有する場合も、`.env` ファイルを個別に設定することで同様に利用可能です。

---

## 💻 対応環境

| 項目       | 内容                                          |
| ---------- | --------------------------------------------- |
| OS         | Windows 11（推奨）                            |
| Python     | 3.10 以上                                     |
| OBS Studio | v29 以降（WebSocket 対応）                    |
| YouTube    | 限定・公開どちらも対応（自分の API キー使用） |
| Discord    | 任意のチャンネルに Webhook 投稿可             |

---

## 🚀 セットアップ手順（初回のみ）

### 1️⃣ Python の導入

1. [Python 公式サイト](https://www.python.org/downloads/windows/) にアクセス
2. 「**Add Python to PATH**」にチェックを入れてインストール
3. コマンドプロンプトで以下を実行し、バージョンを確認します。

```bash
python --version
```

例: `Python 3.12.3` が表示されれば OK です。

---

### 2️⃣ 必要パッケージのインストール

以下のコマンドを実行して、必要な Python ライブラリをインストールします。

```bash
pip install google-api-python-client obs-websocket-py requests python-dotenv
```

または、リポジトリの `requirements.txt` を利用する場合は：

```bash
pip install -r requirements.txt
```

---

### 3️⃣ `.env` ファイルの作成

このリポジトリのルートディレクトリに `.env` ファイルを作成し、以下のように記述してください。

```env
# YouTube API設定
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
YOUTUBE_CHANNEL_ID=YOUR_CHANNEL_ID

# Discord設定
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXXXXXXXXXXXX

# OBS設定（リアルタイム監視モード使用時のみ）
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=YOUR_OBS_PASSWORD
```

> 🔸 `.env` は各自の環境に合わせて個別に作成してください（Git には含めません）。  
> 🔸 `YOUR_YOUTUBE_API_KEY` は後述の手順で取得します。

---

### 4️⃣ YouTube API キーの取得方法

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（例：「YouTubeNotifier」）
3. 左メニュー → 「API とサービス」 → 「ライブラリ」
4. 「YouTube Data API v3」を検索して有効化
5. 「認証情報」 → 「API キーを作成」
6. 取得した API キーを `.env` の `YOUTUBE_API_KEY` に設定

---

### 5️⃣ Discord Webhook の作成方法

1. Discord で通知を送りたいチャンネルを右クリック
2. 「チャンネルを編集」 → 「連携サービス」 → 「Webhook を作成」
3. Webhook 名を設定し、「Webhook URL をコピー」
4. `.env` の `DISCORD_WEBHOOK_URL` に貼り付け

---

### 6️⃣ OBS 設定（リアルタイム通知モードのみ）

1. OBS を起動
2. メニュー → 「ツール」 → 「WebSocket サーバー設定」
3. 「サーバーを有効化」にチェック
4. ポート番号を `4455`（デフォルト）に設定
5. パスワードを設定し、`.env` の `OBS_PASSWORD` に一致させる

---

## ⚙️ 実行方法

```bash
python main.py
```

---

## 🕓 自動起動設定（Windows 用）


---

## 🧪 動作確認手順

### ✅ YouTube 側

限定公開または公開で配信を開始し、`.env` のチャンネル ID が正しいか確認。

### ✅ Discord 側

Webhook を設定したチャンネルに通知が届けば成功。

---

## 🧱 ディレクトリ構成例

```
youtube-live-notifier/
├── notify_on_obs_start.py
├── poll_youtube_live.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🧰 requirements.txt

```txt
google-api-python-client
obs-websocket-py
requests
python-dotenv
```

---

## 🧠 複数人での利用について

`.env` は個人ごとに作成し、Git 管理対象外にします。

---

## ⚠️ 注意事項

-   YouTube API の無料枠は **10,000 クォータ単位／日**
-   `search.list` 1 回あたり 100 単位消費
-   15 分間隔で運用すれば無料枠内

---

## 各種動作テスト

OBS, Youtube, Discord に対してプログラムが正常に動作しているかを確認するためのテストコード

### OBS 起動確認

OBS の起動を検知できているか **obs.py**

```bash
python obs.py
```

### Youtube API 動作確認

Youtube API を正常に実行でき、配信を取得できているか **youtube.py**

```bash
python obs.py
```

### Discord メッセージ確認

Discord にメッセージを投稿できるか **discord.py**

```bash
python discord.py
```

---

## 🧩 拡張予定

-   Discord Embed 対応
-   OBS ホットキー通知
-   Push 通知（PubSubHubbub）
-   GUI 化

---

## 🪪 ライセンス

MIT License © 2025

---

## 💬 開発背景

Carl-bot は限定配信を検知できないため、  
OBS 操作をトリガーにローカル完結の通知を実現。
