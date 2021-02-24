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
class AttendanceFrame(tk.Frame):
    @MyLogger.deco
    def __init__(self,master,**kw):
        super().__init__(master,**kw)
        self.attendancedata = MyDataBase.GetInstance("attendance.xlsx")
        self.attendancedata.DBAppendColumn(['year', 'month', 'date', 'weekday', 'plan/type', 'plan/start', 'plan/end', 'actual/type', 'actual/start', 'actual/end'])
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
        columns = self.attendancedata.GetColumns()
        self.inputfield['label'] = WidgetFactory.NewLabel(self, columns, 0,0,0.3,0.3, "ToBottom")
        self.inputfield['combobox'] = WidgetFactory.NewCombobox(self, columns, 0.3,0,0.7,0.3, "ToBottom")
        for column,widget in self.inputfield['combobox']['widgets'].items():
            widget['instance'].SetText('')
        # filterfield
        if 'combobox' in self.filterfield:
            WidgetFactory.Destroy(self.filterfield['combobox']['id'])
        self.filterfield['combobox'] = WidgetFactory.NewCombobox(self, columns, 0,0.3,1,0.05, "ToRight")
        for column,widget in self.filterfield['combobox']['widgets'].items():
            widget['instance'].SetText('')
# ===================================================================================
    @MyLogger.deco
    def InitializeDynamicWidget(self):
        # viewerfield
        columns = self.attendancedata.GetColumns()
        for column in columns:
            if column in self.viewerfield:
                WidgetFactory.Destroy(self.viewerfield[column]['id'])
        self.attendancedata.DBRead()
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.attendancedata.DBFilter(column, widget['instance'].GetText())
        rows = self.attendancedata.GetRows()
        self.viewerfield['year'] = WidgetFactory.NewLabel(self, rows, 0,0.35,0.05,0.65, "ToBottom")
        self.viewerfield['month'] = WidgetFactory.NewLabel(self, rows, 0.05,0.35,0.05,0.65, "ToBottom")
        self.viewerfield['date'] = WidgetFactory.NewLabel(self, rows, 0.1,0.35,0.05,0.65, "ToBottom")
        self.viewerfield['weekday'] = WidgetFactory.NewLabel(self, rows, 0.15,0.35,0.05,0.65, "ToBottom")
        self.viewerfield['plan/type'] = WidgetFactory.NewCombobox(self, rows, 0.2,0.35,0.2,0.65, "ToBottom")
        self.viewerfield['plan/start'] = WidgetFactory.NewCombobox(self, rows, 0.4,0.35,0.1,0.65, "ToBottom")
        self.viewerfield['plan/end'] = WidgetFactory.NewCombobox(self, rows, 0.5,0.35,0.1,0.65, "ToBottom")
        self.viewerfield['actual/type'] = WidgetFactory.NewCombobox(self, rows, 0.6,0.35,0.2,0.65, "ToBottom")
        self.viewerfield['actual/start'] = WidgetFactory.NewCombobox(self, rows, 0.8,0.35,0.1,0.65, "ToBottom")
        self.viewerfield['actual/end'] = WidgetFactory.NewCombobox(self, rows, 0.9,0.35,0.1,0.65, "ToBottom")
# ===================================================================================
    @MyLogger.deco
    def Draw(self):
        # inputfield
        columns = self.attendancedata.GetColumns()
        for column,widget in self.inputfield['combobox']['widgets'].items():
            self.attendancedata.DBRead()
            self.attendancedata.DBDropDuplicates(column)
            values = self.attendancedata.GetListByColumn(column)
            widget['instance'].SetValues(values)
        # filterfield
        for column,widget in self.filterfield['combobox']['widgets'].items():
            self.attendancedata.DBRead()
            self.attendancedata.DBDropDuplicates(column)
            values = self.attendancedata.GetListByColumn(column)
            widget['instance'].SetValues(values)
        # viewerfield
        self.attendancedata.DBRead()
        for column in columns:
            values = self.attendancedata.GetListByColumn(column)
            for row,widget in self.viewerfield[column]['widgets'].items():
                widget['instance'].SetText(values[row])
# ===================================================================================
    @MyLogger.deco
    def OnKeyEvent(self, event):
        if event.keysym == 'Return':
            if WidgetFactory.HasFocus(self.inputfield['combobox']['id'] , self.master.focus_get()):
                data = []
                for column,widget in self.inputfield['combobox']['widgets'].items():
                    data.append(widget['instance'].GetText())
                self.attendancedata.DBRead()
                self.attendancedata.DBAppendRow(data)
                self.attendancedata.DBWrite()
                # 入力欄空にしたい
                # InitializeStaticWidget呼ぶとfilterも空になっちゃうので仮実装
                for column,widget in self.inputfield['combobox']['widgets'].items():
                    widget['instance'].SetText('')
                self.InitializeDynamicWidget()
                self.Draw()
            if WidgetFactory.HasFocus(self.filterfield['combobox']['id'] , self.master.focus_get()):
                self.InitializeDynamicWidget()
                self.Draw()
            # focused = WidgetFactory.HasFocus(self.viewerfield['data/status']['id'] , self.master.focus_get())
            # if focused != None:
            #     project = self.viewerfield['data/project']['widgets'][focused]['instance'].GetText()
            #     task = self.viewerfield['data/task']['widgets'][focused]['instance'].GetText()
            #     status = self.viewerfield['data/status']['widgets'][focused]['instance'].GetText()
            #     MyLogger.critical(project,task,status)
            #     self.attendancedata.DBRead()
            #     self.attendancedata.DBAppendRow([project,task,status])
            #     self.attendancedata.DBWrite()
            #     self.InitializeDynamicWidget()
            #     self.Draw()
# ===================================================================================
if __name__ == '__main__':
    root = MyTkRoot()
    memoframe = AttendanceFrame(root)
    root.AddFrame(memoframe, 'memoframe', key=memoframe.OnKeyEvent)
    root.mainloop()
# ===================================================================================