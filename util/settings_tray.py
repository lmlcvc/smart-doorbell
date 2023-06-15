from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout, QScrollArea, QWidget
from PyQt5.QtGui import QPixmap

from widgets.IconPushButton import IconPushButton


class SettingsTray(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        self.email_checkbox = QCheckBox("Enable Email Notifications")
        layout.addWidget(self.email_checkbox)

        self.users_label = QLabel("List of Users:")
        layout.addWidget(self.users_label)

        users = [
            {
                "name": "Charles Leclerc",
                "image": "images/ignore.png"
            },
            {
                "name": "Sebastian Vettel",
                "image": "images/ignore.png"
            },
            {
                "name": "Pierre Gasly",
                "image": "images/ignore.png"
            },
            {
                "name": "Fernando Alonso",
                "image": "images/ignore.png"
            },
            {
                "name": "Daniel Ricciardo",
                "image": "images/ignore.png"
            },
            {
                "name": "Max Verstappen",
                "image": "images/ignore.png"
            },
            {
                "name": "Lewis Hamilton",
                "image": "images/ignore.png"
            },
            {
                "name": "Lando Norris",
                "image": "images/ignore.png"
            },
            {
                "name": "Carlos Sainz",
                "image": "images/ignore.png"
            },
            {
                "name": "Esteban Ocon",
                "image": "images/ignore.png"
            },
            {
                "name": "Yuki Tsunoda",
                "image": "images/ignore.png"
            }
        ]

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for user in users:
            user_layout = QHBoxLayout()

            name_label = QLabel(user["name"])
            user_layout.addWidget(name_label)

            image_label = QLabel()
            pixmap = QPixmap(user["image"]).scaledToWidth(36)
            image_label.setPixmap(pixmap)
            user_layout.addWidget(image_label)

            edit_button = IconPushButton("edit", "edit")
            user_layout.addWidget(edit_button)

            delete_button = IconPushButton("delete", "delete")
            user_layout.addWidget(delete_button)

            scroll_layout.addLayout(user_layout)

        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area)

        button = QPushButton("Close")
        button.clicked.connect(self.hide)
        layout.addWidget(button)

        self.setLayout(layout)
