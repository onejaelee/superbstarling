import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
dictTime = {}

class Autosorter:
    def _init_(self, framename, timestamp, presence):
        self.f = framename
        self.t = timestamp
        self.p = presence

def splitvideo(videoname):
    FPS = 25
    # Playing video from file:
    cap = cv2.VideoCapture(str(videoname)+ '.avi')

    try:
        if not os.path.exists('splitframe'):
            os.makedirs('splitframe')
    except OSError:
        print ('Error: Creating directory of data')

    currentFrame = 0
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Saves image of the current frame in jpg file
        if currentFrame % FPS == 0:
            name = './splitframe/' + str(videoname) + str(currentFrame) + '.jpg'
            print ('Creating...' + name)
            cv2.imwrite(name, frame)

        if not ret: break
        currentFrame += 1
        # To stop duplicate images

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    return currentFrame
def timestamp(videoname):
    cframe = self.splitvideo(videoname)
    # figure out the range for the video frames
    for x in range(cframe):
        img = Image.open(str(videoname)+ str(x) + '.jpg')
        crop_img = img[10:35, 340:34]
        text = pytesseract.image_to_string(crop_img)
        #think about if there should be a dictionary for the entire class or just for each video
        #turn the video doodoo into class
        dictTime[str(videoname)+ str(x) + '.jpg'] = text
