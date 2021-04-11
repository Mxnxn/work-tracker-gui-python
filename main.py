import datetime
import requests
import sqlite3
import win32api
from threading import Thread
import time
import tkinter as tk
from tkinter import Text
root = tk.Tk()


class MySqlite:
    def __init__(self):
        self.conn = sqlite3.connect(
            'PAUTILITY.dll', check_same_thread=False)
        self.head = self.conn.cursor()
        result = self.checkIfExists(["timer"])
        if not result:
            self.createTables()

    def checkIfExists(self, table):
        exists = False
        for name in table:
            x2 = self.head.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
            if bool(x2.fetchone()):
                exists = True
        return exists

    def createTables(self):
        self.head.execute(
            '''CREATE TABLE timer (tid INTEGER PRIMARY KEY  AUTOINCREMENT,seconds INTEGER,minutes INTEGER, hours INTEGER)''')
        self.conn.commit()
        print('[+] Tables Successfully Created!')


class Timer(Thread):
    name = ''

    def __init__(self, idle_time, stop_thread, data, errorWidget):
        self.afk = True
        self.active = True
        self.idle_time = idle_time
        self.name = ''
        self.errorWidget = errorWidget
        if data:
            self.seconds = data[1]
            self.minutes = data[2]
            self.hours = data[3]
        else:
            self.seconds = 0
            self.minutes = 0
            self.hours = 0
        self.stop = stop_thread

    def getIdleTime(self, labelll, head, conn):
        event = (win32api.GetTickCount() -
                 win32api.GetLastInputInfo()) / 1000.0
        if event > self.idle_time:
            if(self.afk):
                print("AFK")
                self.afk = False
                self.active = True
        elif event >= 0:
            if(self.active):
                self.afk = True
                time.sleep(1)
                if self.seconds == 20 or self.seconds == 40 or self.seconds == 55:
                    try:
                        x = datetime.datetime.now()
                        ress = requests.post('http://localhost:5000/user/settime', json={
                            'seconds': self.seconds, 'minutes': self.minutes, 'hours': self.hours, 'day': x.strftime("%x"), 'pc': self.name})
                        print(ress.status_code)
                    except Exception as e:
                        self.errorWidget.configure(
                            text="Error : request could not sent!")
                if(self.seconds > 58):
                    self.minutes += 1
                    self.seconds = 0
                    if(self.minutes > 59):
                        self.hours += 1
                        self.minutes = 0
                else:
                    self.seconds += 1
                    labelll.configure(text=self.getActiveTime(),
                                      font=('Arial', 18, 'bold'))

    def getActiveTime(self):
        hh = "0{0}".format(self.hours) if self.hours < 10 else self.hours
        mm = "0{0}".format(self.minutes) if self.minutes < 10 else self.minutes
        ss = "0{0}".format(self.seconds) if self.seconds < 10 else self.seconds
        return '{0}:{1}:{2}'.format(hh, mm, ss)

    def printActiveTime(self):
        while True:
            print(self.getActiveTime())
            time.sleep(1)

    def checkAFK(self, labelll, head, conn):
        while True:
            if(self.stop):
                self.getIdleTime(labelll, head, conn)

    def reset(self, labelll):
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        labelll.configure(text=self.getActiveTime())

    def pause(self, label):
        if self.stop:
            self.stop = False
            label.configure(text="Status: Paused")
        else:
            self.stop = True
            label.configure(text="Status: Running")

    def getName(self, name, box, stop_btn):
        if(name.get() != ""):
            try:
                ress = requests.post(
                    'http://localhost:5000/user/getTime', json={'pc': name.get()})
                print(ress, ress.json())
                if ress.status_code == 200:
                    self.seconds = ress.json()['seconds']
                    self.minutes = ress.json()['minutes']
                    self.hours = ress.json()['hours']
                    self.name = name.get()
                    box.configure(state='disable')
                    self.stop = True
                    self.errorWidget.configure(
                        text="")
                    stop_btn.configure(
                        text="Stop", command=lambda: self.showInput(stop_btn, box, name))
            except Exception as E:
                self.errorWidget.configure(
                    text="Error : request could not sent!")

    def showInput(self, btn, box, name):
        box.configure(state="normal")
        btn.configure(text="Start", command=lambda: self.getName(
            name, entry1, btn))
        self.stop = False
        self.name = ''


if __name__ == "__main__":
    root.title("Work Tracker")
    canvas = tk.Canvas(root, height=0, width=250)
    canvas.pack()
    mSqlite = MySqlite()
    data = mSqlite.head.execute(
        "SELECT * FROM timer WHERE tid = (SELECT MAX(tid) FROM timer);")
    name = tk.StringVar()
    labelll3 = tk.Label(root, text='')
    mTimer = Timer(20, False, data.fetchone(), labelll3)
    try:
        entry1 = tk.Entry(root, textvariable=name)
        entry1.pack(pady=8)
        btn = tk.Button(root, text="Start",
                        command=lambda: mTimer.getName(name, entry1, btn))
        btn.pack(padx=5, pady=4)
        labelll = tk.Label(root, text="Studio Outline",
                           font=('Arial', 18, 'bold'))
        t1 = Thread(target=mTimer.checkAFK, args=(
            labelll, mSqlite.head, mSqlite.conn))
        labelll.pack()
        labelll3.pack(pady=2)
        t1.daemon = True
        t1.start()
        root.mainloop()
    except Exception as e:
        root.destroy
        mTimer.stop = False
