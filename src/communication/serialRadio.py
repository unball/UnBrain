import serial
import time

class SerialRadio():
  """Implementa a comunicação usando simplesmente a interface serial"""
  def __init__(self):

    self.serial = None
    self.failCount = 0

  def closeSerial(self):
    if self.serial is not None: self.serial.close()

  def send(self, msg, waitack=True):
    """Envia a mensagem via barramento serial em `/dev/ttyUSB0`."""
    try:
      if self.serial is None:
        self.serial = serial.Serial('/dev/ttyUSB0', 115200)
        self.serial.timeout = 0.100
    except Exception as e:
      print(e)
      print("Falha ao abrir serial")
      return

    # Início da mensagem
    message = bytes("BBB", encoding='ascii')

    # Checksum
    checksum = 0

    # Vetor de dados
    data = [0] * 6

    # Adiciona as velocidades ao vetor de dados
    for i,(vl,vr) in enumerate(msg):

      # Coloca no vetor de dados
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