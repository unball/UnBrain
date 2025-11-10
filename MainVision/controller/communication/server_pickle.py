import pickle
import socket
import struct
import time


class ServerPickle:
    """Servidor compatível com ClientPickle (envia mensagens com framing de 4 bytes + payload pickle)."""

    def __init__(self, port=5001, host=None):
        self.host = host or socket.gethostname()
        self.port = port
        self.psocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.psocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.psocket.bind((self.host, self.port))
        self.psocket.listen(2)
        print(f"Servidor ouvindo em {self.host}:{self.port}")
        print("Aguardando cliente conectar...")
        self.conn, self.address = self.psocket.accept()
        print("Cliente conectado:", self.address)
        self.t0 = time.time()

    def send(self, data):
        """Envia objeto serializado via pickle com framing de 4 bytes (big-endian)."""
        self.t0 = time.time()
        payload = pickle.dumps(data, protocol=-1)
        header = struct.pack("!I", len(payload))
        self.conn.sendall(header + payload)

    def end(self):
        """Fecha conexões com segurança."""
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        self.conn.close()
        self.psocket.close()


if __name__ == "__main__":
    server = ServerPickle(port=5001)
    count = 0
    t0 = time.time()
    try:
        while True:
            msg = {"counter": count, "timestamp": time.time()-t0}
            server.send(msg)
            print("Enviado:", msg)
            t0 = time.time()
            time.sleep(1)
            count += 1
    except KeyboardInterrupt:
        print("Encerrando servidor...")
    finally:
        server.end()