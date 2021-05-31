# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 16:59:33 2021
@author: meusoft
"""
import urllib.request as urllib
import numpy as np
import cv2

from moduls.functions import gen_frames, test_gen_frames
from flask import Flask, render_template, request, url_for, Response

# Local Library
from moduls.connections import MongoDB
from moduls.config import *


db = MongoDB("localhost", 27017) # MongoDB class requirements host and port variable :)
app=Flask(__name__)

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
        if username==ADMIN and password==ADMIN_PASSWORD:
            return render_template("2_menu_yatay.html")
        elif username=="" and password=="":
            return render_template("1_login.html",hata1=mesaj1)
        else:
            return render_template("1_login.html",hata=mesaj)

@app.route("/kullanicikayit", methods=["GET", "POST"])
def kullanıcıkayıt():
    if request.method=="POST":
        url=db.get_Ip()
        imgResp=urllib.urlopen(url)
        isim=request.form.get("name")
        yas=request.form.get("age")

        checklist=request.form.getlist("kameracheck")
        #görüntü klasöre kayıt edilecek!!!!

        if "Kamera 1" in checklist and "Kamera 2" in checklist:
            db.add_image(isim, imgResp.read())
            db.get_content(isim)

        elif "Kamera 1" in checklist and "Kamera 2" not in checklist:
            db.add_image(isim, imgResp.read())
            db.get_content(isim)

        elif "Kamera 2" in checklist and "Kamera 1" not in checklist:
            db.add_image(isim, imgResp.read())
            db.get_content(isim)

    return render_template("3_kullanıcıkayıt.html")

@app.route("/kullanıcılar", methods=["GET", "POST"])
def kullanıcılar():
    UserList = [i.get('filename') for i in db.content_list() if i.get('filename')]

    if request.method == "POST":
        kullanıcı_isim = request.form.get("k_name")
        if kullanıcı_isim:
            db.delete_users(kullanıcı_isim)
    return render_template("6_kullanıcılar.html", len = len(UserList), UserList = UserList)

@app.route("/kameraip", methods=["GET", "POST"])
def kameraip(ip=db.get_Ip()):
    if request.method == "POST":
        ip = request.form.get("ip_adress")
        db.update_Ip(ip)

        return render_template("2_menu_yatay.html", exip=db.get_Ip())
    return render_template("5_ip_adress.html")

@app.route("/kamera1")
def kamera1():
    return render_template("4_kamera1.html")

@app.route("/anasayfa")
def anasayfa():
    return render_template("2_menu_yatay.html")

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
