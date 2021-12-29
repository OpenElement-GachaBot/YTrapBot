import numpy as np
import cv2
from mss import mss

mon = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

sct = mss()

def getScreen():
    return (np.array(sct.grab(mon)))

def getGrayScreen():
    frame_gray = cv2.cvtColor(getScreen(), cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.equalizeHist(frame_gray)
    return frame_gray

def getWidth():
    return 1920

def getHeight():
    return 1080

