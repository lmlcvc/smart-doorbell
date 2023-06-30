import os
import shutil

from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QCheckBox, QPushButton, QSpacerItem, QSizePolicy, QLineEdit, QInputDialog, QMessageBox
)

from util.train_thread import TrainThread
from widgets.IconPushButton import IconPushButton


class SettingsTray(QFrame):
    def __init__(self, train_model):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        tray_width = 800
        tray_height = 400
        self.setFixedSize(tray_width, tray_height)

        # An instance of TrainModel
        self.train_model = train_model

        # Create the main layout
        layout = QVBoxLayout()

        # TODO: Implement mailing API
        # # Add email notifications checkbox
        # self.email_checkbox = QCheckBox("Enable Email Notifications")
        # layout.addWidget(self.email_checkbox)

        # Add label for the list of users
        self.users_label = QLabel("List of Users:")
        layout.addWidget(self.users_label)

        # Create a scroll area for the user list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()

        layout.addWidget(self.scroll_area)

        # Add Close and Retrain buttons
        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.retrain_button = QPushButton("Retrain Model")
        self.retrain_button.setFixedWidth(160)
        self.retrain_button.clicked.connect(self.retrain_model)
        button_layout.addWidget(self.retrain_button)

        self.close_button = QPushButton("Close")
        self.close_button.setFixedWidth(80)
        self.close_button.clicked.connect(self.hide)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        # Create a train thread instance
        self.train_thread = TrainThread(train_model)
        self.train_thread.train_model.training_update.connect(self.training_progress)
        self.train_thread.training_finished.connect(self.training_finished)

        # Create the label for retraining status
        self.status_label = QLabel("")

        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Refresh the settings window
        self.refresh_settings_window()

    def edit_name(self, user):
        new_name, ok = QInputDialog.getText(self, "Edit Name", "Enter a new name:", QLineEdit.Normal, user["name"])
        if ok and new_name:
            old_path = os.path.join("dataset", user["name"])
            new_path = os.path.join("dataset", new_name)
            QDir().rename(old_path, new_path)

            user["name_label"].setText(new_name)  # Update the label text
            self.train_model.rename_user(user["name"], new_name)

    def delete_user(self, user):
        confirm_dialog = QMessageBox.question(
            self, "Delete User",
            f"Are you sure you want to delete the user '{user['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm_dialog == QMessageBox.Yes:
            user_directory = os.path.join("dataset", user["name"])
            shutil.rmtree(user_directory)

            self.train_model.delete_user(user["name"])
            self.refresh_settings_window()

    def retrain_model(self):
        # Disable the retrain button
        self.retrain_button.setEnabled(False)

        # Show "re-training model..." message
        self.status_label.setText("Re-training model...")

        # Start the train thread
        self.train_thread.start()

    def training_progress(self, progress):
        # Show training finished message
        self.status_label.setText(f"Re-training model...{progress}%")

    def training_finished(self):
        # Enable the retrain button
        self.retrain_button.setEnabled(True)

        # Show training finished message
        self.status_label.setText("Training finished.")

        # Refresh the settings window
        self.refresh_settings_window()

    def refresh_settings_window(self):
        # Clear the existing layout
        self.clear_scroll_layout()

        dataset_path = "dataset"
        users = []

        # Collect user information
        for name in sorted(os.listdir(dataset_path)):
            name_path = os.path.join(dataset_path, name)
            if os.path.isdir(name_path):
                user = {
                    "name": name,
                    "image": None,
                    "edit_button": None,
                    "name_label": None
                }
                images = os.listdir(name_path)
                if images:
                    image_path = os.path.join(name_path, images[0])
                    user["image"] = image_path
                users.append(user)

        # Sort the users based on names
        users = sorted(users, key=lambda x: x["name"].lower())

        name_label_width = 120
        name_label_tooltip_length = name_label_width - 20
        image_height = 96
        button_width = 120
        button_height = 48

        # Remove old name labels
        for user in users:
            name_label = user["name_label"]
            if name_label:
                name_label.setParent(None)
                name_label.deleteLater()

        for user in users:
            user_layout = QHBoxLayout()

            # Create and configure the name label
            name_label = QLabel(user["name"])
            name_label.setFixedWidth(name_label_width)
            name_label.setToolTip(user["name"] if len(user["name"]) > name_label_tooltip_length else "")
            font_metrics = name_label.fontMetrics()
            elided_text = font_metrics.elidedText(user["name"], Qt.ElideRight, name_label_tooltip_length)
            name_label.setText(elided_text)
            name_label.setStyleSheet("font-weight: bold;")
            user_layout.addWidget(name_label)
            user["name_label"] = name_label

            # Create and configure the image label
            image_label = QLabel()
            if user["image"]:
                pixmap = QPixmap(user["image"]).scaledToHeight(image_height)
                image_label.setPixmap(pixmap)
            user_layout.addWidget(image_label)

            # Create and configure the edit button
            edit_button = IconPushButton("edit", "edit")
            edit_button.setFixedSize(button_width, button_height)
            edit_button.setLayoutDirection(Qt.LeftToRight)
            user_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
            user_layout.addWidget(edit_button)
            user["edit_button"] = edit_button

            # Create and configure the delete button
            delete_button = IconPushButton("delete", "delete")
            delete_button.setFixedSize(button_width, button_height)
            delete_button.setLayoutDirection(Qt.LeftToRight)
            user_layout.addWidget(delete_button)

            # Connect the edit button click signal to the edit_name slot
            edit_button.clicked.connect(lambda _, user=user: self.edit_name(user))
            delete_button.clicked.connect(lambda _, user=user: self.delete_user(user))

            # Add the user layout to the scroll layout
            self.scroll_layout.addLayout(user_layout)

        # Set the scroll widget layout and adjust the size
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        # Force the scroll area to update its layout
        self.scroll_area.updateGeometry()

        # Adjust the size of the settings tray
        self.adjustSize()

    def clear_scroll_layout(self):
        # Clear the existing layout and delete the widgets
        scroll_layout = self.scroll_layout
        while scroll_layout.count():
            item = scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
