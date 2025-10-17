import os, asyncio, requests
from obswebsocket import obsws, requests as obsreq, events
from dotenv import load_dotenv

load_dotenv()

OBS_HOST = os.getenv("OBS_HOST")
OBS_PORT = int(os.getenv("OBS_PORT"))
OBS_PASSWORD = os.getenv("OBS_PASSWORD")

def on_stream_started(event):
    print("🚀 配信が開始されました！")

def on_stream_stopped(event):
    print("🛑 配信が終了しました！")

async def main():
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    ws.connect()
    print("✅ OBS WebSocket に接続しました")

    # イベント購読
    #ws.register(on_stream_started, events.StreamStarted)
    #ws.register(on_stream_stopped, events.StreamStopped)

    print("🎧 配信イベントの監視を開始します...")
    def on_event(event):
        print(type(event))
        print(event)
        print(list(event.__dict__.items()))

        name = event.__dict__['name']
        data = event.__dict__['datain']
        print("イベント名:", name)
        if name == "RecordStateChanged":
            print("📼 録画状態が変更されました")
            if data['outputActive'] == True:
                print("▶ 録画が開始されました")
            else:
                print("⏸ 録画が停止されました")
        elif name == "StreamStateChanged":
            print("🚀 配信状態が変更されました")
            if data['outputActive'] == True:
                print("▶ 配信が開始されました")
            else:
                print("⏸ 配信が停止されました")
    
    ws.register(on_event)
    await asyncio.Event().wait()

asyncio.run(main())