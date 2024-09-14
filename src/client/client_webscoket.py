from websocket import create_connection

class ClientWebSocket:
    def __init__(self, port=5001):
        self.host="localhost"
        self.port = str(port)
        self.ws = create_connection("ws://"+self.host+":"+self.port)
        self.message = ""

    def send_msg(self):
        self.ws.send("Teste envio")
    
    def recv_msg(self):
        self.message=self.ws.recv()
        print(self.message)

if __name__ == '__main__':
    client = ClientWebSocket()
    client.send_msg()
    client.recv_msg()