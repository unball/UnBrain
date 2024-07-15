import pickle
import time
import socket

class ServerPickle:
    def __init__(self, port):

        self.host = socket.gethostname()
        self.port = port
        psocket = socket.socket() 
        psocket.bind((self.host, self.port))
        print('Esperando cliente.....................................')
        psocket.listen(2)
        self.conn, self.address = psocket.accept()  
        print("Connection from: " + str(self.address))
        
        self.t0 = time.time()
        
    def send(self, data):

        # print("envio msg MS:",1000*(time.time()-self.t0))
        self.t0 = time.time()
        
        message = pickle.dumps(data,-1)
        # print("Enviando: ",data)
        # print(len(message))
        self.conn.send(message)
    
    def end(self):
        self.psocket.close()
