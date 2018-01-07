import re
import webbrowser

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QTextCursor, QSyntaxHighlighter, QTextCharFormat, QFont, QBrush
from PyQt5.QtWidgets import QTextEdit

regex = {
'heading':'^(#+)\\s*(.+?)$',
'italic':'\\B\\*{1}(.+?)\\*{1}\\B',
'bold':'\\B\\*{2}(.+?)\\*{2}\\B',
'strike': '\B\~{2}(.+?)\~{2}\B',
'empty_list':'^\\s*[+\\-\\*]\\s*$',
'list':'^(\\s*)([+\\-\\*])(\\s?)',
'url':'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
}

class MarkdownHighlighter(QSyntaxHighlighter):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initRules()

    def initRules(self):
        self.highlightingRules = []
        headingFormat = QTextCharFormat()
        defaultSize = self.parent().defaultFont().pointSize()
        headingFormat.setFontPointSize(defaultSize * 1.3)
        headingFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append((regex['heading'], headingFormat))

        italicFormat = QTextCharFormat()
        italicFormat.setFontItalic(True)
        self.highlightingRules.append((regex['italic'], italicFormat))

        boldFormat = QTextCharFormat()
        boldFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append((regex['bold'], boldFormat))

        strikeFormat = QTextCharFormat()
        strikeFormat.setFontStrikeOut(True)
        self.highlightingRules.append((regex['strike'], strikeFormat))

        urlFormat = QTextCharFormat()
        urlFormat.setFontUnderline(True)
        urlFormat.setForeground(QBrush(Qt.blue))
        self.highlightingRules.append((regex['url'], urlFormat))

        self.rehighlight()

    def highlightBlock(self, text):
        for pattern, frmt in self.highlightingRules:
            m = re.search(pattern, text)
            if m:
                self.setFormat(m.start(), m.end(), frmt)


class PaperEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptRichText(False)
        self.dirty = False
        self.highlighter = MarkdownHighlighter(self.document())
        self.tabChar = 4 * ' '
        self.installEventFilter(self)
        self.viewport().installEventFilter(self)

    def setFont(self, font):
        super().setFont(font)

        # block signals as highlighter somehow sends textChanged signal
        self.blockSignals(True)
        self.highlighter.initRules()
        self.blockSignals(False)

    def setDirty(self, status=True):
        self.dirty = status

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and \
        event.button() == Qt.LeftButton and \
        event.modifiers() & Qt.ControlModifier:
            self.handle_linkOpen(event)
        return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab or event.key() == Qt.Key_Backtab:
            self.handle_indentSelection(event)
        elif event.key() == Qt.Key_Return:
            self.handle_Return(event)
        elif event.key() == Qt.Key_Backspace:
            self.handle_Backspace(event)
        else:
            super().keyPressEvent(event)

    def handle_indentSelection(self, event):
        modifiers = event.modifiers()

        if not modifiers & Qt.ControlModifier:
            cursor = self.textCursor()
            selection = cursor.selectedText()
            indent = event.key() == Qt.Key_Tab

            if selection != '':
                linesep = '\u2029'    # qt line ending
                lines = selection.split(linesep)

                if indent:
                    newtext = linesep.join([self.tabChar + i for i in lines])
                else:
                    newtext = linesep.join([i.replace(self.tabChar, '', 1) for i in lines])

                cursor.insertText(newtext)
                pos = cursor.position()
                cursor.setPosition(pos - len(newtext), QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
            else:
                cursor.insertText(self.tabChar)
        else:
            super().keyPressEvent(event)

    def handle_Return(self, event):
        cursor = self.textCursor()
        pos = cursor.position()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        line = cursor.selectedText()

        # delete empty list
        m = re.match(regex['empty_list'], line)
        if m:
            cursor.removeSelectedText()
            return

        # continue list
        m = re.match(regex['list'], line)
        if m:
            mstr = '\n' + line[m.start():m.end()]
            cursor.setPosition(pos)
            cursor.insertText(mstr)
        else:
            super().keyPressEvent(event)

    def handle_Backspace(self, event):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            tblen = len(self.tabChar)
            pos = cursor.position()
            cursor.setPosition(pos - tblen, QTextCursor.KeepAnchor)
            txt = cursor.selectedText()
            if txt == self.tabChar:
                cursor.removeSelectedText()
            else:
                cursor.setPosition(pos)
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def handle_linkOpen(self, event):
        cursor = self.textCursor()
        pos = cursor.position()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        m = re.match(regex['url'], text)
        if m:
            webbrowser.open(m.group(0))


