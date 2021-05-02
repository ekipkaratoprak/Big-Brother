# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 16:59:33 2021

@author: meusoft
"""

from flask import Flask, render_template, request, url_for, Response
import urllib.request as urllib
import numpy as np
import cv2
import face_recognition
import os
from datetime import datetime

app=Flask(__name__)


def gen_frames():
    url='http://192.168.2.2:8080/shot.jpg'
    #stream=urllib.urlopen(url)
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
    path = 'cam1'
    images = []
    classNames = []
    myList = os.listdir(path)
    url='http://192.168.2.2:8080/shot.jpg'
    #stream=urllib.urlopen(url)

    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

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
            #print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                #print(name)
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
                cv2.imwrite('./yetkisizler/%s.jpg' %file_name ,img)

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
"""
def fot_cek(name):
    url='http://192.168.1.35:8080/shot.jpg'
    stream=urllib.urlopen(url)
    imgResp=urllib.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)

    cv2.imwrite('./ImagesBasic/%s.jpg' % name,img)
"""

@app.route('/video_feed')
def video_feed():
    return Response(test_gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/")
def index():
    return render_template("1_login.html")

@app.route("/menu", methods=["GET","POST"])
def menu():
    mesaj="Yanlış Kullanıcı Adı ve Şifre"
    mesaj1="Lütfen Formu Doldurun!"
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("pass")
        if username=="meu" and password=="123":
            return render_template("2_menu_yatay.html")
        elif username=="" and password=="":
            return render_template("1_login.html",hata1=mesaj1)
        else:
            return render_template("1_login.html",hata=mesaj)
    else:
        pass

@app.route("/kullanicikayit", methods=["GET", "POST"])
def kullanıcıkayıt():
    if request.method=="POST":
        url='http://192.168.2.2:8080/shot.jpg'
        #stream=urllib.urlopen(url)
        imgResp=urllib.urlopen(url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)

        isim=request.form.get("name")
        yas=request.form.get("age")
        checklist=request.form.getlist("kameracheck")
        #görüntü klasöre kayıt edilecek!!!!

        if "Kamera 1" in checklist and "Kamera 2" in checklist:
            cv2.imwrite('./cam1/%s.jpg' % isim,img)
            cv2.imwrite('./cam2/%s.jpg' % isim,img)
        elif "Kamera 1" in checklist and "Kamera 2" not in checklist:
            cv2.imwrite('./cam1/%s.jpg' % isim,img)
        elif "Kamera 2" in checklist and "Kamera 1" not in checklist:
            cv2.imwrite('./cam2/%s.jpg' % isim,img)

    return render_template("3_kullanıcıkayıt.html")

@app.route("/kamera1")
def kamera1():
    return render_template("4_kamera1.html")

@app.route("/kamera2")
def kamera2():
    return render_template("5_kamera2.html")

# @app.route("/")
# def index():
#     return render_template("1_login.html", sayı1=10, sayı2=20)
#HTML ÜZERİNDE {{number}} yazarsak bu değişkene ulaşabiliriz.

# @app.route("/search")
# def indexS():
#     return "ARA"

# @app.route("/delete/<string:id>")
# def delete(id):
#     return "Id: "+id


if __name__=="__main__":
    app.run(debug=True)
