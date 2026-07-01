import pickle
import socket
import struct
import time
import threading
import queue

class ServerPickle:
    """Servidor compatível com ClientPickle (envia mensagens com framing de 4 bytes + payload pickle).
    Usa fila e thread de background para evitar bloquear a simulação."""

    def __init__(self, port=5001, host=None):
        self.host = host or socket.gethostname()
        self.port = port
        self.psocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.psocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.psocket.bind((self.host, self.port))
        self.psocket.listen(2)
        self.psocket.setblocking(False)
        self.conn = None
        self.address = None
        self.t0 = time.time()
        
        # Desacoplamento para evitar atrasar o FPS do simulador
        self.queue = queue.Queue(maxsize=1)
        self._running = True
        self._sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self._sender_thread.start()

    def _try_accept(self):
        if self.conn is None:
            try:
                self.conn, self.address = self.psocket.accept()
                self.conn.settimeout(0.01)  # timeout reduzido para não travar o sendall
                print("Cliente conectado:", self.address)
            except BlockingIOError:
                pass
            except Exception as e:
                pass

    def _sender_loop(self):
        """Thread que consome a fila e envia pelo socket sem bloquear o motor."""
        while self._running:
            try:
                data = self.queue.get(timeout=0.1)
                if self.conn is None:
                    self._try_accept()
                if self.conn is not None:
                    payload = pickle.dumps(data, protocol=-1)
                    header = struct.pack("!I", len(payload))
                    try:
                        self.conn.sendall(header + payload)
                    except (TimeoutError, socket.timeout):
                        pass # Droppa o frame gracioso se a rede entupir
                    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                        self.conn.close()
                        self.conn = None
            except queue.Empty:
                pass

    def send(self, data):
        """Apenas enfileira o objeto, descartando os antigos se a rede estiver lenta."""
        try:
            self.queue.put_nowait(data)
        except queue.Full:
            try:
                self.queue.get_nowait() # descarta pacote velho
                self.queue.put_nowait(data) # enfileira o mais recente
            except queue.Empty:
                pass
            except queue.Full:
                pass

    def end(self):
        """Fecha conexões com segurança."""
        self._running = False
        if self.conn is not None:
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