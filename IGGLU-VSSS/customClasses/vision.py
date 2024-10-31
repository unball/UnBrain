"""
def process(self, frame):

# Mensagem de retorno
mensagem = VisionMessage(5)

# Corta o campo
img_warpped = self.warp(frame)

# Formata como HSV
img_hsv = self.converterHSV(img_warpped)

# Segmenta o que não é o fundo
fgMask = self.obterMascaraElementos(img_hsv)

# Segmenta o time
teamMask = self.obterMascaraTime(img_hsv)

# Segmenta a bola
bolaMask = self.obterMascaraBola(img_hsv)

# Tenta identificar uma bola
bola = self.identificarBola(bolaMask & fgMask)
mensagem.setBall(bola)

# O que não é fundo nem bola
fgMaskNoBall = cv2.bitwise_and(fgMask, cv2.bitwise_not(bolaMask))

# Encontra componentes conectados e aplica operações de abertura e dilatação
components = self.obterComponentesConectados(fgMaskNoBall)

#print([x.meanId for x in self._world.robots])

# Itera por cada elemento conectado
for componentMask in components:
    
  # Obtém dados do componente como uma camisa
  camisa = self.detectarCamisa(componentMask)
  
  # Camisa tem área pequena
  if camisa is None: continue
  
  centro, centerMeters, angulo, camisaContours = camisa
  
  # Máscara dos componentes internos do elemento
  componentTeamMask = componentMask & teamMask
  
  # Tenta identificar um aliado
  aliado = self.detectarTime(componentTeamMask, centro, angulo, centerMeters)
  if aliado is not None:
    mensagem.setRobot(aliado[0], (*centerMeters, aliado[1]*np.pi/180), internalContours=aliado[2])
  
  # Adiciona camisa como adversário
  else:
    mensagem.setEnemyRobot((*centerMeters, angulo*np.pi/180), extContour=camisaContours)

return mensagem

"""
from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal, Slot

from customClasses.elements import *
from customClasses.layouts import *
from typing import List, Tuple
import cv2 as cv
import numpy as np
import pdb
class Vision(QWidget):
    def __init__(self, editorFrame) -> None:
      super().__init__()
      self.editorFrame = editorFrame
      self.editorFrame.edited.connect(self.updateBaseImage)
      
      self.baseImage = self.editorFrame.editedImage.copy()
      
    def pixelToMeters(self, x: float, y:float) -> float:      
      scaledWidth = 640
      scaledHeight = 640

      realWidth = 1.75
      realHeight = 1.35

      widthRatio = realWidth / scaledWidth
      heightRatio = -1 * (realHeight / scaledHeight)

      realX = x * widthRatio
      realY = y * heightRatio

      realX = x - scaledWidth / 2
      realY = y - scaledHeight / 2
      
      
      realX *= widthRatio
      realY *= heightRatio
      
      return realX, realY
    
    @Slot(QPixmap)
    def updateBaseImage(self, image: QPixmap) -> None:
      self.baseImage = image.copy()
    
    def findBall(self, segImageBytes: bytes, minArea: float = 10.0) -> Tuple[float]:
      segImage = np.frombuffer(segImageBytes, dtype=np.uint8)
      ballContours,_ = cv.findContours(segImage, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
      ballContours = [countor for countor in ballContours if cv.contourArea(countor) >= minArea]

      if len(ballContours) != 0:
        bolaContour = max(ballContours, key=cv.contourArea)
        ((x,y), radius) = cv.minEnclosingCircle(bolaContour)
        
        return (self.pixelToMeters(x,y), radius)
      
      return None