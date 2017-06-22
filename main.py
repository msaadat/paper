import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QKeySequence, QTextCursor, QColor

from papers import Papers
from config import PaperConfig


class PaperEditor(QTextEdit):
    def __init__(self, config):
        super().__init__()
        self.dirty = False
        if "FontFamily" in config['Paper']:
            font = config['Paper']['FontFamily']
            self.setFontFamily(font)

        if "FontSize" in config['Paper']:
            size = config['Paper']['FontSize']
            self.setFontPointSize(int(size))

    def setDirty(self, status=True):
        self.dirty = status


class PaperWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.config = PaperConfig()
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget()
        self.vbox = QVBoxLayout()

        self.resize(self.config['Paper'].getint('Width'),
                    self.config['Paper'].getint('Height'))
        self.move(self.config['Paper'].getint('WindowX'),
                  self.config['Paper'].getint('WindowY'))
        self.setWindowTitle('Paper')
        self.setWindowIcon(QIcon('paper.png'))

        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_paper)

        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.add_paper)

        delete_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        delete_shortcut.activated.connect(self.delete_paper_active)

        eval_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        eval_shortcut.activated.connect(self.evalText)

        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

        self.papers = Papers(self.config['Paper']['PapersPath'])

        self.tab_bar = QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.tabCloseRequested.connect(self.delete_paper)
        self.tab_bar.tabBarDoubleClicked.connect(self.rename_paper)

        for i in self.papers:
            editor = PaperEditor(self.config)
            editor.setText(self.papers[i].text)
            editor.textChanged.connect(self.set_dirty)
            self.tab_bar.addTab(editor, i)

        self.tabButton = QToolButton(self)
        self.tabButton.setText('+')
        font = self.tabButton.font()
        font.setBold(True)
        self.tabButton.setFont(font)
        self.tab_bar.setCornerWidget(self.tabButton)
        self.tabButton.clicked.connect(self.add_paper)

        self.setCentralWidget(self.tab_bar)
        self.setStyleSheet("""
                QTabBar::tab {
                    padding: 3px;
                    background-color: #cccccc;
                    border-color: #9B9B9B;
                    border: 1px solid #C4C4C3;
                    border-bottom-color: #C2C7CB;
                }
                QTabBar::tab:selected {
                    background-color: #eeeeee;
                    border-color: #9B9B9B;
                    border-bottom-color: #C2C7CB;
                }

                """)
        self.show()

        # activate last used paper
        if "LastPaper" in self.config['Paper']:
            last_paper = self.config['Paper']['LastPaper']
            for i in range(0, self.tab_bar.count()):
                if self.tab_bar.tabText(i) == last_paper:
                    self.tab_bar.setCurrentIndex(i)
                    break

        current = self.tab_bar.currentWidget()
        current.setFocus()

        if "LastCursorPos" in self.config['Paper']:
            last_pos = self.config['Paper'].getint('LastCursorPos')
            cursor = self.tab_bar.currentWidget().textCursor()
            cursor.setPosition(last_pos)
            self.tab_bar.currentWidget().setTextCursor(cursor)

    def evalText(self):
        editor = self.tab_bar.currentWidget()
        cursor = editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            result = eval(text)
            cursor.removeSelectedText()
            cursor.insertText(str(result))
        editor.setTextCursor(cursor)

    def closeEvent(self, event):
        pos = self.tab_bar.currentWidget().textCursor().position()
        self.config['Paper']['LastCursorPos'] = str(pos)
        self.config['Paper']['LastPaper'] = self.tab_bar.tabText(self.tab_bar.currentIndex())

        # save position
        self.config['Paper']['Width'] = str(self.width())
        self.config['Paper']['Height'] = str(self.height())
        self.config['Paper']['WindowX'] = str(self.pos().x())
        self.config['Paper']['WindowY'] = str(self.pos().y())

        self.config.SaveConfig()
        event.accept()

    def add_paper(self):
        name, okPressed = QInputDialog.getText(self, "New Paper",
                                               "Paper name:", QLineEdit.Normal,
                                               "")
        if okPressed and name != '':
            if not self.papers.paper_exists(name):
                editor = PaperEditor()
                self.papers.add_paper(name)
                index = self.tab_bar.addTab(editor, name)
                self.tab_bar.setCurrentIndex(index)
            else:
                QMessageBox.information(self, name, "Paper already exists.")

    def delete_paper_active(self):
        index = self.tab_bar.currentIndex()
        self.delete_paper(index)

    def delete_paper(self, index):
        name = self.tab_bar.tabText(index)
        reply = QMessageBox.question(self, "Delete Paper",
                                     "Are you sure to delete paper " + name,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.papers.delete_paper(name)
            self.tab_bar.removeTab(index)

    def save_paper(self):
        textbox = self.tab_bar.currentWidget()
        index = self.tab_bar.currentIndex()
        name = self.tab_bar.tabText(index)
        self.papers[name].text = textbox.toPlainText()
        self.papers.save_paper(name)
        self.set_dirty(False)

    def set_dirty(self, status=True):
        textbox = self.tab_bar.currentWidget()
        textbox.setDirty(status)
        index = self.tab_bar.currentIndex()
        if status:
            self.tab_bar.tabBar().setTabTextColor(index, QColor("#aaaaaa"))
        else:
            self.tab_bar.tabBar().setTabTextColor(index, QColor())

    def rename_paper(self, index):
        name = self.tab_bar.tabText(index)
        rename, okPressed = QInputDialog.getText(self, "Rename Paper",
                                                 "Paper name:",
                                                 QLineEdit.Normal, "")
        if okPressed and rename != '':
            if not self.papers.paper_exists(rename):
                self.papers.rename_paper(name, rename)
                self.tab_bar.setTabText(index, rename)
            else:
                QMessageBox.information(self, rename, "Paper already exists.")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    p = PaperWindow()
    sys.exit(app.exec_())
