import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from src.gui.app_gui import EmailSaverApp
from src.utils.helpers import resource_path

import sys
import traceback


def show_main():
    global window  # Keeps window from being garbage collected
    window = EmailSaverApp()
    window.setWindowIcon(QIcon(resource_path("resources/icon.ico")))
    window.setWindowTitle("Imap2Eml")
    window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = QSplashScreen(QPixmap(resource_path("resources/logo.png")), Qt.WindowStaysOnTopHint)
    splash.setEnabled(False)
    splash.show()
    QTimer.singleShot(2000, lambda: (splash.close(), show_main()))

    sys.exit(app.exec_())

def log_exceptions():
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)

try:
    # your existing code here
    #from src.gui.gui_utils import launch_app
    show_main()
except Exception:
    log_exceptions()


#  Keep window reference alive
window = None
