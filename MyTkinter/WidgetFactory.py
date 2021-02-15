# ===================================================================================
import sys
sys.path.append("../MyLogger/")
sys.path.append("../MyDataBase/")
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
from MyDataBase import MyDataBase
from MyTkRoot import MyTkRoot
# ===================================================================================
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinterhtml import HtmlFrame
# ===================================================================================
## @brief Widget生成クラス
class WidgetFactory():
    ## @brief 初期化処理
    def __init__(self):
        self.widgets = {}
# ===================================================================================
    ## @brief インスタンス取得
    @classmethod
    def GetInstance(cls):
        if not hasattr(cls, "this_"):
            cls.this_ = cls()
        return cls.this_
# ===================================================================================
    ## @brief ID指定でWidgetsを削除
    @classmethod
    def Destroy(cls, id):
        for key,widget in cls.GetInstance().widgets[id].items():
            widget['instance'].destroy()
        del cls.GetInstance().widgets[id]
# ===================================================================================
    ## @brief ID指定でFocusが当たっているか確認
    @classmethod
    def HasFocus(cls, id, focused):
        for key,widget in cls.GetInstance().widgets[id].items():
            if widget['instance'] == focused:
                MyLogger.critical(key)
                return key
        return None
# ===================================================================================
    ## @brief widget管理用のユニークなIDを生成
    @classmethod
    def GetWidgetsId(cls):
        ret_id = 0
        for id in cls.GetInstance().widgets.keys():
            if ret_id <= id:
                ret_id = id + 1
        return ret_id
# ===================================================================================
    ## @brief widgetの配置レイアウトを計算
    @classmethod
    def CalcLayout(self, length, index, x, y, w, h, direction="ToBottom"):
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
    ## @brief Combobox生成
    @classmethod
    def NewCombobox(cls, parent, name_list, x, y, w, h, direction="ToBottom"):
        id = cls.GetWidgetsId()
        ret = {'id':id, 'widgets':{}}
        # cls.GetInstance().widgets[id] = []
        cls.GetInstance().widgets[id] = {}
        length = len(name_list)
        for name in name_list:
            index = name_list.index(name)
            # widget生成と配置
            v = tk.StringVar()
            instance = cls.Combobox(parent, textvariable=v)
            instance.SetText(name)
            coordates = cls.CalcLayout(length, index, x, y, w, h, direction=direction)
            instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
            ret['widgets'][name] = {'instance':instance, 'stringvar':v, 'coordates':coordates}
            # widget保存
            # cls.GetInstance().widgets[id].append(instance)
            cls.GetInstance().widgets[id][name] = {'instance':instance, 'stringvar':v, 'coordates':coordates}
        return ret
# ===================================================================================
    ## @brief Label生成
    @classmethod
    def NewLabel(cls, parent, name_list, x, y, w, h, direction="ToBottom"):
        id = cls.GetWidgetsId()
        ret = {'id':id, 'widgets':{}}
        # cls.GetInstance().widgets[id] = []
        cls.GetInstance().widgets[id] = {}
        length = len(name_list)
        for name in name_list:
            index = name_list.index(name)
            # widget生成と配置
            instance = cls.Label(parent, text=name)
            # instance.SetText(name)
            coordates = cls.CalcLayout(length, index, x, y, w, h, direction=direction)
            instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
            ret['widgets'][name] = {'instance':instance, 'coordates':coordates}
            # widget保存
            # cls.GetInstance().widgets[id].append(instance)
            cls.GetInstance().widgets[id][name] = {'instance':instance, 'coordates':coordates}
        return ret
# ===================================================================================
    ## @brief HTMLFrame生成
    @classmethod
    def NewHTMLFrame(cls, parent, name_list, x, y, w, h, direction="ToBottom"):
        id = cls.GetWidgetsId()
        ret = {'id':id, 'widgets':{}}
        # cls.GetInstance().widgets[id] = []
        cls.GetInstance().widgets[id] = {}
        length = len(name_list)
        for name in name_list:
            index = name_list.index(name)
            # widget生成と配置
            instance = cls.HTMLFrame(parent)
            coordates = cls.CalcLayout(length, index, x, y, w, h, direction=direction)
            instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
            ret['widgets'][name] = {'instance':instance, 'coordates':coordates}
            # widget保存
            # cls.GetInstance().widgets[id].append(instance)
            cls.GetInstance().widgets[id][name] = {'instance':instance, 'coordates':coordates}
        return ret
# ===================================================================================
    ## @brief Text生成
    @classmethod
    def NewText(cls, parent, name_list, x, y, w, h, direction="ToBottom"):
        id = cls.GetWidgetsId()
        ret = {'id':id, 'widgets':{}}
        # cls.GetInstance().widgets[id] = []
        cls.GetInstance().widgets[id] = {}
        length = len(name_list)
        for name in name_list:
            index = name_list.index(name)
            # widget生成と配置
            my_font = font.Font(parent,family=u'ＭＳ ゴシック',size=10)
            instance = cls.Text(parent,wrap=tk.CHAR,undo=True, bg='black',font=my_font, foreground='white', insertbackground='white')
            x_sb = tk.Scrollbar(parent,orient='horizontal')
            y_sb = tk.Scrollbar(parent,orient='vertical')
            x_sb.config(command=instance.xview)
            y_sb.config(command=instance.yview)
            instance.config(xscrollcommand=x_sb.set,yscrollcommand=y_sb.set)
            w -= 0.03
            h -= 0.03
            coordates = cls.CalcLayout(length, index, x, y, w, h, direction=direction)
            instance.place(relx=coordates['relx'], rely=coordates['rely'], relwidth=coordates['relw'], relheight=coordates['relh'])
            x_sb.place(relx=coordates['relx'], rely=coordates['rely']+coordates['relh'], relwidth=coordates['relw'], relheight=0.03)
            y_sb.place(relx=coordates['relx']+coordates['relw'], rely=coordates['rely'], relwidth=0.03, relheight=coordates['relh'])
            ret['widgets'][name] = {'instance':instance, 'coordates':coordates}
            # widget保存
            # cls.GetInstance().widgets[id].append(instance)
            cls.GetInstance().widgets[id][name] = {'instance':instance, 'coordates':coordates}
        return ret
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
    ## @brief HTMLFrameクラス
    class HTMLFrame(HtmlFrame):
        def __init__(self,master):
            super().__init__(master)
        def SetHTML(self, html):
            self.set_content(html)
# ===================================================================================
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
    root = MyTkRoot()
    frame = tk.Frame(root)
    root.AddFrame(frame, 'FactoryWidget')
    widget1 = WidgetFactory.NewCombobox(frame, ['a','b'], 0,0,1,1)
    widget2 = WidgetFactory.NewLabel(frame, ['a','b'], 0,0,1,1)
    WidgetFactory.Destroy(widget1['id'])
    WidgetFactory.Destroy(widget2['id'])
    widget3 = WidgetFactory.NewCombobox(frame, ['column1','column2','column3','column4','column5'], 0.3,0.1,0.8,0.6)
    widget3['widgets']['column1']['instance'].SetValues(['column1','column2','column3','column4','column5'])
    widget4 = WidgetFactory.NewLabel(frame, ['column1','column2','column3','column4','column5'], 0.1,0.1,0.2,0.6)
    widget5 = WidgetFactory.NewHTMLFrame(frame, ['htmlframe'], 0,0.8,1,0.1, "ToRight")
    widget5['widgets']['htmlframe']['instance'].SetHTML(MyDataBase('task.xlsx').GetHTML())
    widget6 = WidgetFactory.NewText(frame, ['text'], 0,0.9,1,0.1, "ToRight")
    widget6['widgets']['text']['instance'].SetText(MyDataBase('task.xlsx'))
    root.mainloop()
# ===================================================================================