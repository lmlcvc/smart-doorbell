import os.path

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon


class IconPushButton(QPushButton):
    def __init__(self, text, icon_name, icon_dim=48, parent=None):
        super().__init__(parent)
        self.initUI(text, icon_name, icon_dim)

    def initUI(self, text, icon_name, icon_dim):
        layout = QVBoxLayout()
        self.setLayout(layout)

        button = QPushButton(text.upper())
        button.setIcon(QIcon(os.path.join("images", f"{icon_name}.png")))
        self.setIconSize(QSize(icon_dim, icon_dim))

        # Set the button style sheet to place the icon on the left side and text on the right
        button.setStyleSheet(
            "QPushButton { border: none; text-align: left; padding-left: %dpx; }"
            "QPushButton::icon { margin-right: 8px; }" % (button.iconSize().width() + 8)
        )

        layout.addWidget(button)
