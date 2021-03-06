from _overlapped import NULL
import hashlib
import sqlite3
import time
import os
import traceback
import json


class QQoutput():
    def __init__(self, dir, qq_self, qq, mode, emoji):
        self.dir = dir
        self.key = self.get_key()  # 解密用的密钥
        db = os.path.join(dir, "databases", qq_self + ".db")
        self.c1 = sqlite3.connect(db).cursor()
        db = os.path.join(dir, "databases", "slowtable_" + qq_self + ".db")
        self.c2 = sqlite3.connect(db).cursor()

        self.qq_self = qq_self
        self.qq = qq
        self.mode = mode
        self.emoji = emoji

        self.num_to_name = {}

    def decrypt(self, data):
        if type(data) == bytes:
            msg = b''
            try:
                for i in range(0, len(data)):
                    msg += bytes([data[i] ^ ord(self.key[i % len(self.key)])])
                return msg.decode(encoding="utf-8")
            except:
                return NULL
        elif type(data) == str:
            msg = ""
            try:
                for i in range(0, len(data)):
                    msg += chr(ord(data[i]) ^ ord(self.key[i % len(self.key)]))
            except:
                msg = NULL
            return msg
        return NULL

    def add_emoji(self, msg):
        emoji_map = self.map_new_emoji()
        pos = msg.find('\x14')
        while (pos != -1):
            lastpos = pos
            num = ord(msg[pos + 1])
            index = emoji_map[str(num)]
            if self.emoji == 1:
                filename = "new/s" + index + ".png"
            else:
                filename = "old/" + index + ".gif"
            msg = msg.replace(
                msg[pos:pos + 2],
                "<img src='./emoticon/" + filename + "' alt=" + index + ">")
            pos = msg.find('\x14')
            if (pos == lastpos):
                break
        return msg

    def message(self):
        # mode=1 friend
        # mode=2 troop
        num = self.qq.encode("utf-8")
        md5num = hashlib.md5(num).hexdigest().upper()
        if (self.mode == 1):
            cmd = "select msgData,senderuin,time from mr_friend_{}_New".format(
                md5num)
            self.get_friends()
        else:
            cmd = "select msgData,senderuin,time from mr_troop_{}_New".format(
                md5num)
            self.get_troop_members()

        cursors = self.fill_cursors(cmd)
        allmsg = []
        for cs in cursors:
            for row in cs:
                msgdata = row[0]
                if (not msgdata):
                    continue
                uin = row[1]
                ltime = time.localtime(row[2])
                sendtime = time.strftime("%Y-%m-%d %H:%M:%S", ltime)

                allmsg.append(
                    [sendtime, self.decrypt(uin), self.decrypt(msgdata)])
        return allmsg

    def get_friends(self):
        cmd = "SELECT uin, remark FROM Friends"
        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                num = self.decrypt(row[0])
                name = self.decrypt(row[1])
                self.num_to_name[num] = name

    def get_troop_members(self):
        cmd = "SELECT troopuin, memberuin, friendnick, troopnick FROM TroopMemberInfo"
        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                if(self.decrypt(row[0]) != self.qq):
                    continue
                num = self.decrypt(row[1])
                name = self.decrypt(row[3]) or self.decrypt(row[2])
                self.num_to_name[num] = name

    def fill_cursors(self, cmd):
        cursors = []
        # slowtable might not contain related message, so just skip it
        try:
            cursors.append(self.c2.execute(cmd))
        except:
            pass
        cursors.append(self.c1.execute(cmd))
        return cursors

    def output(self):
        name1 = "我"
        file = str(self.qq) + ".html"
        f2 = open(file, "w", encoding="utf-8")
        f2.write(
            "<head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head>"
        )
        allmsg = self.message()
        f2.write("<div style='white-space: pre-line'>")
        for msg in allmsg:
            if not msg[2]:
                continue
            try:
                if (msg[1] == str(self.qq_self)):
                    f2.write("<p align='right'>")
                    f2.write("<font color=\"green\">")
                    f2.write(msg[0])
                    f2.write("</font>-----<font color=\"blue\"><b>")
                    f2.write(name1)
                    f2.write("</font></b></br>")
                else:
                    f2.write("<p align='left'>")
                    f2.write("<font color=\"blue\"><b>")
                    f2.write(self.num_to_name.get(msg[1]) or msg[1])
                    f2.write("</b></font>-----<font color=\"green\">")
                    f2.write(msg[0])
                    f2.write("</font></br>")
                f2.write(self.add_emoji(msg[2]))
                f2.write("</br></br>")
                f2.write("</p>")
            except:
                pass
        f2.write("</div>")

    def get_key(self):
        self.unify_path()
        kc_path = os.path.join(self.dir, "files", "kc")
        kc_file = open(kc_path, "r")
        return kc_file.read()

    # unify databases path of different phones
    def unify_path(self):
        if os.path.isdir(os.path.join(self.dir, "f")):
            os.rename(os.path.join(self.dir, "f"),
                      os.path.join(self.dir, "files"))
        if os.path.isdir(os.path.join(self.dir, "db")):
            os.rename(os.path.join(self.dir, "db"),
                      os.path.join(self.dir, "databases"))
        if os.path.isfile(os.path.join(self.dir, "files", "kc")) == False:
            raise OSError(
                "File not found. Please report your directory layout.")

    def map_new_emoji(self):
        with open('./emoticon/face_config.json', encoding='utf-8') as f:
            emojis = json.load(f)
        new_emoji_map = {}

        for e in emojis['sysface']:
            if self.emoji == 1:
                new_emoji_map[e["AQLid"]] = e["QSid"]
            else:
                if(len(e["EMCode"]) == 3):
                    new_emoji_map[e["AQLid"]] = str(int(e["EMCode"])-100)
        return new_emoji_map


def main(dir, qq_self, qq, mode, emoji):
    try:
        q = QQoutput(dir, qq_self, qq, mode, emoji)
        q.output()
    except Exception as e:
        with open('log.txt', 'w') as f:
            f.write(repr(e))
            f.write(traceback.format_exc())

        print(traceback.format_exc())
        if (repr(e).split(":")[0] == "OperationalError('no such table"):
            raise ValueError("信息填入错误")
        else:
            raise BaseException("Error! See log.txt")
