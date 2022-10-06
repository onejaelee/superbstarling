import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
import pandas as pd
import shutil
import re
import test as ml

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
#path to video files to use for training
video_dir = os.getcwd() + '/training_videos'
#path to folder where images labeled absent get sorted to
#I have edited absent and present dir to be different temporarily
absent_dir = os.getcwd() + "/training_images/Absent"
#path to folder where images labeled present get sorted to
present_dir = os.getcwd() + "/training_images/Present"
#path to excel file to label images
excel_dir = os.getcwd() + "/onejaevideocoding.xlsx"

split_dir = os.getcwd() + "/splitframe"
split_name = "splitframe/"
home_dir = os.getcwd()
acceptabledates = []

def cross_reference_frame(birdlist):
    if birdlist[0] is not None and home_dir is not None and split_name is not None and birdlist[1] is not -1 and birdlist[2] is not -1 and birdlist[3] is not None:
        classification, confidence = ml.check_image(home_dir + '/' + split_name + '/' + birdlist[0])
        birdlist.append(classification)
        birdlist.append(confidence)
        if (classification == 'Present' and birdlist[3] == True) or (classification == 'Absent' and birdlist[3] == False):
            birdlist.append("Correct")
        else:
            birdlist.append("Wrong")
    else:
        birdlist.append("None")
        birdlist.append("None")
        birdlist.append("None")
    return birdlist

def setBroodAge(exceldirectory, left, right ):
    #Date, Age, nestID
    e, d, n = readExcelAge(exceldirectory)
    global acceptabledates, readerName
    if exceldirectory == 'ONE.JAE.video.coding.xlsx':
        readerName = 'One Jae/'
    elif exceldirectory == 'SHANE.video.coding.xlsx':
        readerName = "Shane/"
    elif exceldirectory == "SARAH.video.coding.xlsx":
        readerName = "Sarah/"
    elif exceldirectory == "GABRIELLE.video.coding.xlsx":
        readerName = "Gabrielle/"
    acceptabledates = []
    ageList = []
    for keys, values in d.iteritems():
        ageList.append([int(i) for i in str(values).split() if i.isdigit()])
    for keys, broodAges in enumerate(ageList):
        inRange = True
        for ages in broodAges:
            if int(ages) <= right and int(ages) >= left:
                inRange = True
            else:
                inRange = False
        if inRange and n[keys] == nestID:
            acceptabledates.append(e[keys])


def changeNest(nestname):
    global absent_dir, present_dir, split_name, nestID
    nestID = nestname
    if not os.path.exists('training_images'+ nestname):
        os.makedirs('training_images' + nestname + "/Present")
        os.makedirs('training_images' + nestname + "/Absent")
    split_name = 'splitframe/' + nestname
    absent_dir = os.getcwd() + "/training_images" + nestname + "/Absent"
    present_dir = os.getcwd() + "/training_images" + nestname + "/Present"

def splitvideo(videoname, folder):


    FPS = 25
    # Playing video from file:
    #assumes that the video will be within the training_videos folder
    print("Opening: " + '/media/onejae/usb/SuperStarling/Read Videos/' + readerName + str(folder) + '/' + str(videoname))
    cap = cv2.VideoCapture('/media/onejae/usb/SuperStarling/Read Videos/' + readerName + str(folder) + '/' + str(videoname))

    try:
        if not os.path.exists(split_name):
            os.makedirs(split_name)
    except OSError:
        print('Error when making directory')

    currentFrame = 0
    while(True):

        ret, frame = cap.read()

        # Turns current frame into jpg file
        if currentFrame % FPS == 0:
            name = './'+ split_name + '/' +  str(videoname)  + str(currentFrame) + '.jpg'
            # print('Creating file: ' + name)
            try:
                cv2.imwrite(name, frame)
            except:
                print("Exception, could create " + name)

        if not ret: break
        currentFrame += 1
        # To stop duplicate images32`

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    return currentFrame

#currently is being used to compile prelabeled data
# image_name, timestamp, datestamp, checkpresence(timestamp, datestamp, adultentersnest, adultleavesnest, date, nestidseries, nestid)))
def readvideofolder(directory, exceldirectory, nestid, folder):
    w, x, y, z = readExcel(exceldirectory)
    dict = {}
    for i in os.listdir(directory):
        presence_list = presencestamp(i, w, x, y, z, nestid, folder, )
        for x in presence_list:
            # print(x)
            final_list = cross_reference_frame(x)
            dict['Image Name'] = final_list[0]
            dict['Time'] = final_list[1]
            dict['Date'] = final_list[2]
            dict['Presence'] = final_list[3]
            dict['Classification'] = final_list[4]
            dict['Confidence level'] = final_list[5]
            dict['Correctness'] = final_list[6]
    df = pd.DataFrame(data)
    df.to_excel("output.xlsx")
    
#Moved labeled frames (present vs absent) into corresponding folders
def organizeframes(birdlist):

    for x in birdlist:
        if x[3] == True:
            shutil.move(home_dir + '/' + split_name + '/' + x[0], present_dir)
            print(str(x[0])+' is ' + str(x[3]))
        elif x[3] == False:
            shutil.move(home_dir + '/' + split_name + '/' + x[0], absent_dir)
            print(str(x[0]) + ' is ' + str(x[3]))


#Crops image to specified dimension
def crop(imagePath,x,y,x2,y2):
    img = Image.open(imagePath)
    return img.crop((x,y,x2,y2))

#Uses Tesseract to read time on video file (black and white so requires extrapolation when background obscures time)
def getdate(imagePath):
    whitelist = set('0123456789-')
    crop_img = crop(imagePath,35-10,10-10,197+10,28+10)
    text = pytesseract.image_to_string(crop_img)
    #this removes anything that is not in the whitelist, like commas if tesseract reads one for some reason
    processtext = (''.join([c for c in text if c in whitelist]))
    if len(processtext) == 10 and processtext.count('-') == 2:
        return processtext + ' 00:00:00'
    else:
        print("Tesseract Error: Reading date")
        return -1

#Labels times for a specific image
def gettime(imagePath):

    whitelist = set('0123456789:')
    crop_img = crop(imagePath, 209-10, 5, 337+10, 33+10)
    text = pytesseract.image_to_string(crop_img)
    # this removes anything that is not in the whitelist, like commas if tesseract reads one because the time should only include whitelisted char
    return ''.join([c for c in text if c in whitelist])
    # return text

#same as timestamp, but also logs presence for videos that already have data
#Basically, if the frame corresponds to labeled data - label it
def presencestamp(videoname, adultentersnest, adultleavesnest, date, nestidseries, nestid, folder):

    birdlist = []
    cframe = splitvideo(videoname, folder)
    referencetime = -1
    datestamp = -1
    timestamp = -1
    referenceframe = 0
    # figure out the range for the video frames
    for x in range(int(cframe/25) + (cframe%5 > 0)):

        image_name = str((videoname)+ str(x*25) + '.jpg')
        print('Stamping: ' + image_name)
        if referencetime == -1:
            referencetime = converttime(gettime('./'+ split_name + '/' + image_name))
            if referencetime != -1:
                referenceframe += 1
        elif referencetime != -1:
            print('Reference time: ' + str(referencetime) +' was used')
            timestamp = float(float(referencetime) + float(referenceframe/86400))
            referenceframe +=1

        if datestamp == -1:
            datestamp = getdate('./'+ split_name + '/' + image_name)
        print('Nest ID: ' + str(nestid))
        print('Timestamp: ' + str(timestamp))
        print('Datestamp: ' + str(datestamp))
        print('Image Name: ' + str(image_name))
        #think about if there should be a dictionary for the entire class or just for each video
        #check if this timestamp is a unique value since some of the times overlap in the bird footage
        try:
            i = birdlist.index(timestamp)
        except ValueError:
            i = -1
        if i == -1:
            if timestamp != -1 and datestamp != -1:
                birdlist.append([image_name, timestamp, datestamp, checkpresence(timestamp, datestamp, adultentersnest, adultleavesnest, date, nestidseries, nestid)])

    return birdlist

#Use readExcel to extract relevant bird presence data from labeled Excel sheet
#sometimes people capitalize video coding wrong and it throws an error
def readExcel(directory):
    sheet = pd.read_excel(directory, sheet_name='Video coding')

    w = sheet['adult.enters.nest']
    x = sheet['adult.leaves.nest']
    y = sheet['date']
    z = sheet['nest.id']

    return w, x, y, z

#readExcel, but specifically labels age (which all frames should correspond to a data entry)
def readExcelAge(directory):
    try:
        sheet = pd.read_excel(directory, sheet_name='Filming overview')
    except Exception:
        try:
            sheet = pd.read_excel(directory, sheet_name='Filming Overview')
        except Exception:
            print("Sheet name of Filming Overview or Filming overview not found")
    d = sheet["date"]
    a = sheet["brood.age"]
    n = sheet["nest.id"]

    return d, a, n

def checkfloat(number):
    try:
        x = float(number)
        return True
    except (ValueError,  TypeError) as error:
        return False

#Turns timestamp read from OCR into 00:00:00 format that Excel uses
def converttime(timestamp):
    try:
        (h, m, s) = timestamp.split(':')
    except ValueError:
        print(timestamp + " is unreadable")
        return -1
    #converts a time in 00:00:00 format into the excel format, which is a fraction of a day
    if len(h) == 2 and len(m) == 2 and len(s) == 2:
        return (float(h)*3600 + float(m)*60 + float(s))/86400
    else:
        print(timestamp + " is unreadable")
        return -1

#checkpresence(f,d,d,d, verbose=True)
#for a given frame/image, checks if the timestamp read from the video matches a labeled time frame from the human labeled data.
def checkpresence(timestamp, datestamp, adultentersnest, adultleavesnest, dateseries, nestidseries, nestid, verbose=False):
    time = timestamp
    index = -1
    # value corresponds to the time in adult enters nest, while key refers to the index
    for key, value in adultentersnest.iteritems():
        # You need an if statement that checks if the corresponding (use the key to check) date matches for that line or else it will automatically only check through 5/13 by default since it is first
        if str(nestidseries[key]) == str(nestid):
            if str(dateseries[key]) == datestamp:
                if ((dateseries[key])) in acceptabledates:
                    if verbose:
                        print(dateseries[key])
                    if checkfloat(value):
                        if float(value) <= time:
                            index = key
                        elif float(value) > time:
                            break
                else:
                    print('Error: Not within the correct age range.')
                    return None
    if index != -1:
        try:
            if adultleavesnest[index] > time or adultentersnest[index] == time:
                return True
            elif adultleavesnest[index] < time and adultentersnest[index+1] > time:
                return False
        except (ValueError, TypeError, IndexError) as error:
            print('Error: ' + ' written time is not in right format or timestamp is not within the excel spreadsheet')
            return None
    else:
        print('Error: This timestamp given is not within the excel spreadsheet')
        return None



def main():
    #Because it uses OCR with hundreds of hours of videos and analyzes second by second, it will take more than a day to process them all
    changeNest('2018_SRB2_3.2')
    setBroodAge('ONE.JAE.video.coding.xlsx', 0, 100)
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/One Jae/' + '/2018_SRB2_3.2_2018.05.13', 'ONE.JAE.video.coding.xlsx', '2018_SRB2_3.2', '2018_SRB2_3.2_2018.05.13')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/One Jae/' + '/2018_SRB2_3.2_2018.05.17','ONE.JAE.video.coding.xlsx', '2018_SRB2_3.2', '2018_SRB2_3.2_2018.05.17')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/One Jae/' + '/2018_SRB2_3.2_2018.05.19','ONE.JAE.video.coding.xlsx', '2018_SRB2_3.2', '2018_SRB2_3.2_2018.05.19')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/One Jae/' + '/2018_SRB2_3.2_2018.05.21','ONE.JAE.video.coding.xlsx', '2018_SRB2_3.2', '2018_SRB2_3.2_2018.05.21')
    changeNest('2018_RV_3')
    setBroodAge('ONE.JAE.video.coding.xlsx', 3, 5)
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/One Jae/' + '/2018_RV_3_2018.05.18', 'ONE.JAE.video.coding.xlsx', '2018_RV_3', '2018_RV_3_2018.05.18')
    ## SRB2_6 was not done, doesnt work for some reason, OpenCv error
    changeNest('2018_SRB2_6')
    setBroodAge('ONE.JAE.video.coding.xlsx', 3, 5)
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/One Jae/' + '/2018_SRB2_6_2018.05.10', 'ONE.JAE.video.coding.xlsx', '2018_SRB2_6', '2018_SRB2_6_2018.05.10')
    #
    #
    changeNest('2018_CF2_1')
    setBroodAge('GABRIELLE.video.coding.xlsx',3,5)
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_CF2_1_2018.04.09', 'GABRIELLE.video.coding.xlsx', '2018_CF2_1', '2018_CF2_1_2018.04.09')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_CF2_1_2018.04.10', 'GABRIELLE.video.coding.xlsx', '2018_CF2_1', '2018_CF2_1_2018.04.10')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_CF2_1_2018.04.13', 'GABRIELLE.video.coding.xlsx', '2018_CF2_1', '2018_CF2_1_2018.04.13')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_CF2_1_2018.04.14', 'GABRIELLE.video.coding.xlsx', '2018_CF2_1', '2018_CF2_1_2018.04.14')
    changeNest('2018_SRB1_5.2')
    setBroodAge('GABRIELLE.video.coding.xlsx', 3, 5)
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_SRB1_5.2_2018.05.10', 'GABRIELLE.video.coding.xlsx', '2018_SRB1_5.2', '2018_SRB1_5.2_2018.05.10')
    changeNest('2018_SRB2_1')
    setBroodAge('GABRIELLE.video.coding.xlsx', 3, 5)
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_SRB2_1_2018.04.03', 'GABRIELLE.video.coding.xlsx', '2018_SRB2_1', '2018_SRB2_1_2018.04.03')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_SRB2_1_2018.04.05','GABRIELLE.video.coding.xlsx', '2018_SRB2_1', '2018_SRB2_1_2018.04.05')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_SRB2_1_2018.04.07','GABRIELLE.video.coding.xlsx', '2018_SRB2_1', '2018_SRB2_1_2018.04.07')
    readvideofolder('/media/onejae/usb/SuperStarling/Read Videos/Gabrielle/' + '/2018_SRB2_1_2018.04.09','GABRIELLE.video.coding.xlsx', '2018_SRB2_1', '2018_SRB2_1_2018.04.09')

if __name__ == "__main__":
    main()
        dictTime[str(videoname)+ str(x) + '.jpg'] = text
