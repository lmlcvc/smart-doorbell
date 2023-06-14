from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, \
    QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSize

import sys
import time
import cv2
import os

from widgets.IconPushButton import IconPushButton


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


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Patterns detection")
        self.setGeometry(0, 0, 800, 480)

        # Main menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")

        self.menu_about = self.menu.addMenu("&About")

        # Create a label for the display camera
        self.label = QLabel(self)
        self.label.setFixedSize(580, 420)

        self.button_settings = IconPushButton("settings", "settings")
        self.button_unlock = IconPushButton("unlock", "unlock")
        self.button_save = IconPushButton("save", "save")
        self.button_silent = IconPushButton("ignore", "ignore")
        extra_buttons = [self.button_settings, self.button_unlock, self.button_save, self.button_silent]
        [button.setFixedSize(160, 48) for button in extra_buttons]

        extra_buttons_layout = QVBoxLayout()
        extra_buttons_layout.addWidget(self.button_settings, alignment=Qt.AlignCenter)
        extra_buttons_layout.addWidget(self.button_unlock, alignment=Qt.AlignCenter)
        extra_buttons_layout.addWidget(self.button_save, alignment=Qt.AlignCenter)
        extra_buttons_layout.addWidget(self.button_silent, alignment=Qt.AlignCenter)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.label)
        top_layout.addLayout(extra_buttons_layout)

        # Thread in charge of updating the image
        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updateFrame.connect(self.set_image)

        # Buttons layout 1
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop/Close")
        self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)

        # Right layout for unlock button
        right_layout = QVBoxLayout()
        right_layout.addStretch()  # Add stretchable space to center the buttons vertically

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(buttons_layout)
        layout.addStretch(1)  # Add stretchable space to push the buttons to the right

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connections
        self.button1.clicked.connect(self.start)
        self.button2.clicked.connect(self.kill_thread)
        self.button2.setEnabled(False)

    @pyqtSlot()
    def kill_thread(self):
        print("Finishing...")
        self.button2.setEnabled(False)
        self.button1.setEnabled(True)
        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status = False
        self.th.terminate()
        # Give time for the thread to finish
        time.sleep(1)

    @pyqtSlot()
    def start(self):
        print("Starting...")
        self.button2.setEnabled(True)
        self.button1.setEnabled(False)
        self.th.start()

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())
