# ===================================================================================
import sys
sys.path.append("../MyLogger/")
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
from WidgetFactory import WidgetFactory
# ===================================================================================
import tkinter as tk
import math
# ===================================================================================
## @brief Frameを自動的にリサイズして配置するクラス
# @note
# 描画されていないFrameも裏で動いてる実装になっていると思うので、
# 時間があるときにリファクタしたい
class MyTkRoot(tk.Tk):
    ## @brief 初期化処理
    @MyLogger.deco
    def __init__(self, **kw):
        super().__init__(**kw)
        self.frames = {}
        self.idtable = {}
        self.isKeyEventProcessing = False
        self.isMouseEventProcessing = False
        self.bind("<Control-Key>", self.OnKeyEvent)
        self.bind("<Button>", self.OnMouseEvent)
        self.__DrawCanvas()
# ===================================================================================
    ## @brief 背面のCanvasを描画
    @MyLogger.deco
    def __DrawCanvas(self):
        import pyautogui
        width,height = pyautogui.size()
        self.canvas = tk.Canvas(self, bg="lightblue", width=width, height=height)
        self.canvas.place(relx=0, rely=0.1, relheight=0.9, relwidth=1)
# ===================================================================================
    ## @brief フレームを登録
    @MyLogger.deco
    def AddFrame(self, frame, id, key=None, mouse=None):
        length = len(self.frames)
        # トグルボタン配置
        button = tk.Button(self, text=id)
        button.bind("<Button-1>", self.__OnToggleButtonPressed)
        button.bind("<Return>", self.__OnToggleButtonPressed)
        button.place(relx=length*0.1, rely=0, relheight=0.1, relwidth=0.1)
        # フレーム登録
        self.idtable[length] = id
        if length == 0:
            self.frames[id] = {'frame':frame, 'visibility':True, 'button':button, 'OnKeyEvent':key, 'OnMouseEvent':mouse}
            self.frames[id]['button'].configure(bg='blue')
        else:
            self.frames[id] = {'frame':frame, 'visibility':False, 'button':button, 'OnKeyEvent':key, 'OnMouseEvent':mouse}
            self.frames[id]['button'].configure(bg='gray')
        self.__DrawFrames()
# ===================================================================================
    ## @brief フレームを描画
    @MyLogger.deco
    def __DrawFrames(self):
        # 表示状態のFrameのみ抽出
        visibleFrames = []
        for frame in self.frames.values():
            if frame['visibility'] == True:
                visibleFrames.append(frame['frame'])
            else:
                frame['frame'].place_forget()
        if visibleFrames == []:
            return
        # 行数,列数などを算出
        num = 1
        while num * num < len(visibleFrames):
            num += 1
        rowmax = math.ceil(len(visibleFrames) / num)
        colmax = num
        # Frameを配置
        padding = 0.02
        relwidth = (1-(padding*colmax)) / colmax
        relheight = (0.9-(padding*rowmax)) / rowmax
        for row in range(rowmax):
            for col in range(colmax):
                index = row*colmax+col
                relx = (col*relwidth)+(padding*col)+(padding/2)
                rely = (0.1+row*relheight)+(padding*row)+(padding/2)
                if len(visibleFrames) > index:
                    visibleFrames[index].place(relx=relx,rely=rely,relwidth=relwidth,relheight=relheight)
# ===================================================================================
    ## @brief トグルボタン押下時の処理
    @MyLogger.deco
    def __OnToggleButtonPressed(self, event):
        self.__ToggleFrameVisibility(event.widget["text"])
# ===================================================================================
    ## @brief Frameの表示状態をトグルさせる
    @MyLogger.deco
    def __ToggleFrameVisibility(self, id):
        if self.frames[id]['visibility'] != True:
            self.frames[id]['visibility'] = True
            self.frames[id]['button'].configure(bg='blue')
        else:
            self.frames[id]['visibility'] = False
            self.frames[id]['button'].configure(bg='gray')
        self.__DrawFrames()
# ===================================================================================
    ## @brief キーボードイベント受け取り時の処理
    @MyLogger.deco
    def OnKeyEvent(self, event):
        MyLogger.info(event)
        # Ctrl+数字ならフレームの表示をトグル
        if event.keysym.isdecimal() and len(self.idtable) > int(event.keysym)-1:
            self.__ToggleFrameVisibility(self.idtable[int(event.keysym)-1])
        # Widgetにキーボードイベントを送る
        WidgetFactory.OnKeyEvent(event)
        # 登録されているコールバックを呼び出す
        if self.isKeyEventProcessing == False:
            self.isKeyEventProcessing = True
            for frame in self.frames.values():
                if frame['OnKeyEvent']:
                    frame['OnKeyEvent'](event)
            self.isKeyEventProcessing = False
# ===================================================================================
    ## @brief マウスイベント受け取り時の処理
    @MyLogger.deco
    def OnMouseEvent(self, event):
        MyLogger.info(event)
        # 登録されているコールバックを呼び出す
        if self.isMouseEventProcessing == False:
            self.isMouseEventProcessing = True
            for frame in self.frames.values():
                if frame['OnMouseEvent']:
                    frame['OnMouseEvent'](event)
            self.isMouseEventProcessing = False
# ===================================================================================
    ## @brief 背景画像設定
    @MyLogger.deco
    def SetImage(self, path=""):
        import os
        if not os.path.exists(path):
            from PIL import Image
            import pyautogui
            self.img = Image.open(path)
            self.img = self.img.resize(pyautogui.size())
        else:
            import pyautogui
            self.img = pyautogui.screenshot()
            self.img.mode = 'RGBA'
        from PIL import ImageTk
        self.img = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)
        self.__DrawFrames()
# ===================================================================================
if __name__ == '__main__':
    root = MyTkRoot()
    frame1 = tk.Frame(root, bg='#000000')
    frame2 = tk.Frame(root, bg='#0000ff')
    frame3 = tk.Frame(root, bg='#00ff00')
    frame4 = tk.Frame(root, bg='#00ffff')
    frame5 = tk.Frame(root, bg='#ff0000')
    frame6 = tk.Frame(root, bg='#ff00ff')
    frame7 = tk.Frame(root, bg='#ffff00')
    frame8 = tk.Frame(root, bg='#ffffff')
    root.AddFrame(frame1, '#000000')
    root.AddFrame(frame2, '#0000ff')
    root.AddFrame(frame3, '#00ff00')
    root.AddFrame(frame4, '#00ffff')
    root.AddFrame(frame5, '#ff0000')
    root.AddFrame(frame6, '#ff00ff')
    root.AddFrame(frame7, '#ffff00')
    root.AddFrame(frame8, '#ffffff')
    root.mainloop()
# ===================================================================================