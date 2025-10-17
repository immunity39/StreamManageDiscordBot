import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_test_message():
    """Discord Webhookにメッセージ送信"""
    if not WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL が設定されていません。")
        return

    data = {
        "username": "YouTube通知テストBot",
        "content": "✅ Discord Webhookテスト成功！\nこのメッセージが届いていれば設定OKです。"
    }

    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("🎉 メッセージ送信成功！Discordに届きました。")
    else:
        print(f"⚠️ メッセージ送信失敗（{response.status_code}）")
        print(response.text)

if __name__ == "__main__":
    print("🔍 Discord通知テストを開始します。")
    send_test_message()
