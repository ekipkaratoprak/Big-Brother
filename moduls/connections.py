import json, gridfs

from bson import json_util
from pymongo import MongoClient
from moduls.config import *

class MongoDB:
    """
    MongoDB Variable and Function Class
    """
    def __init__(self, host, port):
        """
        INIT Function
        """
        self.client = MongoClient(
        host=host,
        port=port
        )

        self.face = self.client.FACE
        self.yetkisiz = self.client.YETKISIZ
        self.IP = self.client.IP

        if not list(self.IP.IPS.find({})):
            self.IP.IPS.insert_one({"IP_ADRESS": "127.0.0.1"})

        self.face_fs = gridfs.GridFS(self.face, "FACES")

        if  not list(self.face.FACES.find({})):
            self.add_image(TEST_USER, self.get_byte(TEST_FILE))
            #coll.update(TEST_USER, data, upsert=True);
            #self.face_fs.insert(TEST_USER, self.get_byte(TEST_FILE),upsert=True)

        self.yetkisis_fs = gridfs.GridFS(self.yetkisiz, "YETKISIZ")

    def content_list(self):
        """
        MongoDB Get Image List
        """
        return self.face.FACES.files.find({})

    def get_content(self, filename):
        """
        MongoDB Get Image Content Function
        """
        f_id = self.face.FACES.files.find_one({ "filename" : filename }, { "_id" : 1 })
        return self.face_fs.get(f_id['_id']).read()

    def sub_reader(self, colm):
        """
        MongoDB Read Function
        """
        for key in colm.find():
            print(json.dumps(key, indent=4, default=json_util.default))

    def add_image(self, file_name, content):
        """
        MongoDB Add Image Function
        """
        self.face_fs.put(content, filename=file_name)

    def add_yetkisiz(self, file_name, content):
        """
        MongoDB Add Image Function
        """
        self.yetkisis_fs.put(content, filename=file_name, encoding='utf-8')

    def delete_users(self, filename):
        """
        MongoDB Delete Users Function
        """
        f_id = self.face.FACES.files.find_one({ "filename" : filename }, { "_id" : 1 })
        self.face_fs.delete(f_id['_id'])

    def update_Ip(self, Ip_adress):
        update = self.IP.IPS.find_one({})
        self.IP.IPS.update_one(update, { "$set":{"IP_ADRESS":Ip_adress}})

    def get_Ip(self):
        data = self.IP.IPS.find_one({})
        return data.get("IP_ADRESS")

    def get_byte(self, filename):
        with open(filename, 'rb') as fd:
            return fd.read()
