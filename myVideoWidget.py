from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import *

class myVideoWidget(QVideoWidget):
    doubleClickedItem = pyqtSignal(str)
    def __init__(self, parent=None):
        super(QVideoWidget, self).__init__(parent)

    def mouseDoubleClickEvent(self, QMouseEvent): # 定义双击触发
        self.doubleClickedItem.emit("double clicked")
