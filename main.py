from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, \
    QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QFont, QColor
from PyQt5.QtCore import Qt, pyqtSlot, QPoint

import sys
import time
import cv2

from util.facial_req import FacialRecognition
from widgets.IconPushButton import IconPushButton


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.status = None
        self.setWindowTitle("Patterns detection")
        self.setGeometry(0, 0, 800, 480)

        # Main menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")

        self.menu_about = self.menu.addMenu("&About")

        # Create a label for the display camera
        self.label = QLabel(self)
        self.label.setFixedSize(420, 420)

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

        # Facial recognition
        self.facial_recognition = FacialRecognition(self)
        self.facial_recognition.finished.connect(self.close)
        self.facial_recognition.update_frame.connect(self.set_image)

        # Buttons layout 1
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop/Close")
        self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)

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
        cv2.destroyAllWindows()
        self.status = False
        self.facial_recognition.terminate()
        # Give time for the thread to finish
        time.sleep(1)

    @pyqtSlot()
    def start(self):
        print("Starting...")
        self.button2.setEnabled(True)
        self.button1.setEnabled(False)
        # self.th.start()
        self.facial_recognition.start()

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
