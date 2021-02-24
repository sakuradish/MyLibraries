# ===================================================================================
import sys
sys.path.append("../MyLogger/")
# sys.path.append("../MyDataBase/")
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
# MyLogger.StartBrowserLogging()
# from MyDataBase import MyDataBase
from MyTkRoot import MyTkRoot
# from WidgetFactory import WidgetFactory
from TaskFrame import TaskFrame
from MemoFrame import MemoFrame
from AttendanceFrame import AttendanceFrame
from ExplorerFrame import ExplorerFrame
# ===================================================================================
if __name__ == '__main__':
    root = MyTkRoot()
    taskframe = TaskFrame(root)
    root.AddFrame(taskframe, 'taskframe', key=taskframe.OnKeyEvent)
    memoframe = MemoFrame(root)
    root.AddFrame(memoframe, 'memoframe', key=memoframe.OnKeyEvent)
    attendanceframe = AttendanceFrame(root)
    root.AddFrame(attendanceframe, 'attendanceframe', key=attendanceframe.OnKeyEvent)
    explorerframe = ExplorerFrame(root)
    root.AddFrame(explorerframe, 'explorerframe', key=explorerframe.OnKeyEvent)
    root.mainloop()
# ===================================================================================