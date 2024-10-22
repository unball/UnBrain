from PIL import Image
import cv2 as cv
from PySide6.QtWidgets import QFrame, QLabel, QMainWindow, QApplication
from PySide6.QtGui import QCursor, QPainter, QPixmap, QColor, QPen, QImage
from PySide6.QtCore import Qt, QSize, QPoint, QPointF, QRect
import numpy as np
    

class Editor(QLabel):
    def __init__(self, parent, defaultImage):
        super().__init__(parent)
        
        self.defaultImage = defaultImage
        self.setPixmap(self.defaultImage)
    
    def clearFrame(self):
        self.setPixmap(self.defaultImage.copy())
    
    def calcRelativePosition(self, position):
        labelPosition = position
        labelSize = self.size()
        
        pixmapSize = self.pixmap().size()
        relativePosition = labelPosition - self.rect().topLeft()
        
        pixmapPosition = QPointF(
            (relativePosition.x() * pixmapSize.width() / labelSize.width()),
            (relativePosition.y() * pixmapSize.height() / labelSize.height())
        )
        
        return pixmapPosition

class SegmentEditor(Editor):
    def __init__(self, parent, defaultImage):
        super().__init__(parent, defaultImage)
       
        self.hsvRange = [0, 38, 198, 179, 255, 255]
        
        self.segmentedImage = self.defaultImage.copy()
    
    def segmentImage(self):
        image = self.defaultImage.copy()
        height, width = image.height(), image.width()
        
        cvImage = self.pixmapToCv(image)
        hsvImage = cv.cvtColor(cvImage, cv.COLOR_BGR2HSV)
       
        minHsv = np.array(self.hsvRange[0:3])
        maxHsv = np.array(self.hsvRange[3:6])
            
        mask = cv.inRange(hsvImage, minHsv, maxHsv)
        
        self.segmentedImage = self.cvToPixmap(mask, width, height)
        self.setPixmap(self.segmentedImage)
        
    def pixmapToCv(self, qpixmap):
        qimage = qpixmap.toImage()
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        
        height, width = qimage.height(), qimage.width()
        channels = qimage.depth() // 8
        
        cvImage = np.frombuffer(qimage.bits(), dtype=np.uint8, count=height * width * channels).reshape((height, width, channels))
        
        return cvImage
    
    def cvToPixmap(self, cvImage, width, height):
        bgrImage = cv.cvtColor(cvImage, cv.COLOR_GRAY2BGR) 
        qimage = QImage(bgrImage.data, width, height, width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        return pixmap
    
    def updateMinHue(self, value):
        self.hsvRange[0] = value
        self.segmentImage()
        
    def updateMaxHue(self, value):
        self.hsvRange[3] = value
        self.segmentImage()
    
    def updateMinSaturation(self, value):
        self.hsvRange[1] = value
        self.segmentImage()
        
    def updateMaxSaturation(self, value):
        self.hsvRange[4] = value
        self.segmentImage()
    
    def updateMinValue(self, value):
        self.hsvRange[2] = value
        self.segmentImage()
        
    def updateMaxValue(self, value):
        self.hsvRange[5] = value
        self.segmentImage()
        
class CropEditor(Editor):
    def __init__(self, parent, defaultImage):
        super().__init__(parent, defaultImage)
        
        self.croppedImage = self.defaultImage.copy()
        
        self.pen = QPen()
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setColor(Qt.red)
        
        self.clickedPoints = []
    
    def mousePressEvent(self, event):
        position = event.position()
        pixmap_position = self.calcRelativePosition(position)
        
        if len(self.clickedPoints) <= 2:
            self.clickedPoints.append(position)
            self.drawPoint(pixmap_position)
            
        elif len(self.clickedPoints) == 3:
            self.clickedPoints.append(position)
            rect = list(map(self.calcRelativePosition, self.clickedPoints))
            self.drawRect(rect)
        else:
            self.clearFrame()
            self.clickedPoints.clear()
            
        
    def drawPoint(self, pixmap_position):
        canvas = self.pixmap()

        painter = QPainter(canvas)
        self.pen.setWidth(10)
        painter.setPen(self.pen)
        painter.drawPoint(pixmap_position.x(), pixmap_position.y())
        painter.end()

        self.setPixmap(canvas)
    
    def drawRect(self, rect):
        self.drawPoint(rect[-1])
        canvas = self.pixmap()

        painter = QPainter(canvas)
        self.pen.setWidth(1)
        painter.setPen(self.pen)
        painter.drawPolygon(rect)
        painter.end()
        
        self.cropImage(rect)
        self.setPixmap(canvas)
    
    def cropImage(self, points):
        p1 = QPointF(points[0]).toPoint()
        p2 = QPointF(points[2]).toPoint()
        rect = QRect(p1, p2)
        self.croppedImage = self.defaultImage.copy(rect)
    
    def showCroppedImage(self):
        self.setPixmap(self.croppedImage)