import face_recognition
import numpy as np
# import socket programming library
import socket

# import thread module
from _thread import *
import threading
import json

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

print_lock = threading.Lock()
load_dotenv(find_dotenv())

DB_CONNECT_STRING = 'mysql+pymysql://%s:%s@%s/%s' % (os.environ.get('MYSQL_USER'),
                                                     os.environ.get('MYSQL_PASSWORD'),
                                                     os.environ.get('MYSQL_SERVER'),
                                                     os.environ.get('MYSQL_DATABASE'))

engine = create_engine(DB_CONNECT_STRING)
DB_Session = sessionmaker(bind=engine)
session = DB_Session()


# thread fuction
def threaded(c):
    while True:

        # data received from client
        data = c.recv(1024)
        if not data:
            # lock released on exit
            print_lock.release()
            break

        # reverse the given string from client
        data = json.loads(data)
        print(data)
        image = face_recognition.load_image_file(data['path'])
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) == 0:
            c.send(json.dumps({
                'success': False,
                'message': '未找到人脸'
            }).encode('utf-8'))
        elif len(face_encodings) == 2:
            c.send(json.dumps({
                'success': False,
                'message': '找到多张人脸'
            }).encode('utf-8'))

        else:
            print('ok')

            c.send(json.dumps({
                'success': True,
                'data': face_encodings[0].tolist()
            }).encode('utf-8'))
        # connection closed
    c.close()


def Main():
    host = ""

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 28691
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to post", port)

    # put the socket into listening mode
    s.listen(10)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        print_lock.acquire()

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()


if __name__ == '__main__':
    Main()
