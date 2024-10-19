import asyncio
from websockets.asyncio.server import serve

global queue
# sleep foi para simular o tempo que o Loop demora para ser executado
async def producer():
    await asyncio.sleep(3)
    return "Hello from UnBrain!\n"

async def consumer(message):
    print(f'Message from client: {message}\n')
    #await queue.put(message)

class WebSocket:
    def __init__(self, port=5001):
        self.host="localhost"
        self.port = port
        self.message = ""
        self.queue = queue
    
    def run(self):
        asyncio.run(main())

async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)
        await websocket.send(f"UnBrain received: {message}\n")

async def producer_handler(websocket):
    while True:
        message = await producer()
        await websocket.send(message)

async def hello(websocket):
    print(f"New websocket connected\n")
    await asyncio.gather(
        consumer_handler(websocket),
        producer_handler(websocket),
    )

async def main():
    async with serve(hello, "localhost", 5001):
        await asyncio.get_running_loop().create_future()


if __name__ == '__main__':
    asyncio.run(main())