from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GUI_server import Ui_MainWindow
from threading import Thread
import sys, socket, time, os
from myVideoWidget import myVideoWidget


class myMainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, file='E:\\1.mp4', port=3011, Volume = 50):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.file = file
        self.Volume = Volume
        self.plist = []
        self.sld_video_pressed=False  # 判断当前进度条识别否被鼠标点击
        self.videoFullScreen = False   # 判断当前widget是否全屏
        self.videoFullScreenWidget = myVideoWidget()   # 创建一个全屏的widget
        self.videoFullScreenWidget.setFullScreen(True)
        self.videoFullScreenWidget.hide()               # 不用的时候隐藏起来
        # 创建视频输出的窗口
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setVideoOutput(self.wgt_video)  # 视频播放输出的widget
        self.player.setNotifyInterval(1)
        self.player.setVolume(self.Volume)
        # 对按钮绑定相应函数
        self.player.positionChanged.connect(self.changeSlide)      # change Slide
        self.btn_openFile.clicked.connect(self.openVideoFlie)   #打开文件
        self.btn_play.clicked.connect(self.playVideo)   # play
        self.btn_stop.clicked.connect(self.pauseVideo)  # pause
        # self.playlist.
        self.sld_video.sliderMoved.connect(self.moveSlider)   # 进度条拖拽跳转
        self.sld_video.ClickedValue.connect(self.clickedSlider)  # 进度条点击跳转
        self.videoFullScreenWidget.doubleClickedItem.connect(self.Full_Screen)  #双击响应
        self.wgt_video.doubleClickedItem.connect(self.Full_Screen)   #双击响应
        self.sld_video.setTracking(False)
        self.sld_video.sliderPressed.connect(self.pressSlider)
        self.sld_video.sliderReleased.connect(self.releaseSlider)

        self.ip_list = []
        self.port = port
        # 参数介绍：AF_INET 代表IPV4类型, SOCK_STREAM代表tcp传输协议类型 ,注：AF_INET6代表IPV6
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置端口号复用，让程序退出端口号立即释放，否则的话在30秒-2分钟之内这个端口是不会被释放的，这是TCP的为了保证传输可靠性的机制。
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # 给客户端绑定端口号，客户端需要知道服务器的端口号才能进行建立连接。IP地址不用设置，默认就为本机的IP地址。
        self.tcp_server.bind(("", self.port))
        # 设置监听
        # 128:最大等待建立连接的个数， 提示： 目前是单任务的服务端，同一时刻只能服务与一个客户端，后续使用多任务能够让服务端同时服务与多个客户端
        # 不需要让客户端进行等待建立连接
        # listen后的这个套接字只负责接收客户端连接请求，不能收发消息，收发消息使用返回的这个新套接字tcp_client来完成
        self.tcp_server.listen(128)

    def moveSlider(self, position):
        self.sld_video_pressed = True
        if self.player.duration() > 0: # 开始播放才允许跳转
            video_position = int((position / self.length) * self.player.duration())
            self.player.setPosition(video_position)
            self.lab_video.setText(str(video_position//1000//60)+":"+str(video_position//1000%60)+"/"+self.video_time)

    def clickedSlider(self, position):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / self.length) * self.player.duration())
            self.player.setPosition(video_position)
            self.lab_video.setText(str(video_position//1000//60)+":"+str(video_position//1000%60)+"/"+self.video_time)
        else:
            self.sld_video.setValue(0)

    def changeSlide(self, position):
        self.get_video_time()
        if not self.sld_video_pressed:  # 进度条被鼠标点击时不更新
            self.vidoeLength = self.player.duration()+0.1
            self.sld_video.setValue(round((position/self.vidoeLength)*self.length))
            self.Status = str(position//1000//60)+":"+str(position//1000%60)
            self.lab_video.setText(self.Status+"/"+self.video_time)

    def get_video_time(self): # 获取输入文件的总时长
        self.length = self.player.duration() // 1000
        self.video_min = self.length // 60
        self.video_sec = self.length % 60
        self.video_time = str(self.video_min)+":"+str(self.video_sec)
        self.sld_video.setMaximum(self.length)

    def Full_Screen(self): # 全屏切换操作
        if self.videoFullScreen:
            self.videoFullScreenWidget.hide()
            self.player.setVideoOutput(self.wgt_video)
            self.videoFullScreen = False
        else:
            self.videoFullScreenWidget.show()
            self.player.setVideoOutput(self.videoFullScreenWidget)
            self.videoFullScreen = True

    def pressSlider(self):
        self.sld_video_pressed = True
        print("pressed")
 
    def releaseSlider(self):
        self.sld_video_pressed = False

    def openVideoFlie(self):
        self.player.setMedia(QMediaContent(QFileDialog.getOpenFileUrl()[0]))  # 选取视频文件
        self.player.play()  # 播放视频
        print(self.player.availableMetaData())

    def playVideo(self):
        self.player.play()

    def pauseVideo(self):
        self.player.pause()

    def set_ip_lab(self):
        lip = "-----------------------------\n"
        for i in self.ip_list:
            lip += i + "已连接\n"
        print(lip)
        self.ip_lab.append(lip) # 追加输出已连接的设备端口号
        self.ip_lab.moveCursor(self.ip_lab.textCursor().End)

    def tcp_com(self):
        while True:
            tcpCliSock, addr = self.tcp_server.accept()
            self.ip_list.append(str(addr))
            self.set_ip_lab()
            # 当客户端和服务端建立连接成功以后，需要创建一个子线程，不同子线程负责接收不同客户端的消息
            sub_thread = Thread(target=self.handle_client_request, args=(tcpCliSock, addr))
            # 设置守护主线程
            sub_thread.setDaemon(True)
            # 启动子线程
            sub_thread.start()

    def handle_client_request(self, tcpCliSock, addr): #设置接收触发
        while True:
            try:
                data = tcpCliSock.recv(1024) # 接收前1024个字符
            except ConnectionResetError as e:
                print(e)
                break
            if not data:
                break
            print(data.decode())
            content = data.decode()
            ###
            if "videoUpdate" in content:
                self.videoUpdate(content, tcpCliSock)
            elif content == "videoPlay":
                self.videoPlay(content, tcpCliSock)
            elif content == "videoPause":
                self.videoPause(content, tcpCliSock)
            elif content == "videoStop":
                self.videoStop(content, tcpCliSock)
            elif content == "videoPrev":
                self.videoPrev(content, tcpCliSock)
            elif content == "videoNext":
                self.videoNext(content, tcpCliSock)
            elif content == "videoOne":
                self.videoOne(content, tcpCliSock)
            elif content == "videoMore":
                self.videoMore(content, tcpCliSock)
            elif content == "videoGetStatus":
                self.videoGetStatus(content, tcpCliSock)
            elif content == "videoGetList":
                self.videoGetList(content, tcpCliSock)
            elif "InsSystemVol" in content:
                self.InsSystemVol(content, tcpCliSock)
            elif "DesSystemVol" in content:
                self.DesSystemVol(content, tcpCliSock)
            elif "MuteSystemVol" in content:
                self.MuteSystemVol(content, tcpCliSock)
            else:
                tcpCliSock.send(('[%s] %s' %(time.ctime(), "Command error")).encode())
            ###
        self.ip_list.remove(str(addr))
        self.set_ip_lab()
        tcpCliSock.close()

    def videoUpdate(self, content, tcpCliSock): # 加载视频并⽴即播放
        file = content.split()[1:] # 分割输入文本
        if file:
            #self.playlist.clear()
            for f in file:
                if os.path.exists(f):
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f))) # 添加播放列表
                    self.plist.append(f)
                else:
                    tcpCliSock.send(('[%s] %s' %(time.ctime(), f+" does not exist!")).encode())
            self.playlist.setPlaybackMode(3)  # 0：单曲播放，1：单曲循环，2：顺序播放，3：列表循环，4：随机播放
            self.player.setPlaylist(self.playlist)
        else:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file)))
        tcpCliSock.send(('[%s] %s' %(time.ctime(), ",".join(self.plist)+" Load successful. Start playing!")).encode())
        self.player.play()
        self.player.pause()
        self.player.play()

    def videoPlay(self, content, tcpCliSock): # 视频播放命令
        if self.plist or self.player.duration() > 0:
            self.player.play()
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "Continue to play")).encode())
        else:
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "No file loaded")).encode())

    def videoPause(self, content, tcpCliSock): # 视频暂停命令
        self.player.pause()
        tcpCliSock.send(('[%s] %s' %(time.ctime(), "Pause playing")).encode())

    def videoStop(self, content, tcpCliSock): # 视频停⽌命令
        self.player.stop()
        self.playlist.clear()
        self.plist.clear()
        tcpCliSock.send(('[%s] %s' %(time.ctime(), "Stop playing")).encode())

    def videoPrev(self, content, tcpCliSock): # 视频上⼀曲命令
        self.playlist.previous()
        tcpCliSock.send(('[%s] %s' %(time.ctime(), "play the previous one")).encode())

    def videoNext(self, content, tcpCliSock): # 视频下⼀曲命令
        self.playlist.next()
        tcpCliSock.send(('[%s] %s' %(time.ctime(), "play the next one")).encode())

    def videoOne(self, content, tcpCliSock): # 设置单曲播放
        self.playlist.setPlaybackMode(1)
        tcpCliSock.send(('[%s] %s' %(time.ctime(), "Set the single cycle")).encode())

    def videoMore(self, content, tcpCliSock): # 设置列表循环
        self.playlist.setPlaybackMode(3)
        tcpCliSock.send(('[%s] %s' %(time.ctime(), "Set the list loop")).encode())

    def videoGetStatus(self, content, tcpCliSock): # 获取播放进度
        try:
            if self.player.duration() > 0:
                tcpCliSock.send(('[%s] %s' %(time.ctime(), self.plist[self.playlist.currentIndex()]+
                    "   "+self.Status +"/" +self.video_time)).encode())
            else:
                tcpCliSock.send(('[%s] %s' %(time.ctime(), "No file loaded")).encode())
        except IndexError as e:
            tcpCliSock.send(('[%s] %s' %(time.ctime(), e)).encode())

    def videoGetList(self, content, tcpCliSock): # 获取播放列表
        if self.plist:
            print(",".join(self.plist))
            tcpCliSock.send(('[%s] %s' %(time.ctime(), ",".join(self.plist))).encode())
        else:
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "The playlist is empty")).encode())

    def InsSystemVol(self, content, tcpCliSock): # 增加系统⾳量
        try:
            Volume = content.split()[1:] # 分割输入文本
            self.Volume += int(Volume[0])
            self.player.setVolume(self.Volume)
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "Set volume to " + str(self.Volume) + "%")).encode())
        except ValueError as e:
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "Command error")).encode())

    def DesSystemVol(self, content, tcpCliSock): # 减⼩系统⾳量
        try:
            Volume = content.split()[1:] # 分割输入文本
            self.Volume -= int(Volume[0])
            self.player.setVolume(self.Volume)
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "Set volume to " + str(self.Volume) + "%")).encode())
        except ValueError as e:
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "Command error")).encode())

    def MuteSystemVol(self, content, tcpCliSock): # 静⾳/取消静⾳系统⾳量
        try:
            mute = content.split()[1:] # 分割输入文本
            if int(mute[0]) == 1:
                self.player.setVolume(0)
                tcpCliSock.send(('[%s] %s' %(time.ctime(), "Set the mute OK")).encode())
            elif int(mute[0]) == 0:
                self.player.setVolume(self.Volume)
                tcpCliSock.send(('[%s] %s' %(time.ctime(), "Cancel the mute OK")).encode())
            else:
                tcpCliSock.send(('[%s] %s' %(time.ctime(), "xx is 1: mute; is 0: unmuted.")).encode())
        except ValueError as e:
            tcpCliSock.send(('[%s] %s' %(time.ctime(), "Command error")).encode())

    def xxx(self, content, tcpCliSock):
        pass

    def xxx(self, content, tcpCliSock):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_gui = myMainWindow()
    video_gui.show()
    video_gui.Full_Screen()
    p=Thread(target=video_gui.tcp_com) # 创建TCP通信线程
    p.setDaemon(True) # 开启守护线程
    p.start() # 启用线程
    sys.exit(app.exec_())