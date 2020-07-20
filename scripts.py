import sys
import signal
import requests
import sqlite3
import json
from urllib.request import urlopen
import sys


class Room:

    def __init__(self, id, name):
        self.id = id
        self.name = name


class Device:

    def __init__(self, id, name, status, room):
        self.name = name
        self.status = status
        self.id = id
        self.room = room


url = "http://127.0.0.1:3000"
con = sqlite3.connect('mydatabase.db')
cursorObj = con.cursor()
sql_room_create = "create table if not exists room(localId integer primary Key AUTOINCREMENT, id Varchar2(100)," \
                  "name varchar2(50)) "
cursorObj.execute(sql_room_create)
sql_device_create = "create table if not exists device(localId Integer Primary Key AUTOINCREMENT , id Varchar2(100)," \
                    "name varchar2(50), status bool, room varchar2(100), FOREIGN KEY(room) REFERENCES room(localId)) "
cursorObj.execute(sql_device_create)

with open('token.json') as f:
    data = json.load(f)
    token = "bearer " + data['token']
headers = {
    "Content-Type": "application/json",
    'Authorization': token
}


def signal_handler(sig, frame):
    print('Execting program')
    con.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
# signal.pause()


def update_room(room):
    query = "select * from room where id = '{0}'".format(room.id)
    cursorObj.execute(query)
    try:
        if cursorObj.fetchone()[1] == room.name:
            pass
        else:
            query = "Update room set name='{0}' where id='{1}'".format(
                room.name, room.id)
            cursorObj.execute(query)
    except:
        query = "insert into room(id,name) values ('{0}','{1}')".format(
            room.id, room.name)
        cursorObj.execute(query)


def update_device(device):
    query = "select * from device where id = '{0}'".format(device.id)
    cursorObj.execute(query)
    status = bool(cursorObj.fetchone()[3])
    name = cursorObj.fetchone()[2]
    if cursorObj.fetchone() == None:
        query = "insert into device(id,name,status,room) values ('{0}','{1}','{2}','{3}')".format(device.id,
                                                                                                  device.name,
                                                                                                  device.status,
                                                                                                  device.room)
        print("Insert data  " + query)
        cursorObj.execute(query)
    else:
        if status != device.status:
            query = "update device set status ={0} where id='{1}'".format(
                1 if device.status else 0, device.id)
            cursorObj.execute(query)
            con.commit()
            query = "select * from device where id= '{0}'".format(device.id)
            cursorObj.execute(query)
            print(
                "http://192.168.1.91/{0}/{1}".format(cursorObj.fetchone()[0], 1 if device.status else 0))
            url = "http://192.168.1.91/{0}/{1}".format(
                cursorObj.fetchone()[0], 1 if device.status else 0)
            # response = requests.get(url, timeout=5)
            response = urlopen(url)
            print(response.body)
            print("yes")

            print("device status changed " + query)

        elif name == device.name:
            pass
        else:
            query = "update device set name ='{0}' where id='{1}'".format(
                device.name, device.id)
            print("update Data " + query)


while True:
    response = requests.get(url, headers=headers)
    raw_data = response.json()
    print(raw_data)
    if raw_data['error']:
        print("Url incorrect")
    else:
        print("here")
        for i in raw_data:
            room = Room(i["_id"], i['name'])
            update_room(room)
            for j in i["devices"]:
                device = Device(j["_id"], j["name"], j["status"], i["_id"])
                update_device(device)
        con.commit()

    query = "select * from device"
    cursorObj.execute(query)
