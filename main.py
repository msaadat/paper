from papers import Papers

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QKeySequence, QTextCursor, QColor

class PaperEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.dirty = False
        # self.textChanged.connect(self.setDirty)
    
    def setDirty(self, status=True):
        self.dirty = status

class PaperWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self): 
        self.main_widget = QWidget()
        self.vbox = QVBoxLayout()

        self.resize(550, 350)
        self.move(300, 300)
        self.setWindowTitle('Paper')
        self.setWindowIcon(QIcon('paper.png'))

        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_paper)

        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.add_paper)

        delete_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        delete_shortcut.activated.connect(self.delete_paper_active)

        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.quit)
        

        self.papers = Papers()

        self.tab_bar = QTabWidget()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.tabCloseRequested.connect(self.delete_paper)
        self.tab_bar.tabBarDoubleClicked.connect(self.rename_paper)

        for i in self.papers:
            editor = PaperEditor()
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
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.CustomizeWindowHint)
        self.show()

        current = self.tab_bar.currentWidget()
        current.setFocus()
        current.moveCursor(QTextCursor.End)

    def quit(self):
        sys.exit()

    def add_paper(self):
        name, okPressed = QInputDialog.getText(self, "New Paper","Paper name:", QLineEdit.Normal, "")
        if okPressed and name != '':
            if not self.papers.paper_exists(name):
                editor = PaperEditor()
                self.papers.add_paper(name)
                index = self.tab_bar.addTab(editor, name)
                self.tab_bar.setCurrentIndex(index)
            else:
                reply = QMessageBox.information(self, name, "Paper already exists.")

    def delete_paper_active(self):
        index = self.tab_bar.currentIndex()
        self.delete_paper(index)

    def delete_paper(self, index):
        name = self.tab_bar.tabText(index)
        reply = QMessageBox.question(self, "Delete Paper","Are you sure to delete paper " + name, QMessageBox.Yes | 
                                     QMessageBox.No, QMessageBox.No)
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
        rename, okPressed = QInputDialog.getText(self, "Rename Paper","Paper name:", QLineEdit.Normal, "")
        if okPressed and rename != '':
            if not self.papers.paper_exists(rename):
                self.papers.rename_paper(name, rename)
                self.tab_bar.setTabText(index, rename)
            else:
                reply = QMessageBox.information(self, rename, "Paper already exists.")

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    p = PaperWindow()
    sys.exit(app.exec_())