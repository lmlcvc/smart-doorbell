from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import sys
import cv2
import os


class Thread(QThread):
    updateFrame = pyqtSignal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.trained_file = os.path.join(os.getcwd(), "haarcascade_frontalface_default.xml")
        self.status = True
        self.cap = True

    def run(self):
        self.cap = cv2.VideoCapture(0)
        while self.status:
            cascade = cv2.CascadeClassifier(self.trained_file)
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Reading frame in gray scale to process the pattern
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detections = cascade.detectMultiScale(gray_frame, scaleFactor=1.1,
                                                  minNeighbors=5, minSize=(30, 30))

            # Drawing green rectangle around the pattern
            for (x, y, w, h) in detections:
                pos_ori = (x, y)
                pos_end = (x + w, y + h)
                color = (0, 255, 0)
                cv2.rectangle(frame, pos_ori, pos_end, color, 2)

            # Reading the image in RGB to display it
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Creating and scaling QImage
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)

            # Emit signal
            self.updateFrame.emit(scaled_img)
        sys.exit(-1)
