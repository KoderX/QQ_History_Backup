import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from icon import ico, github_mark
import base64
import QQ_History
import os
import webbrowser


def Enter():
    db, qq, key, msg, n1, n2 = e1.get(), e2.get(), e3.get(), e4.get(), e5.get(
    ), e6.get()
    group = 1 if e7.get() == '私聊' else 2
    if (db == "" or qq == "" or (key == "" and msg == "")):
        info.set("信息不完整！")
        return ()
    info.set("开始导出")
    try:
        realkey = QQ_History.main(db, qq, key, msg, n1, n2, group)
    except Exception as e:
        info.set(repr(e))
        return ()
    if (key == ""):
        keyGet.set(realkey)
    info.set("完成")


def SelectPath():
    pathTmp = filedialog.askopenfilename()
    pathGet.set(pathTmp)


def url():
    webbrowser.open_new("https://github.com/Yiyiyimu/QQ_History_Backup")


root = tk.Tk()
pathGet, keyGet, info = tk.StringVar(), tk.StringVar(), tk.StringVar()

tmp = open("tmp.ico", "wb+")
tmp.write(base64.b64decode(ico))
tmp.close()
root.iconbitmap("tmp.ico")
os.remove("tmp.ico")

root.title("QQ聊天记录导出")

ttk.Label(root, text="*db文件地址：").grid(row=0, column=0, sticky="e")
e1 = ttk.Entry(root, textvariable=pathGet)
e1.grid(row=0, column=1)
ttk.Button(root, text="选择", command=SelectPath, width=5).grid(row=0, column=3)

ttk.Label(root, text="*对方QQ号：").grid(row=1, column=0, sticky="e")
e2 = ttk.Entry(root)
e2.grid(row=1, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="手机识别码：").grid(row=2, column=0, sticky="e")
e3 = ttk.Entry(root, textvariable=keyGet)
e3.grid(row=2, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="最后一次聊天记录\n（至少六个汉字）").grid(row=3, column=0, sticky="e")
e4 = ttk.Entry(root)
e4.grid(row=3, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="我的名字：").grid(row=4, column=0, sticky="e")
e5 = ttk.Entry(root)
e5.grid(row=4, column=1, columnspan=3, sticky="ew", pady=3)
ttk.Label(root, text="对方名字：").grid(row=5, column=0, sticky="e")
e6 = ttk.Entry(root)
e6.grid(row=5, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="私聊/群聊：").grid(row=6, column=0, sticky="e")
e7 = ttk.Combobox(root)
e7['values'] = ('私聊', '群聊')
e7.current(0)
e7.grid(row=6, column=1, columnspan=3, sticky="ew", pady=3)

root.grid_columnconfigure(2, weight=1)

ttk.Button(root, text="确认", command=Enter).grid(row=7, column=1)
l1 = ttk.Label(root, textvariable=info)
l1.grid(row=7, column=1)

tmp = open("tmp.png", "wb+")
tmp.write(base64.b64decode(github_mark))
tmp.close()
github = tk.PhotoImage(file='tmp.png')
os.remove("tmp.png")

button_img = tk.Button(root, image=github, text='b', command=url, bd=0)
button_img.grid(row=6, rowspan=7, column=0, sticky="ws")

root.mainloop()

## pyinstaller -F -w -i icon.ico GUI.py
