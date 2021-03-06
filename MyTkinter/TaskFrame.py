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
        if 'label' in self.inputfield:
            WidgetFactory.Destroy(self.inputfield['label']['id'])
        if 'combobox' in self.inputfield:
            WidgetFactory.Destroy(self.inputfield['combobox']['id'])
        columns = self.taskdata.GetColumns()
        self.inputfield['label'] = WidgetFactory.NewLabel(self, columns, 0,0,0.3,0.3, "ToBottom")
        self.inputfield['combobox'] = WidgetFactory.NewCombobox(self, columns, 0.3,0,0.7,0.3, "ToBottom")
        for column,widget in self.inputfield['combobox']['widgets'].items():
            widget['instance'].SetText('')
        # filterfield
        if 'combobox' in self.filterfield:
            WidgetFactory.Destroy(self.filterfield['combobox']['id'])
        self.filterfield['combobox'] = WidgetFactory.NewCombobox(self, columns, 0,0.3,0.8,0.05, "ToRight")
        for column,widget in self.filterfield['combobox']['widgets'].items():
            widget['instance'].SetText('')
# ===================================================================================
    @MyLogger.deco
    def InitializeDynamicWidget(self):
        # viewerfield
        if 'data/project' in self.viewerfield:
            WidgetFactory.Destroy(self.viewerfield['data/project']['id'])
        if 'data/task' in self.viewerfield:
            WidgetFactory.Destroy(self.viewerfield['data/task']['id'])
        if 'data/status' in self.viewerfield:
            WidgetFactory.Destroy(self.viewerfield['data/status']['id'])
        self.taskdata.DBRead()
        self.taskdata.DBDropDuplicates('data/task')
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.taskdata.DBFilter(column, widget['instance'].GetText())
        rows = self.taskdata.GetRows()
        self.viewerfield['data/project'] = WidgetFactory.NewLabel(self, rows, 0,0.35,0.2,0.65, "ToBottom")
        self.viewerfield['data/task'] = WidgetFactory.NewLabel(self, rows, 0.2,0.35,0.4,0.65, "ToBottom")
        self.viewerfield['data/status'] = WidgetFactory.NewCombobox(self, rows, 0.6,0.35,0.2,0.65, "ToBottom")
        # memofield
        if 'combobox' in self.memofield:
            WidgetFactory.Destroy(self.memofield['combobox']['id'])
        self.taskdata.DBRead()
        self.taskdata.DBDropDuplicates('data/task')
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.taskdata.DBFilter(column, widget['instance'].GetText())
        rows = self.taskdata.GetRows()
        self.memofield['combobox'] = WidgetFactory.NewCombobox(self, rows, 0.8,0.35,0.2,0.65, "ToBottom")
# ===================================================================================
    @MyLogger.deco
    def Draw(self):
        # inputfield
        columns = self.taskdata.GetColumns()
        for column,widget in self.inputfield['combobox']['widgets'].items():
            self.taskdata.DBRead()
            self.taskdata.DBDropDuplicates(column)
            values = self.taskdata.GetListByColumn(column)
            widget['instance'].SetValues(values)
        # filterfield
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.taskdata.DBRead()
            self.taskdata.DBDropDuplicates(column)
            values = self.taskdata.GetListByColumn(column)
            widget['instance'].SetValues(values)
        # viewerfield
        self.taskdata.DBRead()
        for column in columns:
            values = self.taskdata.GetListByColumn(column)
            for row,widget in self.viewerfield[column]['widgets'].items():
                widget['instance'].SetText(values[row])
        self.taskdata.DBDropDuplicates(columns[2])
        for row,widget in self.viewerfield['data/status']['widgets'].items():
            widget['instance'].SetValues(self.taskdata.GetListByColumn(columns[2]))
        # memofield
        for row,widget in self.memofield['combobox']['widgets'].items():
            widget['instance'].SetText('')
# ===================================================================================
    @MyLogger.deco
    def OnKeyEvent(self, event):
        if event.keysym == 'Return':
            if WidgetFactory.HasFocus(self.inputfield['combobox']['id'] , self.master.focus_get()):
                data = []
                for column,widget in self.inputfield['combobox']['widgets'].items():
                    data.append(widget['instance'].GetText())
                self.taskdata.DBRead()
                self.taskdata.DBAppendRow(data)
                self.taskdata.DBWrite()
                # 入力欄空にしたい
                # InitializeStaticWidget呼ぶとfilterも空になっちゃうので仮実装
                for column,widget in self.inputfield['combobox']['widgets'].items():
                    widget['instance'].SetText('')
                self.InitializeDynamicWidget()
                self.Draw()
            if WidgetFactory.HasFocus(self.filterfield['combobox']['id'] , self.master.focus_get()):
                self.InitializeDynamicWidget()
                self.Draw()
            focused = WidgetFactory.HasFocus(self.viewerfield['data/status']['id'] , self.master.focus_get())
            if focused != None:
                project = self.viewerfield['data/project']['widgets'][focused]['instance'].GetText()
                task = self.viewerfield['data/task']['widgets'][focused]['instance'].GetText()
                status = self.viewerfield['data/status']['widgets'][focused]['instance'].GetText()
                MyLogger.critical(project,task,status)
                self.taskdata.DBRead()
                self.taskdata.DBAppendRow([project,task,status])
                self.taskdata.DBWrite()
                self.InitializeDynamicWidget()
                self.Draw()
            focused = WidgetFactory.HasFocus(self.memofield['combobox']['id'] , self.master.focus_get())
            if focused != None:
                project = self.viewerfield['data/project']['widgets'][focused]['instance'].GetText()
                task = self.viewerfield['data/task']['widgets'][focused]['instance'].GetText()
                memo = self.memofield['combobox']['widgets'][focused]['instance'].GetText()
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