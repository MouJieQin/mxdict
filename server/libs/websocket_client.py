import asyncio
import websockets
import typing
from websockets.exceptions import ConnectionClosed
from websockets.asyncio.client import ClientConnection


class WsClient:
    def __init__(self, uri: str, message_handler):
        self.uri = uri
        self.ws = None
        # self.loop = asyncio.get_event_loop()
        self.message_handler = message_handler

    async def connect(self):
        """自动重连的 WebSocket 客户端"""
        while True:
            try:
                async with websockets.connect(self.uri, ping_interval=30) as ws:
                    self.ws = ws
                    print(f"✅ 已连接 Electron WS服务器: {self.uri}")

                    # 监听消息
                    async for msg in ws:
                        print(f"\n📩 从 Electron 收到: {msg}")
                        # 在这里处理消息 → 可以调用你现有的函数
                        await self.message_handler(ws, str(msg))

            except ConnectionClosed:
                print("🔌 Electron 连接断开，5秒后重连...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ Electron WS 错误: {e}，5秒后重连")
                await asyncio.sleep(5)

    async def send(self, msg):
        """发送消息到 Electron"""
        if self.ws and not self.ws.closed:
            await self.ws.send(msg)
            print(f"✅ 发给Electron: {msg}")
        else:
            print("❌ 未连接 Electron")
