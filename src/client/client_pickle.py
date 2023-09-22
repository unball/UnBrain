import socket
import pickle

class ClientPickle:
    def __init__(self, port=5001):
        self.host =socket.gethostname()
        self.port = port
        self.psocket = socket.socket()
        self.psocket.connect((self.host, self.port))
        #while True:
        #    self.receive()

    def receive(self):
        data = self.psocket.recv(15000)
        message = pickle.loads(data)
        #print('Received from server: <type> -> ', type(message), '\n',str(message))
        return message

    def end(self):
        self.psocket.close()
    
    def run(self):
        while True:
            self.receive()

if __name__ == '__main__':
    client = ClientPickle()
    client.run()