from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from GUI_client import Ui_MainWindow
from myVideoWidget import myVideoWidget
import sys, socket

    # # 1 创建客户端套接字对象tcp_client_1
    # # 参数介绍：AF_INET 代表IPV4类型, SOCK_STREAM代表tcp传输协议类型 ,注：AF_INET6代表IPV6
   
    # tcp_client_1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    # # 2 通过客户端套接字的connect方法与服务器套接字建立连接  
    # # 参数介绍：前面的ip地址代表服务器的ip地址，后面的61234代表服务端的端口号 。
    
    # tcp_client_1.connect(("127.0.0.1",3011))

    # # 将编号好的数据存到变量send_data中，注：encode(encoding='utf-8)是将数据转换成utf-8的格式发送给服务器
    # send_data = "你好，服务器，我是客户端1号".encode(encoding='utf-8')
     
    # # 3 通过客户端套接字的send方法将数据发送给服务器
    # tcp_client_1.send(send_data)

    # # 4 通过客户端套接字的recv方法来接受服务器返回的数据存到变量recv_data中，1024是可接收的最大字节数。
    # recv_data = tcp_client_1.recv(1024)
    
    # # 将接收到的服务器数据recv_data通过decode方法解码为utf-8
    # print(recv_data.decode(encoding = 'utf-8'))

    # # 5 最后关闭客户端套接字连接
    # tcp_client_1.close()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    vieo_gui = myMainWindow()
    vieo_gui.show()
    sys.exit(app.exec_())