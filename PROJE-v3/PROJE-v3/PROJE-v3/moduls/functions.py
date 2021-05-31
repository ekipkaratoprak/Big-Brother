import urllib.request as urllib
import face_recognition
import numpy as np
import cv2
import os
from datetime import datetime

from moduls.config import URL_ADRESS
from moduls.connections import MongoDB

db = MongoDB("localhost", 27017)

def gen_frames():
    url=db.get_Ip()

    while True:
        imgResp=urllib.urlopen(url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)
        # all the opencv processing is done here
        scale_percent = 60 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)

            # resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        ret, buffer = cv2.imencode('.jpg', resized)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def test_gen_frames():
    images = []
    classNames = []
    url=db.get_Ip()

    if db.content_list():
        for cl in db.content_list():
            curImg = cv2.imdecode(np.frombuffer(db.get_content(cl.get('filename')), np.uint8), -1)
            images.append(curImg)
            classNames.append(os.path.splitext(cl.get('filename'))[0])

    else:
        return False

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    while True:
        imgResp=urllib.urlopen(url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)

        imgS = cv2.resize(img,(0,0),None,0.25,0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

        for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()

                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

            else:
                date = datetime.now()
                BASE_DIR = './yetkisizler'
                PREFIX = 'non_detected'
                EXTENSION = 'jpg'
                file_name_format = "{:s}-{:%Y%m%d_%H%M%S}.{:s}"
                file_name = file_name_format.format(PREFIX, date, EXTENSION)
                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(img,(x1,y1),(x2,y2),(0,0,255),2)
                cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,0,255),cv2.FILLED)
                cv2.putText(img,"YETKISIZ GIRIS",(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                #cv2.imwrite('./yetkisizler/%s' % file_name ,img)
                db.add_yetkisiz("YETKISIZ", convert_bytes(img))

        frame = convert_bytes(img)
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def convert_bytes(img):
    scale_percent = 60 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    ret, buffer = cv2.imencode('.jpg', resized)
    return buffer.tobytes()
