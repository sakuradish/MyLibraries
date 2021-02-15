# ===================================================================================
import sys
sys.path.append("../MyLogger/")
sys.path.append("../MyDataBase/")
from MyLogger import mylogger
mylogger = mylogger.GetInstance()
from MyDataBase import MyDataBase
from MyTkRoot import MyTkRoot
from WidgetFactory import WidgetFactory
# ===================================================================================
import tkinter as tk
# ===================================================================================
## @brief メモを表示するフレーム
class TaskFrame(tk.Frame):
    @mylogger.deco
    def __init__(self,master,**kw):
        super().__init__(master,**kw)
        self.taskdata = MyDataBase("task.xlsx")
        self.taskdata.DFAppendColumn(['data/project', 'data/task', 'data/status'])
        self.memodata = MyDataBase("memo.xlsx")
        self.memodata.DFAppendColumn(['data/project', 'data/task', 'data/memo'])
        self.inputfield = {}
        self.filterfield = {}
        self.viewerfield = {}
        self.memofield = {}
        self.InitializeStaticWidget()
        self.InitializeDynamicWidget()
        self.Draw()
# ===================================================================================
    @mylogger.deco
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
    @mylogger.deco
    def InitializeDynamicWidget(self):
        # viewerfield
        if 'project' in self.viewerfield:
            WidgetFactory.Destroy(self.viewerfield['project']['id'])
        if 'task' in self.viewerfield:
            WidgetFactory.Destroy(self.viewerfield['task']['id'])
        if 'status' in self.viewerfield:
            WidgetFactory.Destroy(self.viewerfield['status']['id'])
        self.taskdata.DFRead()
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.taskdata.DFFilter(column, widget['instance'].GetText())
        rows = list(range(len(self.taskdata.GetDict())))
        self.viewerfield['project'] = WidgetFactory.NewLabel(self, rows, 0,0.35,0.2,0.65, "ToBottom")
        self.viewerfield['task'] = WidgetFactory.NewLabel(self, rows, 0.2,0.35,0.4,0.65, "ToBottom")
        self.viewerfield['status'] = WidgetFactory.NewCombobox(self, rows, 0.6,0.35,0.2,0.65, "ToBottom")
        # memofield
        if 'combobox' in self.memofield:
            WidgetFactory.Destroy(self.memofield['combobox']['id'])
        self.taskdata.DFRead()
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.taskdata.DFFilter(column, widget['instance'].GetText())
        rows = list(range(len(self.taskdata.GetDict())))
        self.memofield['combobox'] = WidgetFactory.NewCombobox(self, rows, 0.8,0.35,0.2,0.65, "ToBottom")
# ===================================================================================
    @mylogger.deco
    def Draw(self):
        # inputfield
        columns = self.taskdata.GetColumns()
        for column,widget in self.inputfield['combobox']['widgets'].items():
            self.taskdata.DFRead()
            self.taskdata.DFDropDuplicates(column)
            values = self.taskdata.GetListByColumn(column)
            widget['instance'].SetValues(values)
        # filterfield
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.taskdata.DFRead()
            self.taskdata.DFDropDuplicates(column)
            values = self.taskdata.GetListByColumn(column)
            widget['instance'].SetValues(values)
        # viewerfield
        self.taskdata.DFRead()
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.taskdata.DFFilter(column, widget['instance'].GetText())
        for row,widget in self.viewerfield['project']['widgets'].items():
            values = self.taskdata.GetListByColumn(columns[0])
            widget['instance'].SetText(values[row])
        for row,widget in self.viewerfield['task']['widgets'].items():
            values = self.taskdata.GetListByColumn(columns[1])
            widget['instance'].SetText(values[row])
        for row,widget in self.viewerfield['status']['widgets'].items():
            values = self.taskdata.GetListByColumn(columns[2])
            widget['instance'].SetText(values[row])
        for row,widget in self.viewerfield['status']['widgets'].items():
            self.taskdata.DFDropDuplicates(columns[2])
            widget['instance'].SetValues(self.taskdata.GetListByColumn(columns[2]))
        # memofield
        for row,widget in self.memofield['combobox']['widgets'].items():
            widget['instance'].SetText('')
# ===================================================================================
    @mylogger.deco
    def OnKeyEvent(self, event):
        if event.keysym == 'Return':
            if WidgetFactory.HasFocus(self.inputfield['combobox']['id'] , self.master.focus_get()):
                data = []
                for column,widget in self.inputfield['combobox']['widgets'].items():
                    data.append(widget['instance'].GetText())
                self.taskdata.DFRead()
                self.taskdata.DFAppendRow(data)
                self.taskdata.DFWrite()
                self.InitializeDynamicWidget()
                self.Draw()
            if WidgetFactory.HasFocus(self.filterfield['combobox']['id'] , self.master.focus_get()):
                self.InitializeDynamicWidget()
                self.Draw()
            focused = WidgetFactory.HasFocus(self.memofield['combobox']['id'] , self.master.focus_get())
            if focused != None:
                project = self.viewerfield['project']['widgets'][focused]['instance'].GetText()
                task = self.viewerfield['task']['widgets'][focused]['instance'].GetText()
                memo = self.memofield['combobox']['widgets'][focused]['instance'].GetText()
                mylogger.critical(project,task,memo)
                self.memodata.DFRead()
                self.memodata.DFAppendRow([project,task,memo])
                self.memodata.DFWrite()
                self.InitializeDynamicWidget()
                self.Draw()
# ===================================================================================
if __name__ == '__main__':
    root = MyTkRoot()
    memoframe = TaskFrame(root)
    root.AddFrame(memoframe, 'memoframe', key=memoframe.OnKeyEvent)
    root.mainloop()
# ===================================================================================