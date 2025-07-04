import pickle
import time
import socket
import threading

class ServerPickle:
    def __init__(self, port):
        self.host = socket.gethostname()
        self.port = port
        self.psocket = socket.socket()
        self.psocket.bind((self.host, self.port))
        self.psocket.listen(2)
        
        self.conn = None
        self.address = None
        self.t0 = time.time()

        # Cria uma thread para aceitar a conexão
        self.accept_thread = threading.Thread(target=self._accept_connection)
        self.accept_thread.daemon = True
        self.accept_thread.start()

    def _accept_connection(self):
        print('Esperando cliente.....................................')
        self.conn, self.address = self.psocket.accept()
        print("Conectado com:", self.address)

    def send(self, data):
        if self.conn is None:
            print("[ServerPickle] Ainda aguardando conexão do cliente...")
            return
        
        self.t0 = time.time()
        message = pickle.dumps(data, -1)
        self.conn.send(message)
        # print("Enviando: ",data)
        # print(len(message))

    def end(self):
        if self.conn:
            self.conn.close()
        self.psocket.close()
