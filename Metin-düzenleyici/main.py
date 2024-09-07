import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMenu, QAction,
    QTabWidget, QMessageBox, QToolBar, QVBoxLayout, QLineEdit, QPushButton,
    QDialog, QStatusBar, QLabel, QWidget, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont, QTextCursor, QPainter, QColor
from PyQt5.QtCore import Qt, QFileInfo, QSize, QTimer

from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtCore import Qt, QRect


class SatirNumaralari(QWidget):
    def __init__(self, edit):
        super().__init__(edit)
        self.edit = edit
        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)
        self.edit.verticalScrollBar().valueChanged.connect(self.update)
        self.edit.textChanged.connect(self.update)
        self.font = QFont("Courier", 12)
        self.font.setBold(True)
        self.update()

    def eventFilter(self, obj, event):
        if event.type() == event.Paint and obj == self.edit.viewport():
            self.update()
        return super().eventFilter(obj, event)

    def update(self):
        self.updateGeometry()
        super().update()

    def sizeHint(self):
        return QSize(self.lineNumberAreaWidth(), 0)

    def lineNumberAreaWidth(self):
        digits = len(str(self.edit.document().blockCount()))
        return 30 + self.fontMetrics().width('9') * digits

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return

        self.edit.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.edit.document().begin()
        blockNumber = block.blockNumber()

        viewportOffset = self.edit.verticalScrollBar().value()

        top = int(self.edit.document().documentLayout().blockBoundingRect(block).top() - viewportOffset)
        bottom = int(top + self.edit.document().documentLayout().blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setFont(self.font)
                painter.setPen(Qt.black)
                rect = QRect(0, top, self.width(), self.fontMetrics().height())
                painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, number)
            block = block.next()
            top = bottom
            bottom = int(top + self.edit.document().documentLayout().blockBoundingRect(block).height())
            blockNumber += 1

        painter.end()

class BulVeDegistir(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Bul ve Değiştir')
        self.setGeometry(100, 100, 300, 150)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.bulEdit = QLineEdit(self)
        self.bulEdit.setPlaceholderText('Bul...')
        self.layout.addWidget(self.bulEdit)

        self.degistirEdit = QLineEdit(self)
        self.degistirEdit.setPlaceholderText('Değiştir...')
        self.layout.addWidget(self.degistirEdit)

        self.bulBtn = QPushButton('Bul', self)
        self.degistirBtn = QPushButton('Değiştir', self)

        self.bulBtn.clicked.connect(self.bul)
        self.degistirBtn.clicked.connect(self.degistir)

        self.layout.addWidget(self.bulBtn)
        self.layout.addWidget(self.degistirBtn)

        self.show()

    def bul(self):
        text = self.bulEdit.text()
        parent = self.parent()
        if parent:
            currentWidget = parent.tabWidget.currentWidget()
            if currentWidget:
                editor = currentWidget.findChild(QTextEdit)
                if editor:
                    cursor = editor.textCursor()
                    document = editor.document()
                    cursor = document.find(text, cursor)
                    if not cursor.isNull():
                        editor.setTextCursor(cursor)
                    else:
                        parent.statusBar.showMessage('   ')

    def degistir(self):
        text = self.bulEdit.text()
        replace_text = self.degistirEdit.text()
        parent = self.parent()
        if parent:
            currentWidget = parent.tabWidget.currentWidget()
            if currentWidget:
                editor = currentWidget.findChild(QTextEdit)
                if editor:
                    current_text = editor.toPlainText()
                    new_text = current_text.replace(text, replace_text)
                    editor.setPlainText(new_text)

class MetinEditoru(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Metin Editörü')
        self.setGeometry(100, 100, 1200, 800)
        self.degisti_mi = False
        self.initUI()

    def initUI(self):
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.kapatTab)
        self.tabWidget.setMovable(True)

        self.createMenuBar()
        self.createToolBar()
        self.createStatusBar()

        self.show()

    def createMenuBar(self):
        menubar = self.menuBar()

        dosyaMenu = menubar.addMenu('Dosya')

        yeniAction = QAction('Yeni', self)
        yeniAction.setShortcut('Ctrl+N')
        yeniAction.triggered.connect(self.yeniDosya)
        dosyaMenu.addAction(yeniAction)

        acAction = QAction('Aç', self)
        acAction.setShortcut('Ctrl+O')
        acAction.triggered.connect(self.acDosya)
        dosyaMenu.addAction(acAction)

        kaydetAction = QAction('Kaydet', self)
        kaydetAction.setShortcut('Ctrl+S')
        kaydetAction.triggered.connect(self.kaydetDosya)
        dosyaMenu.addAction(kaydetAction)

        kaydetFarkliAction = QAction('Farklı Kaydet', self)
        kaydetFarkliAction.triggered.connect(self.kaydetDosyaFarkli)
        dosyaMenu.addAction(kaydetFarkliAction)

        kapatAction = QAction('Çıkış', self)
        kapatAction.setShortcut('Ctrl+Q')
        kapatAction.triggered.connect(self.close)
        dosyaMenu.addAction(kapatAction)

        duzenMenu = menubar.addMenu('Düzen')

        geriAlAction = QAction('Geri Al', self)
        geriAlAction.setShortcut('Ctrl+Z')
        geriAlAction.triggered.connect(self.geriAl)
        geriAlAction.setDisabled(True)
        duzenMenu.addAction(geriAlAction)

        kesAction = QAction('Kes', self)
        kesAction.setShortcut('Ctrl+X')
        kesAction.triggered.connect(self.kes)
        kesAction.setDisabled(True)
        duzenMenu.addAction(kesAction)

        kopyalaAction = QAction('Kopyala', self)
        kopyalaAction.setShortcut('Ctrl+C')
        kopyalaAction.triggered.connect(self.kopyala)
        kopyalaAction.setDisabled(True)
        duzenMenu.addAction(kopyalaAction)

        yapistirAction = QAction('Yapıştır', self)
        yapistirAction.setShortcut('Ctrl+V')
        yapistirAction.triggered.connect(self.yapistir)
        yapistirAction.setDisabled(True)
        duzenMenu.addAction(yapistirAction)

        tumunuSecAction = QAction('Tümünü Seç', self)
        tumunuSecAction.setShortcut('Ctrl+A')
        tumunuSecAction.triggered.connect(self.tumunuSec)
        tumunuSecAction.setDisabled(True)
        duzenMenu.addAction(tumunuSecAction)

        for action in duzenMenu.actions():
            action.triggered.connect(lambda: None)

    def createToolBar(self):
        toolbar = QToolBar("Araçlar")
        self.addToolBar(toolbar)

        yeniBtn = QAction('Yeni Dosya', self)
        yeniBtn.triggered.connect(self.yeniDosya)
        toolbar.addAction(yeniBtn)

        acBtn = QAction('Dosya Aç', self)
        acBtn.triggered.connect(self.acDosya)
        toolbar.addAction(acBtn)

        kaydetBtn = QAction('Dosyayı Kaydet', self)
        kaydetBtn.triggered.connect(self.kaydetDosya)
        toolbar.addAction(kaydetBtn)

        kesBtn = QAction('Kes', self)
        kesBtn.triggered.connect(self.kes)
        toolbar.addAction(kesBtn)

        kopyalaBtn = QAction('Kopyala', self)
        kopyalaBtn.triggered.connect(self.kopyala)
        toolbar.addAction(kopyalaBtn)

        yapistirBtn = QAction('Yapıştır', self)
        yapistirBtn.triggered.connect(self.yapistir)
        toolbar.addAction(yapistirBtn)

        bulDegistirBtn = QAction('Bul ve Değiştir', self)
        bulDegistirBtn.triggered.connect(self.bulVeDegistir)
        toolbar.addAction(bulDegistirBtn)

    def createStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def yeniDosya(self):
        editor = QTextEdit()
        lineNumbers = SatirNumaralari(editor)
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.addWidget(lineNumbers)
        layout.addWidget(editor)
        frame.setLayout(layout)

        self.tabWidget.addTab(frame, 'Yeni Sekme')
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def acDosya(self):
        dosyaYolu, _ = QFileDialog.getOpenFileName(self, 'Dosya Aç', '', 'Metin Dosyaları (*.txt);;Tüm Dosyalar (*)')
        if dosyaYolu:
            editor = QTextEdit()
            lineNumbers = SatirNumaralari(editor)
            frame = QFrame()
            layout = QHBoxLayout(frame)
            layout.addWidget(lineNumbers)
            layout.addWidget(editor)
            frame.setLayout(layout)

            with open(dosyaYolu, 'r', encoding='utf-8') as file:
                cursor = QTextCursor(editor.document())
                cursor.movePosition(QTextCursor.Start)
                for line in file:
                    cursor.insertText(line)

            self.tabWidget.addTab(frame, QFileInfo(dosyaYolu).fileName())
            self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)


    def kaydetDosya(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            dosyaYolu, _ = QFileDialog.getSaveFileName(self, 'Dosya Kaydet', '', 'Metin Dosyaları (*.txt);;Tüm Dosyalar (*)')
            if dosyaYolu:
                with open(dosyaYolu, 'w', encoding='utf-8') as file:
                    file.write(editor.toPlainText())
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), QFileInfo(dosyaYolu).fileName())

    def kaydetDosyaFarkli(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            dosyaYolu, _ = QFileDialog.getSaveFileName(self, 'Farklı Kaydet', '', 'Metin Dosyaları (*.txt);;Tüm Dosyalar (*)')
            if dosyaYolu:
                with open(dosyaYolu, 'w', encoding='utf-8') as file:
                    file.write(editor.toPlainText())
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), QFileInfo(dosyaYolu).fileName())

    def kapatTab(self, index):
        if self.tabWidget.count() > 1:
            self.tabWidget.removeTab(index)
        else:
            self.close()

    def geriAl(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            if editor and editor.isUndoAvailable():
                editor.undo()

    def yenidenYap(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            if editor and editor.document().isRedoAvailable():
                editor.redo()

    def kes(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            if editor:
                cursor = editor.textCursor()
                if cursor.hasSelection():
                    editor.cut()

    def kopyala(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            if editor:
                cursor = editor.textCursor()
                if cursor.hasSelection():
                    editor.copy()

    def yapistir(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            if editor:
                editor.paste()

    def tumunuSec(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            editor = tab.findChild(QTextEdit)
            if editor:
                editor.selectAll()

    def bulVeDegistir(self):
        dialog = BulVeDegistir(self)
        dialog.exec_()

    def closeEvent(self, event):
        unsaved_files = []
        for index in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(index)
            editor = tab.findChild(QTextEdit)
            if editor and editor.document().isModified():
                unsaved_files.append(self.tabWidget.tabText(index))

        if unsaved_files:
            message = "Aşağıdaki dosyalar kaydedilmemiş:\n" + "\n".join(unsaved_files) + "\n\nProgramı kapatmadan önce kaydedilsin mi?"
            reply = QMessageBox.question(self, 'Kaydedilmemiş Dosyalar', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                for index in range(self.tabWidget.count()):
                    tab = self.tabWidget.widget(index)
                    editor = tab.findChild(QTextEdit)
                    if editor and editor.document().isModified():
                        dosyaYolu, _ = QFileDialog.getSaveFileName(self, 'Dosyayı Kaydet', '', 'Metin Dosyaları (*.txt);;Tüm Dosyalar (*)')
                        if dosyaYolu:
                            with open(dosyaYolu, 'w', encoding='utf-8') as file:
                                file.write(editor.toPlainText())
                                self.tabWidget.setTabText(index, QFileInfo(dosyaYolu).fileName())
                        else:
                            event.ignore()
                            return

        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = MetinEditoru()
    sys.exit(app.exec_())
