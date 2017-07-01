from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit


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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.indentSelection()
        elif event.key() == Qt.Key_Backtab:
            self.indentSelection(False)
        else:
            super().keyPressEvent(event)

    def indentSelection(self, indent=True):
        cursor = self.textCursor()
        selection = cursor.selectedText()

        if selection != '':
            linesep = '\u2029'    # qt line ending
            lines = selection.split(linesep)

            if indent:
                newtext = linesep.join(['\t' + i for i in lines])
            else:
                newtext = linesep.join([i.replace('\t', '', 1) for i in lines])

            cursor.insertText(newtext)
            pos = cursor.position()
            cursor.setPosition(pos - len(newtext), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
