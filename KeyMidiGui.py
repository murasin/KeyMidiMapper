#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import tkinter
import tkinter.ttk as ttk
from tkinter import messagebox as tkMessageBox
from tkinter import filedialog as tkFileDialog

class mainGui():
    def __init__(self):
        pass

    def setup(self, ports, midiout):
        self.root=tkinter.Tk()
        self.root.geometry("400x300")
        #self.root.withdraw() #ルートウインドウは非表示にしてダイアログボックスのみ出したいとき
        self.root.title(u"Key2MidiMapper")
        #self.root.iconbitmap(default="MidiKeyMapper.ico")
        self.root.resizable(width=False, height=False) #最大化禁止 

        # ツリービューの作成
        frame_t = tkinter.Frame(self.root, bd=2, relief="ridge")
        frame_t.pack(fill="x",side="top", padx="10", pady="10")
        
        self.tree = ttk.Treeview(frame_t, selectmode="browse", height=8 ,padding=10)
        self.tree["columns"] = (1,2,3)
        self.tree["show"] = "headings"
        self.tree.column(1,width=25)
        self.tree.column(2,width=200)
        self.tree.column(3,width=75)
        self.tree.heading(1,text="id")
        self.tree.heading(2,text="port")
        self.tree.heading(3,text="status")

        # ツリービューのスタイル変更
        style = ttk.Style()
        # TreeViewの全部に対して、フォントサイズの変更
        style.configure("Treeview",font=("",12))
        # TreeViewのHeading部分に対して、フォントサイズの変更と太字の設定
        style.configure("Treeview.Heading",font=("",12,"bold"))

        for i in range(len(ports)):
            data = (i+1, ports[i][:-2], "")
            self.tree.insert("","end", tags = i, values=data)
        # ツリービューの配置
        self.tree.pack(fill="x",side="top",padx=5,pady=5)
        
        frame_b = tkinter.Frame(self.root,bd=2,relief="flat")
        frame_b.pack(fill="x")
        button1 = tkinter.Button(frame_b,text="切断", command=lambda:self.disconnect(midiout))
        button1.pack(side="right", padx="5", pady="5", ipadx='15')
        button2 = tkinter.Button(frame_b,text="接続", command=lambda:self.connect(midiout))
        button2.pack(side="right" ,padx="5", pady="5", ipadx='15')
        return

    def connect(self, midiout):
        selected_items = self.tree.selection()
        if not selected_items:
            # Itemが選択されていない
            return

        if(midiout.is_port_open()):
            midiout.close_port()
        tree_items = self.tree.get_children()
        for item in tree_items:
            self.tree.set(item, 3, "")

        # SelectModeがBrowseなので、複数選択を考慮しない
        values = self.tree.item(selected_items[0])["values"][0]
        midiout.open_port( values - 1 )
        self.tree.set(selected_items[0], 3, "connecting")

        return

    def disconnect(self, midiout):

        if(midiout.is_port_open()):
            midiout.close_port()
        tree_items = self.tree.get_children()
        for item in tree_items:
            self.tree.set(item, 3, "")

        return

    def getFilePass(self):
        fTyp=[('テキストファイル', '*.csv')]
        #複数のタイプを指定することも可能。

        iDir=os.getcwd()  #iDir='c:/' #Windows

        #askopenfilename 一つのファイルを選択する。
        filename = tkFileDialog.askopenfilename(filetypes=fTyp,initialdir=iDir) 
        #tkMessageBox.showinfo('FILE NAME is ...',filename)

        #askopenfilenames 複数ファイルを選択する。
        # filenames=filedialog.askopenfilenames(filetypes=fTyp,initialdir=iDir) 
        # for f in filenames:
        #     tkMessageBox.showinfo('FILE NAME is ...',f)
        #askdirectory ディレクトリを選択する。
        # dirname=tkFileDialog.askdirectory(initialdir=iDir)
        # tkMessageBox.showinfo('SELECTED DIRECROTY is ...',dirname)
        return filename

    def run(self):
        self.root.mainloop()
        return