# ===================================================================================
import sys
sys.path.append("../MyLogger/")
sys.path.append("../MyDataBase/")
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
from MyDataBase import MyDataBase
from MyTkRoot import MyTkRoot
from WidgetFactory import WidgetFactory
# ===================================================================================
import tkinter as tk
import glob
import os
# ===================================================================================
class ExplorerFrame(tk.Frame):
    @MyLogger.deco
    def __init__(self,master, cnf={},**kw):
        super().__init__(master,cnf,**kw)
        # self.explorerdata = MyDataBase("../data/explorer.txt", ['base', 'path', 'update', 'size'])
        self.InitializeStaticWidget()
        self.PlaceStaticWidget()
        self.UpdateStaticWidgetProperty()
# ===================================================================================
    @MyLogger.deco
    def InitializeStaticWidget(self):
        # text
        self.text = WidgetFactory.NewText(self, ['text'], 0,0.1,1,0.9, "ToRight")
        # self.text['widgets']['text']['instance'].SetText(self.explorerdata)
# ===================================================================================
    @MyLogger.deco
    def PlaceStaticWidget(self):
        pass
# ===================================================================================
    @MyLogger.deco
    def UpdateStaticWidgetProperty(self, event=None):
        pass
        # # text
        # self.text.configure(state='normal')
        # self.text.configure(undo=False)
        # self.text.delete('1.0','end')
        # for record in self.explorerdata.GetAllRecords(filter={'path':self.cb2.get()}):
        #     self.text.insert('end', self.explorerdata.ConvertRecordToString(record) + "\n")
        # self.text.see('end')
        # self.text.configure(state='disabled')
        # # combobox1
        # records = self.explorerdata.GetAllRecordsByColumn('base')
        # records = [record['data']['base'] for record in records]
        # records = list(dict.fromkeys(records))
        # self.cb1.configure(values=records)
        # # combobox2
        # records = self.explorerdata.GetAllRecordsByColumn('base')
        # records = [record['data']['base'] for record in records]
        # records = list(dict.fromkeys(records))
        # self.cb2.configure(values=records)
# ===================================================================================
    @MyLogger.deco
    def __Glob(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            os.system("start " + path)
            basedirs = [path]
            donecnt = 0
            remaincnt = len(basedirs)
            while 1:
                if not basedirs:
                    break
                basedir = basedirs.pop(0)
                progress = "[" + str(donecnt) + "/" + str(remaincnt) + "]"
                try:
                    files = [file for file in glob.glob(basedir + "/*", recursive=False) if os.path.isfile(file)]
                    dirs = [dir for dir in glob.glob(basedir + "/*", recursive=False) if os.path.isdir(dir)]
                    basedirs += dirs
                    for file in files:
                        print(progress + file)
                        update = datetime.datetime.fromtimestamp(os.stat(file).st_mtime)
                        update = update.strftime('%Y/%m/%d')
                        size = str(os.stat(file).st_size)
                        self.explorerdata.InsertRecordWithLogInfo([self.cb1.get(), file, update, size])
                except:
                    update = datetime.datetime.fromtimestamp(os.stat(basedir).st_mtime)
                    update = update.strftime('%Y/%m/%d')
                    size = str(os.stat(basedir).st_size)
                    self.explorerdata.InsertRecordWithLogInfo([self.cb1.get(), basedir, update, size])
                    print(basedir+" can not glob for some error")
                donecnt += 1
                remaincnt += len(basedirs)
# ===================================================================================
    @MyLogger.deco
    def OnKeyEvent(self, event):
        if event.keysym == 'Return':
            if self.cb1 == self.master.focus_get() and self.cb1.get() != "":
                self.__Glob(self.cb1.get())
                self.UpdateStaticWidgetProperty()
            elif self.cb2 == self.master.focus_get():
                self.UpdateStaticWidgetProperty()
# ===================================================================================
if __name__ == '__main__':
    root = MyTkRoot()
    explorerframe = ExplorerFrame(root)
    root.AddFrame(explorerframe, 'explorerframe', key=explorerframe.OnKeyEvent)
    root.mainloop()
# ===================================================================================