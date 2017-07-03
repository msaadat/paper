import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QSyntaxHighlighter, QTextCharFormat, QFont
from PyQt5.QtWidgets import QTextEdit


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlightingRules = []

        headingFormat = QTextCharFormat()
        defaultSize = parent.defaultFont().pointSize()
        headingFormat.setFontPointSize(defaultSize * 1.3)
        headingFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append(("^(#+)\\s*(.+?)$", headingFormat))

        italicFormat = QTextCharFormat()
        italicFormat.setFontItalic(True)
        self.highlightingRules.append(("\\B\\*{1}(.+?)\\*{1}\\B", italicFormat))

        boldFormat = QTextCharFormat()
        boldFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append(("\\B\\*{2}(.+?)\\*{2}\\B", boldFormat))

        strikeFormat = QTextCharFormat()
        strikeFormat.setFontStrikeOut(True)
        self.highlightingRules.append(("\B\~{2}(.+?)\~{2}\B", strikeFormat))

    def highlightBlock(self, text):
        for pattern, frmt in self.highlightingRules:
            m = re.search(pattern, text)
            if m:
                self.setFormat(m.start(), m.end(), frmt)


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

        self.document().setDefaultFont(self.currentFont())
        self.highlighter = MarkdownHighlighter(self.document())

    def setDirty(self, status=True):
        self.dirty = status

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab or event.key() == Qt.Key_Backtab:
            self.handle_indentSelection(event)
        if event.key() == Qt.Key_Return:
            self.handle_Return(event)
        else:
            super().keyPressEvent(event)

    def handle_indentSelection(self, event):
        cursor = self.textCursor()
        selection = cursor.selectedText()
        indent = event.key() == Qt.Key_Tab
        modifiers = event.modifiers()

        if (selection != '') and (modifiers != Qt.ControlModifier):
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
        else:
            super().keyPressEvent(event)

    def handle_Return(self, event):
        cursor = self.textCursor()
        pos = cursor.position()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        line = cursor.selectedText()

        # delete empty list
        m = re.match("^\\s*[+\\-\\*]\\s*$", line)
        if m:
            cursor.removeSelectedText()
            return

        # continue list
        m = re.match("^(\\s*)([+\\-\\*])(\\s?)", line)
        if m:
            mstr = '\n' + line[m.start():m.end()]
            cursor.setPosition(pos)
            cursor.insertText(mstr)
        else:
            super().keyPressEvent(event)
