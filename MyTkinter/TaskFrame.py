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
# ===================================================================================
## @brief メモを表示するフレーム
class TaskFrame(tk.Frame):
    @MyLogger.deco
    def __init__(self,master,**kw):
        super().__init__(master,**kw)
        self.taskdata = MyDataBase.GetInstance("task.xlsx")
        self.taskdata.DBAppendColumn(['data/project', 'data/task', 'data/status'])
        self.memodata = MyDataBase.GetInstance("memo.xlsx")
        self.memodata.DBAppendColumn(['data/project', 'data/task', 'data/memo'])
        self.inputfield = {}
        self.filterfield = {}
        self.viewerfield = {}
        self.memofield = {}
        self.InitializeStaticWidget()
        self.InitializeDynamicWidget()
        self.Draw()
# ===================================================================================
    @MyLogger.deco
    def InitializeStaticWidget(self):
        # inputfield
        if 'id' in self.inputfield:
            WidgetFactory.Destroy(self.inputfield['id'])
        self.inputfield = WidgetFactory.NewInputField(self, self.taskdata, 0,0,1,0.3)
        # filterfield
        if 'id' in self.filterfield:
            WidgetFactory.Destroy(self.filterfield['id'])
        self.filterfield = WidgetFactory.NewFilterField(self, self.taskdata, 0,0.3,0.8,0.05, "ToRight")
# ===================================================================================
    @MyLogger.deco
    def InitializeDynamicWidget(self):
        # viewerfield
        if 'id' in self.viewerfield:
            WidgetFactory.Destroy(self.viewerfield['id'])
        self.viewerfield = WidgetFactory.NewViewerField(self, self.taskdata, 0,0.35,0.8,0.65)
        # memofield
        if 'id' in self.memofield:
            WidgetFactory.Destroy(self.memofield['id'])
        self.taskdata.DBRead()
        self.taskdata.DBDropDuplicates('data/task')
        for column,widget in self.filterfield['instance'].comboboxes.items():
            self.taskdata.DBFilter(column, widget['instance'].GetText())
        rows = self.taskdata.GetRows()
        self.memofield = WidgetFactory.NewMultiCombobox(self, rows, 0.8,0.35,0.2,0.65, "ToBottom")
# ===================================================================================
    @MyLogger.deco
    def Draw(self):
        pass
# ===================================================================================
    @MyLogger.deco
    def OnKeyEvent(self, event):
        if event.keysym == 'Return':
            # if WidgetFactory.HasFocus(self.inputfield['combobox']['id'] , self.master.focus_get()):
            #     data = []
            #     for column,widget in self.inputfield['combobox']['widgets'].items():
            #         data.append(widget['instance'].GetText())
            #     self.taskdata.DBRead()
            #     self.taskdata.DBAppendRow(data)
            #     self.taskdata.DBWrite()
            #     # 入力欄空にしたい
            #     # InitializeStaticWidget呼ぶとfilterも空になっちゃうので仮実装
            #     for column,widget in self.inputfield['combobox']['widgets'].items():
            #         widget['instance'].SetText('')
            #     self.InitializeDynamicWidget()
            #     self.Draw()
            # if WidgetFactory.HasFocus(self.filterfield['combobox']['id'] , self.master.focus_get()):
            #     self.InitializeDynamicWidget()
            #     self.Draw()
            # focused = WidgetFactory.HasFocus(self.viewerfield['data/status']['id'] , self.master.focus_get())
            # if focused != None:
            #     project = self.viewerfield['data/project']['widgets'][focused]['instance'].GetText()
            #     task = self.viewerfield['data/task']['widgets'][focused]['instance'].GetText()
            #     status = self.viewerfield['data/status']['widgets'][focused]['instance'].GetText()
            #     MyLogger.critical(project,task,status)
            #     self.taskdata.DBRead()
            #     self.taskdata.DBAppendRow([project,task,status])
            #     self.taskdata.DBWrite()
            #     self.InitializeDynamicWidget()
            #     self.Draw()
            
            if (focused := WidgetFactory.HasFocus(self.memofield['id'] , self.master.focus_get())):
                project = self.viewerfield['instance'].comboboxes[focused]['data/project']['instance'].GetText()
                task = self.viewerfield['instance'].comboboxes[focused]['data/task']['instance'].GetText()
                memo = self.memofield['instance'].comboboxes[focused]['instance'].GetText()
                MyLogger.critical(project,task,memo)
                self.memodata.DBRead()
                self.memodata.DBAppendRow([project,task,memo])
                self.memodata.DBWrite()
                # self.InitializeDynamicWidget()
                self.Draw()
# ===================================================================================
if __name__ == '__main__':
    root = MyTkRoot()
    memoframe = TaskFrame(root)
    root.AddFrame(memoframe, 'memoframe', key=memoframe.OnKeyEvent)
    root.mainloop()
# ===================================================================================