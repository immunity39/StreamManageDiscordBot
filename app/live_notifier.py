import os
import asyncio
import discord
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# 通知済みライブIDの保存用
notified_live_ids = set()

async def check_live_status():
    """YouTubeチャンネルのライブ配信をチェック"""
    global notified_live_ids

    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        eventType="live",
        type="video",
        order="date",
        maxResults=1
    )
    response = request.execute()

    if response.get("items"):
        live_video = response["items"][0]
        live_id = live_video["id"]["videoId"]
        title = live_video["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={live_id}"

        if live_id not in notified_live_ids:
            notified_live_ids.add(live_id)
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            await channel.send(f"🎥 **ライブ配信が開始されました！**\n{title}\n{url}")

    else:
        print("No live streaming currently.")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    # 定期実行タスク
    while True:
        try:
            await check_live_status()
        except Exception as e:
            print("Error:", e)
        await asyncio.sleep(60 * 3)  # 3分ごとにチェック

client.run(DISCORD_TOKEN)
