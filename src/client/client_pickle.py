"""
Client não-bloqueante para receber objetos pickle via TCP com framing (prefixo 4 bytes - tamanho em network order).
Adaptado do código do usuário para funcionar sem bloquear (setblocking(False)) e sem threads.

Como usar (servidor deve enviar: struct.pack('!I', len(payload)) + payload):
    payload = pickle.dumps(obj)
    conn.sendall(struct.pack('!I', len(payload)) + payload)

O método `receive()` foi mantido com assinatura parecida: retorna a PRIMEIRA mensagem disponível ou None.
Se quiser receber todas as mensagens disponíveis, use `receive_all()`.

"""

import socket
import struct
import pickle
import time


class ClientPickle:
    def __init__(self, port=5001, host=None):
        # host padrão: hostname local (igual ao código original)
        self.host = host or socket.gethostname()
        self.port = port
        self.psocket = None
        self._recv_buffer = bytearray()
        
    def _try_connect(self):
        try:
            self.psocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.psocket.connect((self.host, self.port))
            self.psocket.setblocking(False)
            self._recv_buffer.clear()
            return True
        except (ConnectionRefusedError, OSError):
            self.psocket = None
            return False

    def _recv_from_socket(self):
        """Tenta ler dados do socket sem bloquear. Se não houver dados, simplesmente retorna.
        Lança ConnectionError se a conexão foi fechada pelo servidor.
        """
        if self.psocket is None:
            if not self._try_connect():
                return
                
        try:
            while True:
                data = self.psocket.recv(65536)
                if not data:
                    # Conexão fechada pelo servidor
                    self.psocket.close()
                    self.psocket = None
                    raise ConnectionError("Conexão fechada pelo servidor")
                self._recv_buffer += data
        except BlockingIOError:
            # nenhum dado disponível no momento (não bloqueante)
            pass
        except ConnectionResetError:
            # servidor desconectou abruptamente
            self.psocket.close()
            self.psocket = None
            raise ConnectionError("Conexão resetada pelo servidor")
        except OSError:
            self.psocket = None

    def _extract_messages(self):
        """Extrai todas as mensagens completas do _recv_buffer usando framing de 4 bytes (big-endian unsigned int).
        Retorna lista de objetos desserializados (pickle).
        """
        messages = []
        header_len = 4
        while True:
            if len(self._recv_buffer) < header_len:
                break  # nem mesmo o cabeçalho chegou
            # lê o tamanho da próxima mensagem
            msg_len = struct.unpack('!I', self._recv_buffer[:header_len])[0]
            if len(self._recv_buffer) < header_len + msg_len:
                break  # mensagem incompleta
            payload = bytes(self._recv_buffer[header_len:header_len + msg_len])
            # remove a mensagem do buffer
            del self._recv_buffer[:header_len + msg_len]
            try:
                obj = pickle.loads(payload)
                messages.append(obj)
            except Exception as e:
                import traceback
                traceback.print_exc()
                # se o pickle estiver corrompido, ignora essa mensagem e continua
                # (pode-se adicionar logging/alerta aqui)
                continue
        return messages

    def receive(self):
        """Tenta receber a mensagem mais recente; não bloqueante.
        - Retorna o objeto desserializado mais recente se houver mensagens completas.
        - Retorna None se não houver mensagem no momento.
        - Raise ConnectionError se a conexão for fechada pelo servidor.
        """
        # tenta puxar dados do kernel sem bloquear
        self._recv_from_socket()
        msgs = self._extract_messages()
        if msgs:
            return msgs[-1] # Retorna a mais recente e descarta as intermediárias
        return None

    def receive_all(self):
        """Retorna uma lista com todas as mensagens completas disponíveis no buffer (pode ser vazia)."""
        self._recv_from_socket()
        return self._extract_messages()

    def run(self, sleep_seconds=0.0001):
        """Loop de exemplo que processa mensagens conforme chegam. Evita busy-loop com sleep pequeno.
        Não usa threads. Chame run() apenas se quiser que este processo bloqueie a thread principal.
        """
        try:
            while True:
                msgs = self.receive_all()
                for m in msgs:
                    # aqui você pode processar cada mensagem como quiser
                    print('Recebido:', m)
                # pequeno sono cooperativo para não consumir 100% CPU
                # time.sleep(sleep_seconds)
        except ConnectionError:
            print('Conexão encerrada pelo servidor')
        finally:
            self.end()

    def end(self):
        try:
            self.psocket.close()
        except Exception:
            pass

    def __del__(self):
        try:
            if self.psocket:
                self.psocket.close()
        except Exception:
            pass


if __name__ == '__main__':
    client = ClientPickle(port=5001)
    # exemplo: usar receive() num loop do seu app (não bloqueante)
    # while True:
    #     msg = client.receive()
    #     if msg is not None:
    #         print('Recebeu:', msg)
    #     # faça outras tarefas do app aqui (UI, lógica, etc.)
    #     time.sleep(0.01)

    # ou rode o loop interno de exemplo (vai bloquear a thread principal)
    client.run()

    print('Cliente iniciado (não executando loop). Use client.receive() ou client.run() conforme precisar.')


# import socket
# import pickle

# class ClientPickle:
#     def __init__(self, port=5001):
#         self.host =socket.gethostname()
#         self.port = port
#         self.psocket = socket.socket()
#         self.psocket.connect((self.host, self.port))
#         #while True:
#         #    self.receive()
#         self.psocket.setblocking(False)
        

#     def receive(self):
#         try:
#             # socket.setdefaulttimeout(1/30)
#             data = self.psocket.recv(15000)
#             message = pickle.loads(data)
#             #print('Received from server: <type> -> ', type(message), '\n',str(message))
#             return message
#         except BlockingIOError:
#             # nenhum dado disponível no momento (não bloqueante)
#             return None
#         except:
#             # servidor desconectou abruptamente
#             raise ConnectionError("Conexão resetada pelo servidor")

#     def end(self):
#         self.psocket.close()
    
#     def run(self):
#         while True:
#             self.receive()

# if __name__ == '__main__':
#     client = ClientPickle()
#     client.run()