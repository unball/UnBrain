import threading
import websockets.sync.server as sync_ws
import time
import websockets
import pickle
import numpy as np
import matplotlib.pyplot as plt

def producer():
    while True:
        time.sleep(3)
        message = "Hello !"

def consumer(message):
    print(f'Hello {message}')

class WebSocket:
    def __init__(self, loop, port=5001):
        self.world = loop.world
        self.host = "localhost"
        self.port = port
        self.server = None

    def producer(self):
    # Simula uma tarefa demorada de 3 segundos
        # time.sleep(3)

        # mensagem com infos dos robos e bola
        message_robot = [f"ROBOT {i}: pos {self.world.team[i].pos} vel {self.world.team[i].v};\n" for i in self.world.n_robots]
        message_ball = f"BALL: pos {self.world.ball.pos} vel {self.world.ball.v*400}\n"

        # calculo pra enviar o UVF via mensagem
        def message_uvf(robot_i=2, field_dims=(170*4, 130*4), arrow_spaces=16):
            x = np.arange(-field_dims[0]/2, field_dims[0]/2, arrow_spaces)
            y = np.arange(-field_dims[1]/2, field_dims[1]/2, arrow_spaces)
            X, Y = np.meshgrid(x, y)
            arrow_positions = np.array([X.flatten(), Y.flatten()]).T
        
            robot = self.world.raw_team[robot_i]

            positions = []
            for i in range(arrow_positions.shape[0]):
                positions.append(arrow_positions[i]/400)
            
            angles = list(map(robot.field.F, positions))

            # plt.quiver(X, Y, np.cos(angles), np.sin(angles))
            # plt.draw()
            # plt.pause(1)

            return angles if robot.field is not None else 0
        
        self.message = f"{message_robot[0]}{message_robot[1]}{message_robot[2]}{message_ball};\n UVF:{message_uvf()}" # main.loop.world.team
        
        info = self.message
        print("produzindo")
        return str(info)

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
