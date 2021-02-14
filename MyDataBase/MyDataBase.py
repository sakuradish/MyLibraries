# ===================================================================================
import sys
sys.path.append("../MyLogger/")
from MyLogger import mylogger
mylogger = mylogger.GetInstance()
# ===================================================================================
import os
import datetime
import pandas as pd
import shutil
# ===================================================================================
## @brief Excelのデータを管理するクラス
# @note
# 現状列の定義はExcel上でしか行えない
class MyDataBase():
    ## @brief 初期化処理
    @mylogger.deco
    def __init__(self, filename):
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.datapath = self.basedir + "/data/" + filename
        # self.callbacks = []
        self.Initialize()
        self.Backup()
# ===================================================================================
    ## @brief データベース初期化処理
    # @note
    @mylogger.deco
    def Initialize(self):
        # ファイル/フォルダがなければ作成
        if not os.path.exists(os.path.dirname(self.datapath)):
            os.makedirs(os.path.dirname(self.datapath))
        if not os.path.exists(self.datapath):
            pd.DataFrame(columns=['timestamp/date', 'timestamp/time']).to_excel(self.datapath, index=False)
            # pd.DataFrame().to_excel(self.datapath, index=False)
            mylogger.info(self.datapath, ' is initialized')
        # DataFrame読み込み
        self.DFRead()
        # Timestamp用の列がなければ追加してファイル更新
        if not 'timestamp/date' in self.df and not 'timestamp/time' in self.df:
            dt = datetime.datetime.now()
            self.df.insert(0, 'timestamp/date', dt.strftime("%Y/%m/%d"))
            self.df.insert(1, 'timestamp/time', dt.strftime('%X'))
            self.DFWrite()
# ===================================================================================
    # @brief バックアップ処理
    @mylogger.deco
    def Backup(self):
        folder = self.basedir + "/backup/" + str(datetime.date.today()) + "/"
        file = folder + os.path.basename(self.datapath)
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.exists(file):
            shutil.copy2(self.datapath, file)
# ===================================================================================
    ## @brief データフレームをxlsxから読み込み
    @mylogger.deco
    def DFRead(self):
        self.df = pd.read_excel(self.datapath, engine='openpyxl')
# ===================================================================================
    ## @brief データフレームをxlsxに書き込み
    # @note
    @mylogger.deco
    def DFWrite(self):
        self.df.to_excel(self.datapath, index=False)
# ===================================================================================
    ## @brief データフレームから指定列の重複を削除
    # @note
    # keepに'first/last'を設定することで残す行を選択可能
    @mylogger.deco
    def DFDropDuplicates(self, column, keep='last'):
        self.df = self.df.drop_duplicates(subset=[column], keep=keep)
# ===================================================================================
    ## @brief データフレームを指定列で並び替え
    @mylogger.deco
    def DFSort(self, column, ascending=True):
        self.df = self.df.sort_values(by=[column], ascending=ascending)
# ===================================================================================
    ## @brief データフレームに行を追加
    @mylogger.deco
    def DFAppendRow(self, row):
        # サイズが一致しない場合、仮の列名を追加
        while len(row) != len(self.GetColumns()):
            self.DFAppendColumn('UnknownColumn'+str(len(self.df.columns)))
        # 行追加
        dt = datetime.datetime.now()
        temp = {'timestamp/date':dt.strftime("%Y/%m/%d"),
                'timestamp/time':dt.strftime('%X')}
        for k,v in zip(self.GetColumns(), row):
            temp[k] = v
        self.df = self.df.append(temp, ignore_index=True)
# ===================================================================================
    ## @brief データフレームに列を追加
    @mylogger.deco
    def DFAppendColumn(self, column, value=''):
        self.df.insert(len(self.df.columns), column, value)
# ===================================================================================
    ## @brief データフレームを辞書型に変換して取得
    # @note
    # Timestamp用の列を意識しなくていいように削除して渡す。
    @mylogger.deco
    def GetColumns(self):
        return list(self.df.columns)[2:]
# ===================================================================================
    ## @brief データフレームを辞書型に変換して取得
    @mylogger.deco
    def GetDict(self):
        return self.df.to_dict('index')
# ===================================================================================
    ## @brief データフレームを文字列型に変換して取得
    # @note
    # データフレームにto_stringというメソッドがあるが、
    # TAB区切りの方が好みなので自作
    @mylogger.deco
    def GetStr(self):
        ret = ''
        # タイトル行
        isFirstColumn = True
        for column in list(self.df.columns):
            if isFirstColumn:
                ret += column
                isFirstColumn = False
            else:
                ret += '\t' + column
        ret += '\n'
        # データ行
        for row in self.df.to_dict('index').values():
            isFirstColumn = True
            for value in row.values():
                if isFirstColumn:
                    ret += value
                    isFirstColumn = False
                else:
                    ret += '\t' + value
            ret += '\n'
        return ret
# ===================================================================================
    ## @brief データフレームをHTML文字列に変換して取得
    @mylogger.deco
    def GetHTML(self):
        return self.df.to_html(index=False)
# ===================================================================================
if __name__ == '__main__':
    db = MyDataBase('todo.xlsx')
    db.DFAppendRow(['プロジェクトX','洗濯','柔軟剤が少ない'])
    db.DFAppendRow(['プロジェクトX','家事','カレー'])
    db.DFAppendRow(['プロジェクトY','会議','ABC会議室'])
    db.DFAppendRow(['プロジェクトY','営業','DEF株式会社'])
    mylogger.success(db.GetColumns())
    mylogger.success(db.GetDict())
    mylogger.success(db.GetStr())
    mylogger.success(db.GetHTML())
    db.DFSort('memo', ascending=False)
    db.DFDropDuplicates('project')
    db.DFWrite()
    input('press any key ...')
# ===================================================================================