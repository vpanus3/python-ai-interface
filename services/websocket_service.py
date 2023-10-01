import asyncio
import websockets

class WebSocketService:

    def __init__(self):
        self.websocket = None
        self.loop = asyncio.get_event_loop()

    async def handler(self, websocket, path):
        self.websocket = websocket
        try:
            async for message in websocket:
                print(f"Received message from client: {message}")
        except websockets.ConnectionClosed:
            print("Connection closed.")

    async def start(self):
        self.server = websockets.serve(self.handler, 'localhost', 8080)
        await self.loop.run_until_complete(self.server)
        await self.loop.run_forever()

    def stop(self):
        self.server.ws_server.close()
        self.loop.stop()
        print("WebSocket server stopped.")

    async def send_message(self, message):
        if self.websocket:
            await self.websocket.send(message)
            print(f"Sent: {message}")