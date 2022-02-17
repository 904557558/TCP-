from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from GUI_client import Ui_MainWindow
from myVideoWidget import myVideoWidget
import sys, socket

class myMainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.connect_btn.clicked.connect(self.connect)
        self.break_btn.clicked.connect(self.break_off)
        self.load_btn.clicked.connect(self.load_file)
        self.play_btn.clicked.connect(self.play_video)
        self.push_btn.clicked.connect(self.push_video)
        self.stop_btn.clicked.connect(self.stop_video)

    def connect(self):
        self.HOST = str(self.ip_edit.text())
        self.PORT = int(self.port_edit.text())
        self.ADDR = (self.HOST, self.PORT)
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.tcp_client.connect(self.ADDR)
            self.label.setText(self.HOST+":"+str(self.PORT)+"已连接")
        except  ConnectionRefusedError as e:
            self.label.setText(str(e))
            print(e)

    def break_off(self):
        self.tcp_client.close()
        self.label.setText("连接已断开")

    def load_file(self):
        # data = "videoUpdate "+ str(self.file_edit.text())
        data = str(self.file_edit.text())
        self.tcp_client.send(data.encode())
        self.connect = str(self.tcp_client.recv(10240).decode())
        # self.connect.append(str(self.tcp_client.recv(1024).decode()+"\n"))
        self.textEdit.append(self.connect)
        print(self.connect)

    def play_video(self):
        data = "videoPlay"
        self.tcp_client.send(data.encode())
        self.connect = str(self.tcp_client.recv(1024).decode())
        # self.connect.append(str(self.tcp_client.recv(1024).decode()+"\n"))
        self.textEdit.append(self.connect)

    def push_video(self):
        data = "videoPause"
        self.tcp_client.send(data.encode())
        self.connect = str(self.tcp_client.recv(1024).decode())
        # self.connect.append(str(self.tcp_client.recv(1024).decode()+"\n"))
        self.textEdit.append(self.connect)

    def stop_video(self):
        data = "videoStop"
        self.tcp_client.send(data.encode())
        self.connect = str(self.tcp_client.recv(1024).decode())
        # self.connect.append(str(self.tcp_client.recv(1024).decode()+"\n"))
        self.textEdit.append(self.connect)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    vieo_gui = myMainWindow()
    vieo_gui.show()
    sys.exit(app.exec_())