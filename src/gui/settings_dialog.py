#settings_dialog
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QCheckBox

from src.gui.gui_utils import show_error_message
from src.utils.helpers import resource_path

import json
import os



SETTINGS_FILE = resource_path("settings.dat")
FERNET_KEY_FILE = resource_path("key.key")

def get_fernet():
    if not os.path.exists(FERNET_KEY_FILE):
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(Fernet.generate_key())
    with open(FERNET_KEY_FILE, "rb") as f:
        key = f.read()
    return Fernet(key)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout()

        # Inputs
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("App Password")
        layout.addWidget(self.password_input)

        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("IMAP server (e.g., imap.yandex.com)")
        layout.addWidget(self.server_input)

        self.target_email_input = QLineEdit()
        self.target_email_input.setPlaceholderText("Target email")
        layout.addWidget(self.target_email_input)

        self.from_email_input = QLineEdit()
        self.from_email_input.setPlaceholderText("From email")
        layout.addWidget(self.from_email_input)

        self.unread_only_checkbox = QCheckBox("Show Only Unread Emails")
        layout.addWidget(self.unread_only_checkbox)

        self.days_input = QLineEdit()
        self.days_input.setPlaceholderText("Number of days to fetch")
        layout.addWidget(self.days_input)

        self.icon_save = QIcon(resource_path('resources/icons/save_icon.svg'))
        save_btn = QPushButton("Save Settings")
        save_btn.setIcon(self.icon_save)
        save_btn.setIconSize(QSize(32, 32))

        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)
        self.load_settings()

    def save_settings(self):
        data = {
            "email": self.email_input.text(),
            "password": self.password_input.text(),
            "server": self.server_input.text(),
            "target_email": self.target_email_input.text(),
            "from_email": self.from_email_input.text(),
            "unread_only": self.unread_only_checkbox.isChecked(),
            "days": self.days_input.text()

        }
        fernet = get_fernet()
        encrypted = fernet.encrypt(json.dumps(data).encode())
        with open(SETTINGS_FILE, "wb") as f:
            f.write(encrypted)
        self.accept()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            fernet = get_fernet()
            with open(SETTINGS_FILE, "rb") as f:
                encrypted = f.read()
                try:
                    decrypted = fernet.decrypt(encrypted).decode()
                    data = json.loads(decrypted)
                    self.email_input.setText(data.get("email", ""))
                    self.password_input.setText(data.get("password", ""))
                    self.server_input.setText(data.get("server", ""))
                    self.target_email_input.setText(data.get("target_email", ""))
                    self.from_email_input.setText(data.get("from_email", ""))
                    self.unread_only_checkbox.setChecked(data.get("unread_only", False))
                    self.days_input.setText(str(data.get("days", "")))
                except Exception:
                    show_error_message(
                        "Settings could not be decrypted.\nPlease ensure your encryption key is correct and the file isn't corrupted."
                    )

