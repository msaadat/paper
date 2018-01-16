import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QKeySequence, QColor, QFont, QPixmap

from papers import PapersStore
from config import PaperConfig
from paper_editor import PaperEditor
from password_dlg import PasswordDialog


class PaperWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.config = PaperConfig()
        self.papers = PapersStore(self.config['Paper']['PapersPath'])
        self.locked = True

        self.initUI()

        self.toggleLock()

    def initUI(self):
        self.main_widget = QWidget()
        self.screen_stack = QStackedWidget(self)

        self.resize(self.config['Paper'].getint('Width'),
                    self.config['Paper'].getint('Height'))
        self.move(self.config['Paper'].getint('WindowX'),
                  self.config['Paper'].getint('WindowY'))

        self.setWindowTitle('Paper')
        self.setWindowIcon(QIcon('icons/paper.png'))

        # hack to set correct icon in windows taskbar
        if os.name == 'nt':
            import ctypes
            myappid = 'msaadat.paper'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)



        self.tab_bar = QTabWidget(self.screen_stack)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.tabCloseRequested.connect(self.delete_paper)
        self.tab_bar.tabBarDoubleClicked.connect(self.rename_paper)

        self.hboxContainer = QWidget(self)
        self.hboxCorner = QHBoxLayout(self.hboxContainer)

        self.tabButton = QToolButton(self.hboxContainer)
        self.tabButton.setText('➕')
        font = self.tabButton.font()
        font.setPointSize(font.pointSize() + 1)
        self.tabButton.setFont(font)
        self.tabButton.setAutoRaise(True)
        self.tabButton.clicked.connect(self.add_paper_handler)

        self.menuBtn = QToolButton(self.hboxContainer)
        self.menuBtn.setText('☰')
        self.menuBtn.setAutoRaise(True)
        font = self.menuBtn.font()
        font.setPointSize(font.pointSize() + 3)
        font.setBold(True)
        self.menuBtn.setFont(font)

        self.lock_action = QAction("Lock", self)
        # self.lock_action.setShortcuts(QKeySequence("Ctrl+L"))
        self.lock_action.triggered.connect(self.toggleLock)

        font_action = QAction("Font...", self)
        font_action.triggered.connect(self.getFont)

        self.menuBtnmenu = QMenu(self.menuBtn)
        self.menuBtnmenu.installEventFilter(self)

        self.menuBtnmenu.addAction(self.lock_action)
        self.menuBtnmenu.addAction(font_action)
        self.menuBtn.setMenu(self.menuBtnmenu)
        self.menuBtn.setPopupMode(QToolButton.InstantPopup)

        self.hboxCorner.addWidget(self.tabButton)
        self.hboxCorner.addWidget(self.menuBtn)
        self.hboxCorner.setContentsMargins(0, 0, 0, 0)
        self.hboxContainer.setLayout(self.hboxCorner)

        self.tab_bar.setCornerWidget(self.hboxContainer)

        self.unlock_pixmap = QPixmap()
        self.unlock_pixmap.load("icons/unlock.png")
        self.lock_screen = QLabel(self.screen_stack)
        self.lock_screen.setPixmap(self.unlock_pixmap)
        self.lock_screen.setAlignment(Qt.AlignCenter)
        self.lock_screen.installEventFilter(self)

        self.screen_stack.insertWidget(0, self.lock_screen)
        self.screen_stack.insertWidget(1, self.tab_bar)

        self.setCentralWidget(self.screen_stack)
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

                QToolButton::menu-indicator { image: none; }
                """)

        # main window shortcuts
        lock_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        lock_shortcut.activated.connect(self.toggleLock)

        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

        # editor shortcuts
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self.tab_bar)
        save_shortcut.activated.connect(self.save_paper)

        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self.tab_bar)
        new_shortcut.activated.connect(self.add_paper_handler)

        delete_shortcut = QShortcut(QKeySequence("Ctrl+W"), self.tab_bar)
        delete_shortcut.activated.connect(self.delete_paper_active)

        eval_shortcut = QShortcut(QKeySequence("Ctrl+E"), self.tab_bar)
        eval_shortcut.activated.connect(self.evalText)

        self.show()

    def toggleLock(self):
        if self.locked:
            if self.getPassword():
                self.loadPapers()
                self.screen_stack.setCurrentWidget(self.tab_bar)
                self.locked = False
        else:
            if self.closeEditors():
                self.screen_stack.setCurrentWidget(self.lock_screen)
                self.locked = True

    def getFont(self, event):
        prevfont = QFont()
        if "Font" in self.config['Paper']:
            prevfont.fromString(self.config['Paper']['Font'])

        font, ok = QFontDialog.getFont(prevfont, self)
        if ok:
            self.setFont(font)

    def setFont(self, font=None):
        if font is None:
            if "Font" in self.config['Paper']:
                font = QFont()
                font.fromString(self.config['Paper']['Font'])

        if font is not None:
            self.config['Paper']['Font'] = font.toString()
            for i in range(self.tab_bar.count()):
                editor = self.tab_bar.widget(i)
                editor.setFont(font)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show and obj == self.menuBtnmenu:
            # show menu to the right instead of left
            pos = obj.pos()
            geo = self.menuBtn.geometry()
            obj.move(pos.x() + geo.width() - obj.geometry().width(), pos.y())
            return True
        elif event.type() == QEvent.MouseButtonPress and obj == self.lock_screen:
            self.toggleLock()
        return False

    def loadPapers(self):
        try:
            self.papers.loadPapers()
        except ValueError as e:
            QMessageBox.warning(self, "Error",
                                e.args[0])
            return

        if not self.papers:
            self.papers.addPaper("note")
            self.papers["note"].text = "##My note"

        for i in self.papers:
            self.add_paper(self.papers[i].name)

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

        self.setFont()

    def getPassword(self):
        if not self.papers.pw_check_path.exists():
            pwd, response = PasswordDialog.getPassword(self)
            if response == QDialog.Accepted and pwd != '':
                self.papers.changePassword(pwd)
                return True
            else:
                return False
        else:
            pwd, response = QInputDialog.getText(self, "Password",
                                              "Input pasword:",
                                                      QLineEdit.Password, "")
            if response == QDialog.Accepted and pwd != '':
                if self.papers.setPassword(pwd):
                    return True
                else:
                    QMessageBox.warning(self, "Error", "Invalid Password")
                    return False
            else:
                return False

    def evalText(self):
        editor = self.tab_bar.currentWidget()
        cursor = editor.textCursor()
        result = None
        if cursor.hasSelection():
            text = cursor.selectedText()
            try:
                result = eval(text)
            except:
                pass
            if result is not None:
                cursor.removeSelectedText()
                cursor.insertText(str(result))
        editor.setTextCursor(cursor)

    def closeEditors(self):
        # check for unsaved papers
        unsaved = []
        for i in range(self.tab_bar.count()):
            editor = self.tab_bar.widget(i)
            name = self.tab_bar.tabText(i)
            if editor.dirty:
                unsaved.append((name, editor))

        if unsaved:
            reply = QMessageBox.question(self, "Unsaved Papers",
                                         "Papers contain unsaved changes. Save all before closing?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                for i, j in unsaved:
                    self.papers[i].text = j.toPlainText()
                    self.papers.savePaper(i)
            if reply == QMessageBox.Cancel:
                return False

        # save last paper & cursor pos
        widget = self.tab_bar.currentWidget()
        if widget is not None:
            pos = self.tab_bar.currentWidget().textCursor().position()
            self.config['Paper']['LastCursorPos'] = str(pos)
            self.config['Paper']['LastPaper'] = self.tab_bar.tabText(self.tab_bar.currentIndex())

        # save position
        self.config['Paper']['Width'] = str(self.width())
        self.config['Paper']['Height'] = str(self.height())
        self.config['Paper']['WindowX'] = str(self.pos().x())
        self.config['Paper']['WindowY'] = str(self.pos().y())

        self.config.SaveConfig()

        # reset papers and remove all tabs
        self.papers = PapersStore(self.config['Paper']['PapersPath'])
        for i in range(self.tab_bar.count()):
            self.tab_bar.removeTab(0)

        return True

    def closeEvent(self, event):
        if self.closeEditors():
            event.accept()
            sys.exit()

    def add_paper_handler(self):
        name, okPressed = QInputDialog.getText(self, "New Paper",
                                               "Paper name:", QLineEdit.Normal,
                                               "")
        if okPressed and name != '':
            if self.papers.addPaper(name):
                self.add_paper(name)
            else:
                QMessageBox.information(self, name, "Paper already exists.")

    def add_paper(self, name):
        editor = PaperEditor()
        editor.setText(self.papers[name].text)
        index = self.tab_bar.addTab(editor, name)
        self.tab_bar.setCurrentIndex(index)
        editor.textChanged.connect(self.set_dirty)

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
            self.papers.deletePaper(name)
            self.tab_bar.removeTab(index)

    def save_paper(self):
        textbox = self.tab_bar.currentWidget()
        index = self.tab_bar.currentIndex()
        name = self.tab_bar.tabText(index)
        self.papers[name].text = textbox.toPlainText()
        self.papers.savePaper(name)
        textbox.setDirty(False)
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
            if self.papers.renamePaper(name, rename):
                self.tab_bar.setTabText(index, rename)
            else:
                QMessageBox.information(self, rename, "Paper already exists.")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    p = PaperWindow()
    sys.exit(app.exec_())
