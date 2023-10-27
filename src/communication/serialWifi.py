from tools import encodeSpeeds
import serial.tools.list_ports
import serial
import subprocess
import world
import constants
import time

class SerialRadio():
  """Implementa a comunicação usando simplesmente a interface serial"""
  def __init__(self, control = False, debug = False):

    self.serial = None
    self.failCount = 0
    self.control = control
    self.debug = debug

  def closeSerial(self):
    if self.serial is not None: self.serial.close()

  def send(self, msg, waitack=True):
    """Envia a mensagem via barramento serial em `/dev/ttyUSB*`."""
    try:
      if self.serial is None:
        
        porta = [port.device for port in serial.tools.list_ports.comports()][0]
        subprocess.Popen("echo '04594618189' | sudo -S  chmod a+rw "+porta , stdout=subprocess.PIPE, shell=True)
        print("Acessando a porta USB", porta)
        self.serial = serial.Serial(porta, 115200)
        self.serial.timeout = 0.100
        
    except Exception as e:
      if(constants.SHOW_DEBUG_WIFI_ERROR):
        print("FALHA AO ABRIR SERIAL, Erro:", e)
      return

    # Início da mensagem
    message = bytes("BBB", encoding='ascii')

    # Checksum
    checksum = 0

    # Vetor de dados
    data = [0] * 6

    # Adiciona as velocidades ao vetor de dados

    for i,(vr,vl) in enumerate(msg):
      if(self.debug and self.serial is not None):
        print(f"ROBO {i} | VL {vl} | VR {vr}")
      data[i] = vl
      data[i+3] = vr

      # Computa o checksum
      checksum += vl+vr

    # Concatena o vetor de dados à mensagem
    for v in data: message += (v).to_bytes(2,byteorder='little', signed=True)

    # Concatena com o checksum
    limitedChecksum = (1 if checksum >= 0 else -1) * (abs(checksum) % 32767)
    message += (limitedChecksum).to_bytes(2,byteorder='little', signed=True)

    # Envia
    try:
      self.serial.write(message)
      if waitack:
        response = self.serial.readline().decode()
        try:
          result = list(map(lambda x:int(x), response.replace("\n","").split("\t")))
          if len(result) != 3: print("ACK de tamanho errado")
          else:
            if result[0] != limitedChecksum or result[1] != data[0] or result[2] != data[3]:
              print("Enviado:\t" + str(limitedChecksum) + "\t" + str(data[0]) + "\t" + str(data[3]))
              print("Falha no checksum")
              print("ACK:\t\t" + response)
        except:
          #print("Enviado:\t" + str(data[0]) + " " + str(data[5]) + " " + ' '.join([hex(c) for c in list(message)]))
          print(data)
          print(limitedChecksum)
          print("ACK:\t\t" + response)
          
    except Exception as e:
      self.failCount += 1
      print("Falha ao enviar: " + str(self.failCount) + ", " + str(e))

      if self.failCount >= 30:
        self.serial.close()
        self.serial = None
        self.failCount = 0