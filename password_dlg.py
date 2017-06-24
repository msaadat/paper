
from PyQt5.QtWidgets import (QApplication, QMessageBox, QDialog, QGridLayout,
                             QHBoxLayout, QLabel, QPushButton, QLineEdit)


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super(PasswordDialog, self).__init__(parent)

        self.password = None

        okButton = QPushButton("&Ok")
        okButton.clicked.connect(self.ok_pressed)

        self.pass1_edit = QLineEdit()
        self.pass1_edit.setEchoMode(QLineEdit.Password)
        self.pass2_edit = QLineEdit()
        self.pass2_edit.setEchoMode(QLineEdit.Password)

        lable1 = QLabel("Password:")
        lable2 = QLabel("Repeat password:")

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(okButton)

        mainLayout = QGridLayout()
        mainLayout.addWidget(lable1, 0, 0)
        mainLayout.addWidget(self.pass1_edit, 0, 1)
        mainLayout.addWidget(lable2, 1, 0)
        mainLayout.addWidget(self.pass2_edit, 1, 1)
        mainLayout.addLayout(buttonsLayout, 2, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Set Password")

    def ok_pressed(self):
        pass1 = self.pass1_edit.text()
        pass2 = self.pass2_edit.text()

        if pass1 != pass2:
            QMessageBox.warning(self, "Password",
                                    "Passwords do not match.")
            self.pass1_edit.setFocus()
            self.pass1_edit.selectAll()
        elif pass1 == '':
            QMessageBox.information(self, "Password",
                                    "Passwords cannot be empty.")
            self.pass1_edit.setFocus()
            self.pass1_edit.selectAll()
        else:
            self.password = pass1
            self.accept()

    @staticmethod
    def getPassword(parent):
        dialog = PasswordDialog(parent)
        result = dialog.exec_()
        return dialog.password, result


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = PasswordDialog()
    window.show()
    sys.exit(app.exec_())
