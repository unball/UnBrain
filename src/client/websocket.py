import threading
import websockets.sync.server as sync_ws
import time
import websockets
import pickle
import numpy as np
import matplotlib.pyplot as plt
import msgpack

def producer():
    while True:
        time.sleep(3)
        message = "Hello !"

def consumer(message):
    print(f'Hello {message}')

class WebSocket:
    def __init__(self, loop, port=5001):
        self.loop = loop
        self.host = "localhost"
        self.port = port
        self.server = None

    def producer(self):
    # Simula uma tarefa demorada de 3 segundos
        # time.sleep(3)

        # mensagem com infos dos robos e bola
        message_robot = {f"ROBOT {i}": list(self.loop.world.team[i].pos)+list(self.loop.world.team[i].v) for i in self.loop.world.n_robots if i is not None}
        message_ball = list(self.loop.world.ball.pos)+list(self.loop.world.ball.v) # lembrar de multiplicar a velocidade por 400 (n sei pq)

        # calculo pra enviar o UVF via mensagem
        def message_uvf(robot_i=2, field_dims=(170*4, 130*4), arrow_spaces=16):
            x = np.arange(-field_dims[0]/2, field_dims[0]/2, arrow_spaces)
            y = np.arange(-field_dims[1]/2, field_dims[1]/2, arrow_spaces)
            X, Y = np.meshgrid(x, y)
            arrow_positions = np.array([X.flatten(), Y.flatten()]).T
        
            robot = self.loop.world.raw_team[robot_i]

            positions = []
            for i in range(arrow_positions.shape[0]):
                positions.append(arrow_positions[i]/400)
            
            angles = list(map(robot.field.F, positions))

            return angles if robot.field is not None else 0
        
        # self.message = f"{message_robot[0]}{message_robot[1]}{message_robot[2]}{message_ball};\n UVF:{message_uvf()}" # main.loop.world.team
        self.message = {"TEAM": message_robot, 
                        "BALL": message_ball}
        
        if self.loop.draw_uvf:
            self.message["UVF"] = message_uvf()

        packed_message = msgpack.packb(self.message)
        print(msgpack.unpackb(packed_message)["BALL"])
        
        info = packed_message
        print("produzindo")
        return info

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
