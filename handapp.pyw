from handpose_modules.HandTrackingModule import HandDetector
from handpose_modules.PoseModule import PoseDetector
import cv2
import numpy as np
from pynput.keyboard import Key, Controller
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from ui.mainUI import *

class MainCam(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.viewCam)
        self.ui.pushButton.clicked.connect(self.controlTimer)
        # Parameters
        self.width, self.height = 640, 480
        self.buttonPressed = [False, False, False, False, False]
        self.volumeModeSwitch=False
       
        # Hand Detector
        self.detectHand = HandDetector(maxHands = 2, detectionCon = 0.8, trackCon = 0.8)
        self.detectBody = PoseDetector(detectionCon=0.7, trackCon=0.7)

        # Keyboard Controller
        self.keyboard=Controller()

        # Volume
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    

    def press_key(self, button):
        self.keyboard.press(button)
        self.keyboard.release(button)

    def viewCam(self):
        success, img = self.cap.read()
        img=cv2.flip(img,1)
        handP, img = self.detectHand.findHands(img, flipType=False)
        bodyP, img = self.detectBody.findPose(img, draw=False)
        if bodyP :
            if handP :
                hand=handP[0]
                y=hand['lmList'][12][1]
                fingers = self.detectHand.fingersUp(hand)
                detectLimit=bodyP[11][2]
                cv2.line(img,(0,detectLimit),(self.width, detectLimit),(0,0,255),10)
                if y < detectLimit:
                    if self.volumeModeSwitch == False:
                        if hand['type'] == 'Right':
                            if fingers==[1,0,0,0,0] or fingers==[0,0,0,0,0]:
                                if self.buttonPressed[0] == False:
                                    self.press_key(Key.right)
                                    self.buttonPressed[0] = True
                            else: self.buttonPressed[0] = False
                            if fingers == [1,0,1,1,1] or fingers == [0,0,1,1,1]:
                                if self.buttonPressed[1] == False:
                                    self.press_key(Key.esc)
                                    self.buttonPressed[1] = True
                            else: self.buttonPressed[1] = False
                        if hand['type'] == 'Left':
                            if fingers == [1,0,0,0,0] or fingers == [0,0,0,0,0]:
                                if self.buttonPressed[2] == False:
                                    self.press_key(Key.left)
                                    self.buttonPressed[2] = True
                            else: self.buttonPressed[2] = False
                            if fingers == [1,0,1,1,1] or fingers == [0,0,1,1,1]:
                                if self.buttonPressed[3] == False:
                                    self.press_key(Key.f5)
                                    self.buttonPressed[3] = True
                            else: self.buttonPressed[3] = False

                        if fingers == [1,1,1,0,0] or fingers == [0,1,1,0,0]:
                            if self.buttonPressed[4] == False:
                                self.volumeModeSwitch = True
                                self.buttonPressed[4] = True
                        else: self.buttonPressed[4] = False

                if fingers == [1,1,1,0,0] or fingers == [0,1,1,0,0]:
                    if self.buttonPressed[4] == False:
                        self.volumeModeSwitch = False
                        self.buttonPressed[4] = True
                else: self.buttonPressed[4] = False

            if self.volumeModeSwitch == True:
                maxLen = self.detectBody.findDistanceY(12, 24)
                currentLen = self.detectBody.findDistanceY(16, 24)
                if currentLen > maxLen: currentLen = maxLen
                PercentVol = int(np.interp(currentLen,[0,maxLen],[0, 100]))
                barLen = np.interp(currentLen,[0,maxLen],[0, self.height])
                self.volume.SetMasterVolumeLevelScalar(PercentVol/100, None)
                By= self.height - int(barLen)
                cv2.rectangle(img, (0, 0),(30, self.height), (0,0,255),2)
                cv2.rectangle(img, (0, By),(30, self.height), (0,0,255),cv2.FILLED)
                cv2.putText(img, f'{int(PercentVol)}%', (35, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,255))
            
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        step = c * w
        qImg = QImage(img.data, w, h, QImage.Format_RGB888)
        self.ui.label_2.setPixmap(QPixmap.fromImage(qImg))

        
    def controlTimer(self):
        if not self.timer.isActive():
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3,self.width)
            self.cap.set(4,self.height)
            self.timer.start(0)
            self.ui.pushButton.setText("OFF")
        else:
            self.timer.stop()
            self.cap.release()
            cv2.destroyAllWindows()
            self.ui.pushButton.setText("ON")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    Cam = MainCam()
    Cam.show()

    sys.exit(app.exec_())