from PIL import Image
import cv2 as cv
from PySide6.QtWidgets import QFrame, QLabel, QMainWindow, QApplication
from PySide6.QtGui import QCursor, QPainter, QPixmap, QColor, QPen, QImage
from PySide6.QtCore import Qt, QSize, QPoint, QPointF, QRect
import numpy as np

class Editor:
    def __init__(self) -> None:
        
        self.foregroundHsv = [0, 38, 198, 179, 255, 255]
        self.ballHsv = [0,44,0,82,255,255]
        self.teamHsv = [0,0,0,179,255,255]
    
    def crop(self, image, rect):
        return image.crop(rect)
    
    def wrap(self, image, rect):
        # height, width, _ = shape
    
        # base = np.array([[0,0],[1,0],[1,1],[0,1]])
        # key_points = np.array(points) * np.array([width, height])
        
        # frame_points = base * np.array([width, height])
        
        # h, mask = cv2.findHomography(key_points, frame_points, cv2.RANSAC)
        # homography_matrix = self.getHomography(image.shape)
        # return cv2.warpPerspective(image, np.array(homography_matrix), (image.shape[1], image.shape[0]))
        pass
    
    def convert2Hsv(self, image):
        img_filtered = cv.GaussianBlur(image, (5,5), 0)
        return cv.cvtColor(img_filtered, cv.COLOR_BGR2HSV)
    
    def segment(self, image, find="all"):
        image = self.convert2Hsv(image)
        if find == "all":
            mask = cv.inRange(image, np.array(self.foregroundHsv[0:3]), np.array(self.foregroundHsv[3:6]))
        
        if find == "ball":
            mask = cv.inRange(image, np.array(self.ballHsv[0:3]), np.array(self.ballHsv[3:6]))
        
        if find == "team":
            mask = cv.inRange(image, np.array(self.teamHsv[0:3]), np.array(self.teamHsv[3:6]))
        
        return mask
    
    def brightness(self, image):
        raise NotImplementedError
        
    def contrast(self, image):
        raise NotImplementedError
    
    def sharpness(self, image):
        raise NotImplementedError
    
    def updateFgHsv(self, range):
        self.foregroundHsv = range

    def updateBallHsv(self, range):
        self.ballHsv = range

    def updateTeamHsv(self, range):
        self.teamHsv = range
    

class Editor(QLabel):
    def __init__(self, parent, defaultImagePath):
        super().__init__(parent)
        
        self.defaultImage = QPixmap(defaultImagePath)
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

    

class CropEditor(Editor):
    def __init__(self, parent, defaultImagePath):
        super().__init__(parent, defaultImagePath)
        
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