# app_gui.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QCheckBox
)
from PyQt5.QtCore import QThread, QObject, pyqtSignal, Qt,QSize
from src.utils.email_utils import connect_to_mailbox, get_email_metadata
from src.config import DOWNLOAD_FOLDER
from src.utils.helpers import resource_path
from src.gui.settings_dialog import SettingsDialog
from src.utils.settings_handler import load_settings
from src.gui.spinner_widget import Spinner
from PyQt5.QtGui import QIcon
from src.utils.eml_saver import save_eml
from src.utils.email_filters import build_search_query


class EmailFetchWorker(QObject):
    finished = pyqtSignal(object, str)
    error = pyqtSignal(str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def run(self):
        try:
            mail = connect_to_mailbox(
                self.settings["email"],
                self.settings["password"],
                self.settings["server"]
            )

            mail.select("INBOX")

            # Use dynamic search query
            search_criteria = build_search_query(
                days=int(self.settings["days"]),
                target_email=self.settings.get("target_email"),
                from_email=self.settings.get("from_email"),
                unread_only=self.settings.get("unread_only", False)
            )

            result, data = mail.search(None, search_criteria)

            ids = data[0].split() if result == "OK" else []
            email_data = get_email_metadata(mail, ids)

            mail.logout()
            self.finished.emit(email_data, f"Fetched {len(email_data)} emails.")
        except Exception as e:
            self.error.emit(str(e))


class EmailSaverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imap2Eml")
        self.setMinimumSize(1024, 800)

        main_layout = QVBoxLayout(self)


        #  Buttons in horizontal layout
        self.settings_button = QPushButton(" Settings")
        self.fetch_button = QPushButton(" Fetch Emails")
        self.save_button = QPushButton(" Save Selected Emails")

        self.icon_fetch = QIcon(resource_path('resources/icons/move_to_inbox_icon.svg'))
        self.icon_save = QIcon(resource_path('resources/icons/archive_icon.svg'))
        self.icon_settings = QIcon(resource_path('resources/icons/settings_icon.svg'))
        self.fetch_button.setIcon(self.icon_fetch)
        self.fetch_button.setIconSize(QSize(32, 32))
        self.settings_button.setIcon(self.icon_settings)
        self.settings_button.setIconSize(QSize(32, 32))
        self.save_button.setIcon(self.icon_save)
        self.save_button.setIconSize(QSize(32, 32))

        self.settings_button.clicked.connect(self.open_settings)
        self.fetch_button.clicked.connect(self.load_emails)
        self.save_button.clicked.connect(self.save_selected_emails)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.fetch_button)
        button_layout.addWidget(self.save_button)
        button_layout.setSpacing(12)
        main_layout.addLayout(button_layout)

        # Select All
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        main_layout.addWidget(self.select_all_checkbox)

        #  Email list
        self.email_list_widget = QListWidget()
        main_layout.addWidget(self.email_list_widget, stretch=1)
        self.email_list_widget.itemClicked.connect(self.show_preview)

        #preview pane
        self.preview_label = QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignTop)
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setTextFormat(Qt.RichText)
        main_layout.addWidget(self.preview_label)

        #  Spinner + status at bottom
        self.spinner = Spinner()
        self.spinner.setVisible(False)
        self.status_label = QLabel("")
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.spinner)
        status_layout.addWidget(self.status_label)
        status_layout.setSpacing(8)
        main_layout.addStretch()
        main_layout.addLayout(status_layout)

        #  Styling
        with open(resource_path("src/gui/style.qss"), "r") as f:
            self.setStyleSheet(f.read())

    def open_settings(self):
        SettingsDialog(self).exec_()

    def load_emails(self):
        settings = load_settings()
        if not settings:
            QMessageBox.warning(self, "Missing Info", "Please configure your settings first.")
            return

        #  Disable buttons during fetch
        for btn in [self.settings_button, self.fetch_button, self.save_button]:
            btn.setEnabled(False)

        self.spinner.show()
        self.status_label.setText(" Fetching emails...")

        self.thread = QThread()
        self.worker = EmailFetchWorker(settings)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_emails_fetched)
        self.worker.error.connect(self.on_email_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_emails_fetched(self, email_data, message):
        self.email_data = email_data
        self.status_label.setText(message)
        self.spinner.hide()

        self.email_list_widget.clear()
        for email in email_data:
            item = QListWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setCheckState(Qt.Unchecked)
            self.icon_mail = QIcon(resource_path('resources/icons/mail_icon.svg'))
            subject = email.get("subject") or "(No Subject)"
            item.setIcon(self.icon_mail)
            item.setText(f"{subject} | From: {email['from']}")
            item.setData(Qt.UserRole, email)
            self.email_list_widget.addItem(item)

        #  Re-enable buttons after fetch
        for btn in [self.settings_button, self.fetch_button, self.save_button]:
            btn.setEnabled(True)
        self.select_all_checkbox.setCheckState(Qt.Unchecked)

    def on_email_error(self, error_message):
        self.status_label.setText("")
        QMessageBox.critical(self, "Error", error_message)
        self.spinner.hide()

        #  Re-enable buttons even on error
        for btn in [self.settings_button, self.fetch_button, self.save_button]:
            btn.setEnabled(True)

    def save_selected_emails(self):
        saved = 0
        for i in range(self.email_list_widget.count()):
            item = self.email_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                email_obj = item.data(Qt.UserRole)
                if save_eml(email_obj, DOWNLOAD_FOLDER):
                    saved += 1
        QMessageBox.information(self, "Saved", f"{saved} emails saved to '{DOWNLOAD_FOLDER}'.")

    def show_preview(self, item):
        email_obj = item.data(Qt.UserRole)
        sender = email_obj.get("from", "(Unknown Sender)")
        subject = email_obj.get("subject", "(No Subject)")
        preview = email_obj.get("preview", "")

        self.preview_label.setText(
            f"<b>From:</b> {sender}<br>"
            f"<b>Subject:</b> {subject}<br><br>"
            f"{preview}"
        )

    def toggle_select_all(self, state):
        check = Qt.Checked if state == Qt.Checked else Qt.Unchecked
        for i in range(self.email_list_widget.count()):
            item = self.email_list_widget.item(i)
            item.setCheckState(check)


