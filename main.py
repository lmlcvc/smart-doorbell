import os
import shutil
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, \
    QWidget, QLineEdit, QMessageBox, QInputDialog, QFileDialog
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

        # Create a label for the display camera
        self.camera_feed = QLabel(self)
        self.camera_feed.setFixedSize(420, 315)

        # Create a label for door open warning
        self.warning_label = QLabel(self)
        self.warning_label.setText("")
        self.warning_label.setStyleSheet("color: red")

        self.button_settings = IconPushButton("settings", "settings")
        self.button_unlock = IconPushButton("unlock", "unlock")
        self.button_save = IconPushButton("save", "save")
        self.button_add_user = IconPushButton("add user", "add_user")
        self.button_silent = IconPushButton("ignore", "ignore")
        extra_buttons = [self.button_settings, self.button_unlock, self.button_save, self.button_add_user,
                         self.button_silent]
        [button.setFixedSize(160, 48) for button in extra_buttons]

        extra_buttons_layout = QVBoxLayout()
        [extra_buttons_layout.addWidget(button, alignment=Qt.AlignCenter) for button in extra_buttons]

        feed_layout = QVBoxLayout()
        feed_layout.setAlignment(Qt.AlignTop)
        feed_layout.addWidget(self.camera_feed)
        feed_layout.addWidget(self.warning_label, alignment=Qt.AlignCenter)

        top_layout = QHBoxLayout()
        top_layout.addLayout(feed_layout)
        top_layout.addLayout(extra_buttons_layout)

        # Re-training model label
        self.retrain_label = QLabel("Re-training model...", self)
        self.retrain_label.setObjectName("retrain_label")
        self.retrain_label.setAlignment(Qt.AlignCenter)
        feed_layout.addWidget(self.retrain_label)  # Add the re-training model label to the layout
        self.retrain_label.hide()

        # Facial recognition
        self.facial_recognition = FacialRecognition(self)
        self.facial_recognition.finished.connect(self.close)
        self.facial_recognition.update_frame.connect(self.set_image)
        self.facial_recognition.update_warning.connect(self.set_warning)

        # Model
        self.train_model = TrainModel()
        self.train_thread = TrainThread(self.train_model)
        self.train_thread.training_finished.connect(self.training_finished)

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
        self.button_add_user.clicked.connect(self.add_user)

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
        self.settings_tray.refresh_settings_window()

    def kill_thread(self):
        print("Finishing thread")
        self.facial_recognition.status = False
        self.facial_recognition.finish_thread = True
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)

    def start(self):
        self.facial_recognition.start()
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)

    def set_image(self, image):
        self.camera_feed.setPixmap(QPixmap.fromImage(image))

    def set_warning(self, status):
        if status is True:
            self.warning_label.setText("Door is still open!")
        else:
            self.warning_label.setText("")

    def save_user(self):
        self.capture_images = []  # Reset the captured images list
        self.capture_counter = 0  # Reset the capture counter
        self.capture_timer.start()  # Start the timer to capture images

    def training_finished(self):
        self.train_thread.status = False
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
                            self.retrain_label.show()  # Show the re-training model label
                            self.train_thread.status = True
                            self.train_thread.start()  # Start the train thread
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

    def add_user(self):
        name, ok = QInputDialog.getText(self, "Add User", "Enter the user name:")
        if ok and name:
            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png)")
            if file_dialog.exec_():
                files = file_dialog.selectedFiles()
                user_directory = os.path.join("dataset", name)
                if not self.train_model.user_exists(name) and not os.path.exists(user_directory):
                    os.makedirs(user_directory)
                    for i, file in enumerate(files):
                        src_path = file
                        dest_path = os.path.join(user_directory, f"{name}_{i + 1}.jpg")
                        shutil.copyfile(src_path, dest_path)

                    # Refresh the settings window to include the new user
                    self.settings_tray.refresh_settings_window()
                    QMessageBox.information(self, "User Added", "New user added successfully.")

                    self.retrain_label.show()  # Show the re-training model label
                    self.train_thread.status = True
                    self.train_thread.start()  # Start the train thread
                else:
                    QMessageBox.warning(self, "Error", "User already exists.")
        else:
            QMessageBox.warning(self, "Error", "Invalid user name.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
