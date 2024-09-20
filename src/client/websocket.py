import threading
import websockets.sync.server as sync_ws
import time
import websockets

def producer():
    while True:
        time.sleep(3)
        message = "Hello !"

def consumer(message):
    print(f'Hello {message}')

class WebSocket:
    def __init__(self, port=5001):
        self.host = "localhost"
        self.port = port
        self.server = None

    def producer(self):
    # Simula uma tarefa demorada de 3 segundos
        time.sleep(3)
        return "Hello from UnBrain!\n"

    def run(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

    def start_server(self):
        if self.server is None:
            with sync_ws.serve(self.handle_connection, host=self.host, port=self.port) as server:
                print(f"WebSocket server running at ws://{self.host}:{self.port}")
                server.serve_forever()
                    
    def handle_connection(self, websocket):
        print(f"New websocket connected\n")
        while True:
            try:
                message = websocket.recv()
                print(f"Message from client: {message}\n")
                websocket.send(f"UnBrain received: {message}\n")
                response = self.producer()
                websocket.send(response)
            except websockets.ConnectionClosed:
                print("Client disconnected\n")
                break


if __name__ == '__main__':
    ws = WebSocket()
    ws.run()
