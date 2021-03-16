# ===================================================================================
import sys
sys.path.append("../MyLogger/")
sys.path.append("../MyDataBase/")
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
from MyDataBase import MyDataBase
# ===================================================================================
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinterhtml import HtmlFrame
# ===================================================================================
## @brief Widget生成クラス
class WidgetFactory():
    widgets = {}
    font = ("MSゴシック", "20", "bold")
    # ## @brief 初期化処理
    # def __init__(self):
    #     self.widgets = {}
    #     self.font = ("MSゴシック", "20", "bold")
# ===================================================================================
    # ## @brief インスタンス取得
    # @classmethod
    # def GetInstance(cls):
    #     if not hasattr(cls, "this_"):
    #         cls.this_ = cls()
    #     return cls.this_
# ===================================================================================
    ## @brief ID指定でWidgetsを削除
    @classmethod
    def Destroy(cls, id):
        for key,widget in cls.widgets[id].items():
            widget['instance'].destroy()
        del cls.widgets[id]
# ===================================================================================
    ## @brief ID指定でFocusが当たっているか確認
    @classmethod
    def HasFocus(cls, id, focused):
        MyLogger.sakura(cls.widgets)
        MyLogger.sakura(cls.widgets[id])
        if id in cls.widgets:
            return cls.widgets[id].HasFocus(focused)
        # for key,widget in cls.widgets[id].items():
        #     if widget['instance'].HasFocus(focused):
        #         MyLogger.critical(key)
        #         return key
        return None
# ===================================================================================
    ## @brief キーボードイベント
    # @note
    # 各部品のOnKeyEventをコール
    @classmethod
    def OnKeyEvent(cls, event):
        for id,widgets in cls.widgets.items():
            # MyLogger.sakura(id)
            # MyLogger.sakura(widgets)
            pass
        # fontサイズを変更(別途部品の描画更新の検討が必要)
        if event.keysym == 'plus':
            cls.font = (cls.font[0], str(int(cls.font[1])+1), cls.font[2])
        elif event.keysym == 'minus':
            cls.font = (cls.font[0], str(int(cls.font[1])-1), cls.font[2])
# ===================================================================================
    ## @brief widget管理用のユニークなIDを生成
    @classmethod
    def GetWidgetsId(cls):
        ret_id = 0
        for id in cls.widgets.keys():
            if ret_id <= id:
                ret_id = id + 1
        return ret_id
# ===================================================================================
    ## @brief widgetの配置レイアウトを計算
    @classmethod
    def CalcLayout1D(cls, length, index, x, y, w, h, direction="ToBottom"):
        if direction == "ToBottom":
            relw = w
            relh = h / length
            relx = x
            rely = y + relh * index
        elif direction == "ToRight":
            relw = w / length
            relh = h
            relx = x + relw * index
            rely = y
        return {'relx':relx, 'rely':rely, 'relw':relw, 'relh':relh}
# ===================================================================================
    ## @brief widgetの配置レイアウトを計算
    @classmethod
    def CalcLayout2D(cls, column_length, column_index, row_length, row_index, x, y, w, h):
        relw = w / column_length
        relh = h / row_length
        relx = x + relw * column_index
        rely = y + relh * row_index
        return {'relx':relx, 'rely':rely, 'relw':relw, 'relh':relh}
# ===================================================================================
    ## @brief InputFieldクラス
    @classmethod
    def NewInputField(cls, parent, database, x, y, w, h, direction="ToBottom"):
        instance = cls.InputField(cls, parent, database, x, y, w, h, direction=direction)
        id = cls.GetWidgetsId()
        cls.widgets[id] = instance
        return {'id':id, 'instance':instance}
    ## @brief InputFieldクラス
    class InputField():
        def __init__(self, cls, parent, database, x, y, w, h, direction="ToBottom"):
            self.labels = {}
            self.comboboxes = {}
            columns = database.GetColumns()
            for column in columns:
                length = len(columns)
                index = columns.index(column)
                # widget生成と配置
                font = cls.font
                instance = cls.Label(parent, text=column, font=font)
                coordates = cls.CalcLayout1D(length, index, x, y, w/2, h, direction=direction)
                instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
                self.labels[column] = {'instance':instance}
                # widget生成と配置
                v = tk.StringVar()
                font = cls.font
                instance = cls.Combobox(parent, textvariable=v, font=font)
                instance.SetText("")
                database.DBRead()
                database.DBDropDuplicates(column)
                values = database.GetListByColumn(column)
                instance.SetValues(values)
                coordates = cls.CalcLayout1D(length, index, x+w/2, y, w/2, h, direction=direction)
                instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
                self.comboboxes[column] = {'instance':instance, 'stringvar':v}
        def Destroy(self):
            pass
        def OnKeyEvent(self):
            pass
# ===================================================================================
    ## @brief FilterFieldクラス
    @classmethod
    def NewFilterField(cls, parent, database, x, y, w, h, direction="ToBottom"):
        instance = cls.FilterField(cls, parent, database, x, y, w, h, direction=direction)
        id = cls.GetWidgetsId()
        cls.widgets[id] = instance
        return {'id':id, 'instance':instance}
    ## @brief FilterFieldクラス
    class FilterField():
        def __init__(self, cls, parent, database, x, y, w, h, direction="ToBottom"):
            self.comboboxes = {}
            columns = database.GetColumns()
            for column in columns:
                length = len(columns)
                index = columns.index(column)
                # widget生成と配置
                v = tk.StringVar()
                font = cls.font
                instance = cls.Combobox(parent, textvariable=v, font=font)
                instance.SetText("")
                database.DBRead()
                database.DBDropDuplicates(column)
                values = database.GetListByColumn(column)
                instance.SetValues(values)
                coordates = cls.CalcLayout1D(length, index, x, y, w, h, direction=direction)
                instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
                self.comboboxes[column] = {'instance':instance, 'stringvar':v}
        def Destroy(self):
            pass
        def OnKeyEvent(self):
            pass
# ===================================================================================
    ## @brief ViewerFieldクラス
    @classmethod
    def NewViewerField(cls, parent, database, x, y, w, h):
        instance = cls.ViewerField(cls, parent, database, x, y, w, h)
        id = cls.GetWidgetsId()
        cls.widgets[id] = instance
        return {'id':id, 'instance':instance}
    ## @brief ViewerFieldクラス
    # @note
    # まずは全要素を表示
    class ViewerField():
        def __init__(self, cls, parent, database, x, y, w, h):
            self.uniquecolumns = []
            self.comboboxes = {}
            columns = database.GetColumns()
            rows = database.GetRows()
            for column in columns:
                column_length = len(columns)
                column_index = columns.index(column)
                # filterしたrowが欲しい
                # self.taskdata.DBRead()
                # self.taskdata.DBDropDuplicates('data/task')
                # for column,widget in self.filterfield['combobox']['widgets'].items():
                #     self.taskdata.DBFilter(column, widget['instance'].GetText())
                # rows = self.taskdata.GetRows()
                for row in rows:
                    row_length = len(rows)
                    row_index = rows.index(row)
                    # widget生成と配置
                    v = tk.StringVar()
                    font = cls.font
                    instance = cls.Combobox(parent, textvariable=v, font=font)
                    # instance.SetText("")
                    instance.SetText(column + str(row))
                    database.DBRead()
                    database.DBDropDuplicates(column)
                    values = database.GetListByColumn(column)
                    instance.SetValues(values)
                    coordates = cls.CalcLayout2D(column_length, column_index, row_length, row_index, x, y, w, h)
                    instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
                    if not row in self.comboboxes:
                        self.comboboxes[row] = {}
                    if not column in self.comboboxes[row]:
                        self.comboboxes[row][column] = {}
                    self.comboboxes[row][column] = {'instance':instance, 'stringvar':v}
        def SetUniqueColumn(column):
            self.uniquecolumns.append(column)
            # self.taskdata.DBDropDuplicates('data/task')
        def LinkFilterField(field):
            pass
        def Destroy(self):
            pass
        def OnKeyEvent(self):
            pass
# ===================================================================================
    ## @brief MultiComboboxクラス
    @classmethod
    def NewMultiCombobox(cls, parent, name_list, x, y, w, h, direction="ToBottom"):
        instance = cls.MultiCombobox(cls, parent, name_list, x, y, w, h, direction=direction)
        id = cls.GetWidgetsId()
        cls.widgets[id] = instance
        return {'id':id, 'instance':instance}
    ## @brief MultiComboboxクラス
    class MultiCombobox():
        def __init__(self, cls, parent, name_list, x, y, w, h, direction="ToBottom"):
            self.comboboxes = {}
            for name in name_list:
                length = len(name_list)
                index = name_list.index(name)
                # widget生成と配置
                v = tk.StringVar()
                font = cls.font
                instance = cls.Combobox(parent, textvariable=v, font=font)
                instance.SetText("")
                coordates = cls.CalcLayout1D(length, index, x, y, w, h, direction=direction)
                instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
                self.comboboxes[name] = {'instance':instance, 'stringvar':v}
        def Destroy(self):
            pass
        def OnKeyEvent(self):
            pass
        def HasFocus(self, focused):
            for key,widget in self.comboboxes.items():
                MyLogger.sakura(key,widget)
                if widget['instance'] == focused:
                    return key
            return None
# ===================================================================================
    ## @brief Comboboxクラス
    class Combobox(ttk.Combobox):
        def __init__(self,master,**kw):
            super().__init__(master,**kw)
        def SetValues(self, values):
            self.configure(values=values)
        def SetText(self, text):
            self.set(text)
        def GetText(self):
            return self.get()
# ===================================================================================
    ## @brief Labelクラス
    class Label(tk.Label):
        def __init__(self,master,**kw):
            super().__init__(master,**kw)
        def SetText(self, text):
            self['text'] = text
        def GetText(self):
            return self['text']
# ===================================================================================
    # ## @brief HTMLFrame生成
    # @classmethod
    # def NewHTMLFrame(cls, parent, name_list, x, y, w, h, direction="ToBottom"):
    #     id = cls.GetWidgetsId()
    #     ret = {'id':id, 'widgets':{}}
    #     # cls.widgets[id] = []
    #     cls.widgets[id] = {}
    #     length = len(name_list)
    #     for name in name_list:
    #         index = name_list.index(name)
    #         # widget生成と配置
    #         instance = cls.HTMLFrame(parent)
    #         coordates = cls.CalcLayout1D(length, index, x, y, w, h, direction=direction)
    #         instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
    #         ret['widgets'][name] = {'instance':instance, 'coordates':coordates}
    #         # widget保存
    #         # cls.widgets[id].append(instance)
    #         cls.widgets[id][name] = {'instance':instance, 'coordates':coordates}
    #     return ret
    ## @brief HTMLFrameクラス
    # class HTMLFrame(HtmlFrame):
    #     def __init__(self,master):
    #         super().__init__(master)
    #     def SetHTML(self, html):
    #         self.set_content(html)
# ===================================================================================
    ## @brief Text生成
    @classmethod
    def NewText(cls, parent, name_list, x, y, w, h, direction="ToBottom"):
        id = cls.GetWidgetsId()
        ret = {'id':id, 'widgets':{}}
        # cls.widgets[id] = []
        cls.widgets[id] = {}
        length = len(name_list)
        for name in name_list:
            index = name_list.index(name)
            # widget生成と配置
            font = cls.font
            instance = cls.Text(parent,wrap=tk.CHAR,undo=True, bg='black',font=font, foreground='white', insertbackground='white')
            x_sb = tk.Scrollbar(parent,orient='horizontal')
            y_sb = tk.Scrollbar(parent,orient='vertical')
            x_sb.config(command=instance.xview)
            y_sb.config(command=instance.yview)
            instance.config(xscrollcommand=x_sb.set,yscrollcommand=y_sb.set)
            w -= 0.03
            h -= 0.03
            coordates = cls.CalcLayout1D(length, index, x, y, w, h, direction=direction)
            instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
            x_sb.place(relx=coordates['relx'], rely=coordates['rely']+coordates['relh'], relwidth=coordates['relw'], relheight=0.03)
            y_sb.place(relx=coordates['relx']+coordates['relw'], rely=coordates['rely'], relwidth=0.03, relheight=coordates['relh'])
            ret['widgets'][name] = {'instance':instance, 'coordates':coordates}
            # widget保存
            # cls.widgets[id].append(instance)
            cls.widgets[id][name] = {'instance':instance, 'coordates':coordates}
        return ret
    ## @brief Textクラス
    class Text(tk.Text):
        def __init__(self,master,**kw):
            super().__init__(master,**kw)
        def SetText(self, database):
            self.configure(state='normal')
            self.delete('1.0','end')
            # 文字色設定
            cnt = 1
            for column in database.GetColumns():
                R = ((33 * cnt) - 1) / 1000000
                G = ((33 * cnt) - 1) / 10000
                B = ((33 * cnt) - 1) / 100
                color = '#' + ('00'+str(R))[-2:] + ('00'+str(G))[-2:] + ('00'+str(B))[-2:]
                MyLogger.critical(color)
                self.tag_config(column, background=color)
                cnt += 1
            # 文字列設定
            for row in database.GetDict().values():
                for column in database.GetColumns():
                    text = row[column]
                    self.insert('end',  text + "\t", column)
                self.insert('end', "\n")
            # 文字色設定
            self.see('end')
            # self.configure(state='disabled')
# ===================================================================================
if __name__ == '__main__':
    def main():
        from MyTkRoot import MyTkRoot
        root = MyTkRoot()
        frame = tk.Frame(root)
        root.AddFrame(frame, 'FactoryWidget')
        # widget1 = WidgetFactory.NewCombobox(frame, ['a','b'], 0,0,1,1)
        # widget2 = WidgetFactory.NewLabel(frame, ['a','b'], 0,0,1,1)
        # WidgetFactory.Destroy(widget1['id'])
        # WidgetFactory.Destroy(widget2['id'])
        # widget3 = WidgetFactory.NewCombobox(frame, ['column1','column2','column3','column4','column5'], 0.3,0.1,0.8,0.6)
        # widget3['widgets']['column1']['instance'].SetValues(['column1','column2','column3','column4','column5'])
        widget3 = WidgetFactory.NewInputField(frame, MyDataBase('task.xlsx'), 0.3,0.1,0.8,0.6)
        # widget3['widgets']['column1']['instance'].SetValues(['column1','column2','column3','column4','column5'])
        widget4 = WidgetFactory.NewLabel(frame, ['column1','column2','column3','column4','column5'], 0.1,0.1,0.2,0.6)
        widget5 = WidgetFactory.NewHTMLFrame(frame, ['htmlframe'], 0,0.8,1,0.1, "ToRight")
        widget5['widgets']['htmlframe']['instance'].SetHTML(MyDataBase('task.xlsx').GetHTML())
        widget6 = WidgetFactory.NewText(frame, ['text'], 0,0.9,1,0.1, "ToRight")
        widget6['widgets']['text']['instance'].SetText(MyDataBase('task.xlsx'))
        root.mainloop()
    main()
# ===================================================================================