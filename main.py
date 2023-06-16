import os

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, \
    QWidget, QLineEdit, QMessageBox, QInputDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

import sys

from util.facial_req import FacialRecognition
from util.settings_tray import SettingsTray
from util.train_model import TrainModel
from util.train_thread import TrainThread
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

        # Re-training model label
        self.retrain_label = QLabel("Re-training model...", self)
        self.retrain_label.setObjectName("retrain_label")
        self.retrain_label.setAlignment(Qt.AlignCenter)
        self.retrain_label.hide()

        # Facial recognition
        self.facial_recognition = FacialRecognition(self)
        self.facial_recognition.finished.connect(self.close)
        self.facial_recognition.update_frame.connect(self.set_image)

        # Model
        self.train_model = TrainModel()
        self.train_thread = TrainThread(self.train_model)

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
        layout.addWidget(self.retrain_label)  # Add the re-training model label to the layout

        # Settings dialog
        self.settings_tray = SettingsTray(self.train_model)

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
        self.button_save.clicked.connect(self.save_user)

        # Timer for capturing images
        self.capture_timer = QTimer()
        self.capture_timer.setInterval(1000)  # 1 second interval
        self.capture_timer.timeout.connect(self.capture_image)
        self.capture_counter = 0
        self.capture_images = []

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

    def save_user(self):
        self.capture_images = []  # Reset the captured images list
        self.capture_counter = 0  # Reset the capture counter
        self.capture_timer.start()  # Start the timer to capture images

    def training_finished(self):
        self.retrain_label.hide()  # Hide the re-training model label after training finished

    def capture_image(self):
        if self.capture_counter < 5:
            image = self.facial_recognition.get_frame_image()  # Capture the current frame image
            if image is not None:
                self.capture_images.append(image)  # Add the image to the captured images list
                self.capture_counter += 1  # Increment the capture counter

                if self.capture_counter == 5:
                    # Stop the timer after capturing 5 images
                    self.capture_timer.stop()

                    # Prompt the user to enter a name for the new user
                    name, ok = QInputDialog.getText(self, "New User", "Enter the user name:")
                    if ok and name:
                        user_directory = os.path.join("dataset", name)
                        if not self.train_model.user_exists(name) and not os.path.exists(user_directory):
                            os.makedirs(user_directory)
                            for i, img in enumerate(self.capture_images):
                                img_path = os.path.join(user_directory, f"{name}_{i + 1}.jpg")
                                img.save(img_path)

                            # Refresh the settings window to include the new user
                            self.settings_tray.refresh_settings_window()
                            QMessageBox.information(self, "User Saved", "New user saved successfully.")
                        else:
                            QMessageBox.warning(self, "Error", "User already exists.")

                        self.capture_images = []  # Clear the captured images list
                        self.capture_counter = 0  # Reset the capture counter
        else:
            # Stop the timer if the desired number of images has been captured
            self.capture_timer.stop()
            QMessageBox.warning(self, "Error", "Failed to capture images.")

            self.capture_images = []  # Clear the captured images list
            self.capture_counter = 0  # Reset the capture counter
            return
        self.retrain_label.show()  # Show the re-training model label
        self.train_thread.start()  # Start the train thread


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
