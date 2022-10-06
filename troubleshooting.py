#Original file from Chris Dahms: https://github.com/MicrocontrollersAndMore/TensorFlow_Tut_2_Classification_Walk-through
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
#you need to give extra room around the numbers for the program to read it
def doCrop(imagePath, cropPath, x, y, x2, y2):
    im = Image.open(imagePath)
    box = (x, y, x2, y2)
    region = im.crop(box) # extract the box region
    region.save(cropPath) # save it as a separate image
doCrop('Testframes0296.jpg','testing0.jpg',209-10,11-10,337+10,33+10)
img = Image.open('testing0.jpg')
text = pytesseract.image_to_string(img)
print(text)
