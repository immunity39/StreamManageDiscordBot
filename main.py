import asyncio, os, requests, time
from obswebsocket import obsws, requests as obsreq
from googleapiclient.discovery import build
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

load_dotenv()
OBS_HOST = os.getenv("OBS_HOST")
OBS_PORT = os.getenv("OBS_PORT")
OBS_PASSWORD = os.getenv("OBS_PASSWORD")
YT_API_KEY = os.getenv("YOUTUBE_API_KEY")
YT_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

# スコープ：読み取り専用でOK
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print("warning: token.json 読み込み失敗 -> 新規認証します:", e)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("既存トークンをリフレッシュしました。")
            except Exception as e:
                print("トークン刷新に失敗しました。再認証します:", e)
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"{CREDENTIALS_FILE} がありません。Google Cloud Console からダウンロードして配置してください。")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            # 保存
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
                print("token.json を保存しました。")

    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def list_my_broadcasts(youtube, max_results=5):
    """
    mine=True で呼び出す（broadcastStatus を同時に指定しないこと）
    返り値：broadcast のリスト（空なら []）
    """
    try:
        req = youtube.liveBroadcasts().list(
            part="id,snippet,contentDetails,status",
            mine=True,
            maxResults=max_results
        )
        resp = req.execute()
    except HttpError as e:
        # エラーハンドリング（400など）
        print("HttpError:", e)
        raise

    results = []
    for it in resp.get("items", []):
        vid = it.get("id")
        title = it.get("snippet", {}).get("title")
        status_obj = it.get("status", {})
        lifecycle = status_obj.get("lifeCycleStatus")
        privacy = status_obj.get("privacyStatus")
        results.append({
            "id": vid,
            "title": title,
            "lifecycle": lifecycle,
            "privacy": privacy
        })
    return results

def get_current_live_broadcast(youtube):
    """
    取得した一覧から現在 'live' 状態のものだけを返す
    lifeCycleStatus == 'live' を判定基準にしています
    """
    broadcasts = list_my_broadcasts(youtube, max_results=1)
    for b in broadcasts:
        if b["lifecycle"] == "live":
            return b
    return None

def on_stream_start():
    print("🔐 YouTube OAuth 認証を行います...")
    yt = get_authenticated_service()
    print("✅ 認証完了")


    # 配信開始のラグを考慮し、1分間の間10秒ごとに確認
    flag = False
    cnt = 0
    while not flag:
        # 現在ライブ中のものだけ取得
        live_now = get_current_live_broadcast(yt)
        if live_now:
            print("🎥 現在ライブ中:", live_now["title"])
            flag = True
            title = live_now["title"] if live_now else "不明なタイトル"
            url = f"https://www.youtube.com/watch?v={live_now['id']}" if live_now else "不明なURL"
            if url:
                data = {
                    "username": "YouTube通知Bot",
                    "content": f"🎥 **配信開始！**\n{title}\n{url}"
                }
                response = requests.post(DISCORD_WEBHOOK, json=data)
                if response.status_code == 204:
                    print("🎉 メッセージ送信成功！Discordに届きました。")
                else:
                    print(f"⚠️ メッセージ送信失敗（{response.status_code}）")
                    print(response.text)
            else:
                print("⚠️ 現在ライブ中の配信はありません。10秒後に再確認します。")
        else:
            print("⚠️ 現在ライブ中の配信はありません。")
            time.sleep(10)
            cnt += 1
            if cnt >= 6:
                break
    if not flag:
        print("ライブ配信が検出されません")

async def main():
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    ws.connect()
    print("OBS接続成功")

    def on_event(event):
        name = event.__dict__['name']
        data = event.__dict__['datain']
        if name == "StreamStateChanged":
            print("🚀 配信状態が変更されました")
            if data['outputActive'] == True:
                print("▶ 配信が開始されました")

                on_stream_start()
            else:
                print("⏸ 配信が停止されました")
    
    ws.register(on_event)
    await asyncio.Event().wait()

asyncio.run(main())