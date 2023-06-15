from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QCheckBox, QPushButton, QSpacerItem, QSizePolicy

from widgets.IconPushButton import IconPushButton

import os

class SettingsTray(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        tray_width = 800
        tray_height = 400
        self.setFixedSize(tray_width, tray_height)

        layout = QVBoxLayout()

        self.email_checkbox = QCheckBox("Enable Email Notifications")
        layout.addWidget(self.email_checkbox)

        self.users_label = QLabel("List of Users:")
        layout.addWidget(self.users_label)

        dataset_path = "dataset"
        users = []

        for name in sorted(os.listdir(dataset_path)):
            name_path = os.path.join(dataset_path, name)
            if os.path.isdir(name_path):
                user = {
                    "name": name,
                    "image": None
                }
                images = os.listdir(name_path)
                if images:
                    image_path = os.path.join(name_path, images[0])
                    user["image"] = image_path
                users.append(user)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        name_label_width = 120
        name_label_tooltip_length = name_label_width - 20  # Adjust tooltip length if needed
        image_height = 96
        button_width = 120
        button_height = 48

        for user in users:
            user_layout = QHBoxLayout()

            name_label = QLabel(user["name"])
            name_label.setFixedWidth(name_label_width)
            name_label.setToolTip(user["name"] if len(user["name"]) > name_label_tooltip_length else "")
            font_metrics = name_label.fontMetrics()
            elided_text = font_metrics.elidedText(user["name"], Qt.ElideRight, name_label_tooltip_length)
            name_label.setText(elided_text)
            user_layout.addWidget(name_label)

            image_label = QLabel()
            if user["image"]:
                pixmap = QPixmap(user["image"]).scaledToHeight(image_height)
                image_label.setPixmap(pixmap)
            user_layout.addWidget(image_label)

            edit_button = IconPushButton("edit", "edit")
            edit_button.setFixedSize(button_width, button_height)
            edit_button.setLayoutDirection(Qt.LeftToRight)
            user_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
            user_layout.addWidget(edit_button)

            delete_button = IconPushButton("delete", "delete")
            delete_button.setFixedSize(button_width, button_height)
            delete_button.setLayoutDirection(Qt.LeftToRight)
            user_layout.addWidget(delete_button)

            scroll_layout.addLayout(user_layout)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        close_button_width = 80
        close_button = QPushButton("Close")
        close_button.setFixedWidth(close_button_width)
        close_button.clicked.connect(self.hide)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
