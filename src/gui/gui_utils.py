# gui_utils.py

from PyQt5.QtWidgets import QMessageBox

def show_error_message(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Error")
    msg.setText(message)
    msg.exec_()


