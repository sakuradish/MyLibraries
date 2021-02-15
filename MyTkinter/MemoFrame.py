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
# import datetime
import tkinter as tk
# from tkinter import font
# from tkinter import ttk
# from PIL import Image, ImageTk
# import time
# ===================================================================================
## @brief メモを表示するフレーム
class MemoFrame(tk.Frame):
    @MyLogger.deco
    def __init__(self,master,**kw):
        super().__init__(master,**kw)
        self.memodata = MyDataBase.GetInstance("memo.xlsx")
        self.memodata.DFAppendColumn(['data/project', 'data/task', 'data/memo'])
        self.memodata.AddCallbackOnWrite(self.OnWrite)
        self.Draw()
# ===================================================================================
    @MyLogger.deco
    def Draw(self):
        columns = self.memodata.GetColumns()
        self.labels = WidgetFactory.NewLabel(self, columns, 0,0,1,0.05, "ToRight")
        self.comboboxes = WidgetFactory.NewCombobox(self, columns, 0,0.05,1,0.05, "ToRight")
        for column,widget in self.comboboxes['widgets'].items():
            widget['instance'].SetText('')
            self.memodata.DFRead()
            self.memodata.DFDropDuplicates(column)
            values = self.memodata.GetListByColumn(column)
            widget['instance'].SetValues(values)
        self.memodata.DFRead()
        self.text = WidgetFactory.NewText(self, ['text'], 0,0.1,1,0.9, "ToRight")
        self.text['widgets']['text']['instance'].SetText(self.memodata)
# ===================================================================================
    @MyLogger.deco
    def OnKeyEvent(self, event):
        if event.keysym == 'Return':
            print(WidgetFactory.HasFocus(self.comboboxes['id'] , self.master.focus_get()))
            if WidgetFactory.HasFocus(self.comboboxes['id'] , self.master.focus_get()):
                self.memodata.DFRead()
                columns = self.memodata.GetColumns()
                for column in columns:
                    self.memodata.DFFilter(column, self.comboboxes['widgets'][column]['instance'].GetText())
                self.text['widgets']['text']['instance'].SetText(self.memodata)
# ===================================================================================
    @MyLogger.deco
    def OnWrite(self):
        self.text['widgets']['text']['instance'].SetText(self.memodata)
# ===================================================================================
if __name__ == '__main__':
    root = MyTkRoot()
    memoframe = MemoFrame(root)
    root.AddFrame(memoframe, 'memoframe', key=memoframe.OnKeyEvent)
    root.mainloop()
# ===================================================================================