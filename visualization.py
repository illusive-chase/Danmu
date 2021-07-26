# -*- coding: utf-8 -*-
# filename: visualization.py
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import time
import socket
import os
import urllib
import urllib.request
from multiprocessing import Process, Queue
import threading 
import random

class Danmu(QLabel):
    font = QFont('SimHei', 20, 100)
    pe = QPalette()  
    pe.setColor(QPalette.WindowText, Qt.white)

    def __init__(self, parent, text, y=0, color=QColor(255, 255, 255)):
        super().__init__(text, parent)
        self.text = text
        self.fin = False
        self.parent = parent
        self.setFont(self.font)
        self.setposY(y)
        self.setcolor(color)
        self.setPalette(self.pe)
        self.animation = QPropertyAnimation(self, b'pos')
        baseTime = int(min(15, len(text) * 0.5 + 5) * 1000)
        self.animation.setDuration(random.randint(int(baseTime * 0.8), int(baseTime * 1.2)))
        self.animation.setStartValue(QPoint(QDesktopWidget().screenGeometry().width(), self.posY))
        self.animation.setEndValue(QPoint(-self.width()-5, self.posY))
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.start()
        self.animation.finished.connect(self.finish)

    def setposY(self, y):
        self.posY = y

    def setcolor(self, color):
        self.color = color

    def finish(self):
        self.fin = True


class DanmuWindow(QWidget):
    _signal = pyqtSignal(str) 
    def __init__(self):
        super().__init__()
        self._signal.connect(self.mySignal)
        self.setGeometry(0, 0, QDesktopWidget().screenGeometry().width(), QDesktopWidget().screenGeometry().height()/3)
        self.th = threading.Thread(target=self.getDanmu)
        self.th.setDaemon(True)
        self.th.start()
        self.danmu = []
        self.waiting = []
    
    def mySignal(self, text):
        danmu = Danmu(self, text, random.randint(0, 190), QColor(255, 255, 255))
        danmu.show()
        self.danmu.append(danmu)

    def getDanmu(self):
        time.sleep(1)
        url = "http://121.36.49.200/danmu"
        while True:
            data = b''
            try:
                data = urllib.request.urlopen(url).read()
            except Exception as Argument:
                print(Argument)
            if data != b'':
                msg = data.decode('utf-8')
                print(msg)
                self.waiting += msg.split('\n')
            for _ in range(1):
                if self.waiting:
                    self._signal.emit(self.waiting[0])
                    self.waiting.pop(0)
            while self.danmu and self.danmu[0].fin:
                self.danmu[0].setParent(None)
                self.danmu[0].deleteLater()
                self.danmu.pop(0)
            time.sleep(0.2)


def invoke_gui():
    app = QApplication(sys.argv)
    win = DanmuWindow()
    win.setAttribute(Qt.WA_TranslucentBackground)
    win.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    p = Process(target=invoke_gui, args=())
    p.start()
