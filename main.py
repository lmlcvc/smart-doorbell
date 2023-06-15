from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, \
    QWidget
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QPoint

import sys
import time
import cv2

from util.facial_req import FacialRecognition
from util.settings_tray import SettingsTray
from widgets.IconPushButton import IconPushButton


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Title and dimensions
        self.setWindowTitle("Smart doorbell")
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

        # Buttons layout
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

        # Settings dialog
        self.settings_tray = SettingsTray()

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connections
        self.button1.clicked.connect(self.start)
        self.button2.clicked.connect(self.kill_thread)
        self.button2.setEnabled(False)

        self.button_unlock.clicked.connect(self.facial_recognition.handle_unlock_signal)
        self.button_silent.clicked.connect(self.facial_recognition.handle_bell_silent_signal)

        self.button_settings.clicked.connect(self.show_settings)

    def show_settings(self):
        self.settings_tray.show()
        self.settings_tray.adjustSize()
        self.settings_tray.move(
            self.width() - self.settings_tray.width() - 10,
            self.height() - self.settings_tray.height() - 10
        )
        self.settings_tray.setFocus(Qt.PopupFocusReason)

    def kill_thread(self):
        print("Finishing thread")
        self.facial_recognition.finish_thread = True
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)

    def start(self):
        self.facial_recognition.start()
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)

    def set_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
