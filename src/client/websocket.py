import asyncio
from websockets.asyncio.server import serve

queue = asyncio.Queue()

async def producer():
    await asyncio.sleep(3)
    return "Hello !"

async def consumer(message):
    print(f'Hello {message}')
    await queue.put(message)

class WebSocket:
    def __init__(self, port=5001):
        global queue
        self.host="localhost"
        self.port = port
        self.message = ""
        self.queue = queue
    
    def run(self):
        asyncio.run(main())

async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)

async def producer_handler(websocket):
    while True:
        print("while true")
        message = await producer()
        await websocket.send(message)

async def hello(websocket):
    await asyncio.gather(
        consumer_handler(websocket),
        producer_handler(websocket),
    )

async def main():
    async with serve(hello, "localhost", 5001):
        await asyncio.get_running_loop().create_future()
        asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())