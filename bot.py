import asyncio, os, requests
from obswebsocket import obsws, requests as obsreq
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = os.getenv("OBS_PASSWORD")
YT_API_KEY = os.getenv("YOUTUBE_API_KEY")
YT_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

youtube = build("youtube", "v3", developerKey=YT_API_KEY)

def get_live_video():
    req = youtube.search().list(
        part="snippet",
        channelId=YT_CHANNEL_ID,
        eventType="live",
        type="video"
    )
    res = req.execute()
    if res["items"]:
        video = res["items"][0]
        title = video["snippet"]["title"]
        vid = video["id"]["videoId"]
        return title, f"https://www.youtube.com/watch?v={vid}"
    return None, None

async def on_stream_start():
    title, url = get_live_video()
    if url:
        requests.post(DISCORD_WEBHOOK, json={
            "content": f"🎥 **配信開始！**\n{title}\n{url}"
        })
        print("通知送信:", title)
    else:
        print("ライブ配信が検出されません")

async def main():
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    ws.connect()
    print("OBS接続成功")

    def on_event(event):
        if event.getUpdateType() == "StreamStarted":
            asyncio.create_task(on_stream_start())

    ws.register(on_event)
    await asyncio.Event().wait()

asyncio.run(main())
