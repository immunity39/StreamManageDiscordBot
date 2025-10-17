import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

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

def list_my_broadcasts(youtube, max_results=10):
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

    items = resp.get("items", [])
    results = []
    for it in items:
        vid = it.get("id")
        title = it.get("snippet", {}).get("title")
        status_obj = it.get("status", {})
        lifecycle = status_obj.get("lifeCycleStatus")
        privacy = status_obj.get("privacyStatus")
        results.append({
            "id": vid,
            "title": title,
            "lifecycle": lifecycle,
            "privacy": privacy,
            "url": f"https://www.youtube.com/watch?v={vid}"
        })
    return results

def get_current_live_broadcasts(youtube):
    """
    取得した一覧から現在 'live' 状態のものだけを返す
    lifeCycleStatus == 'live' を判定基準にしています
    """
    all_bcs = list_my_broadcasts(youtube, max_results=50)
    live_ones = [b for b in all_bcs if b["lifecycle"] and b["lifecycle"].lower().startswith("live")]
    return live_ones

if __name__ == "__main__":
    print("🔐 YouTube OAuth 認証を行います...")
    yt = get_authenticated_service()
    print("✅ 認証完了。自分のブロードキャストを取得します...")
    bcs = list_my_broadcasts(yt)
    if not bcs:
        print("（※）ブロードキャストが存在しません。予約も含め無しです。")
    else:
        print("==== 自分のブロードキャスト一覧 ====")
        for b in bcs:
            print(f"- {b['title']}  | lifecycle={b['lifecycle']}  | privacy={b['privacy']}  | {b['url']}")
    # 現在ライブ中のものだけ取得する例
    live_now = get_current_live_broadcasts(yt)
    if live_now:
        print("\n🎥 現在ライブ中:")
        for b in live_now:
            print(f"  * {b['title']} ({b['privacy']}) -> {b['url']}")
    else:
        print("\n⚠️ 現在ライブ中の配信はありません。")
