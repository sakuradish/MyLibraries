# ===================================================================================
import sys
sys.path.append("../MyLogger/")
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
# ===================================================================================
import os
import datetime
import pandas as pd
import shutil
# ===================================================================================
## @brief Excelのデータを管理するクラス
# @note
# 未だに読み込み時と書き込み時のタイプ指定がちゃんとできていない気がするので要改善。
class MyDataBase():
    ## @brief 初期化処理
    @MyLogger.deco
    def __init__(self, filename):
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.datapath = self.basedir + "/data/" + filename
        self.df = None
        self.dict = {}
        self.columns = []
        self.rows = []
        self.OnWriteCallback = []
        self.DBInitialize()
        self.DBBackup()
# ===================================================================================
    ## @brief インスタンス取得
    # @note
    # ファイルごとにインスタンスを生成する
    @classmethod
    @MyLogger.deco
    def GetInstance(cls, filename):
        if not hasattr(cls, 'this_'):
            cls.this_ = {}
        if not filename in cls.this_:
            cls.this_[filename] = cls(filename=filename)
        return cls.this_[filename]
# ===================================================================================
    ## @brief データベース初期化処理
    # @note
    @MyLogger.deco
    def DBInitialize(self):
        # ファイル/フォルダがなければ作成
        if not os.path.exists(os.path.dirname(self.datapath)):
            os.makedirs(os.path.dirname(self.datapath))
        if not os.path.exists(self.datapath):
            pd.DataFrame(columns=['timestamp/date', 'timestamp/time']).to_excel(self.datapath, index=False)
            # pd.DataFrame().to_excel(self.datapath, index=False)
            MyLogger.info(self.datapath, ' is initialized')
        # DataFrame読み込み
        self.DBRead()
        # Timestamp用の列がなければ追加してファイル更新
        if not 'timestamp/date' in self.df and not 'timestamp/time' in self.df:
            dt = datetime.datetime.now()
            self.df.insert(0, 'timestamp/date', dt.strftime("%Y/%m/%d"))
            self.df.insert(1, 'timestamp/time', dt.strftime('%X'))
            self.DBWrite()
# ===================================================================================
    # @brief バックアップ処理
    @MyLogger.deco
    def DBBackup(self):
        folder = self.basedir + "/backup/" + str(datetime.date.today()) + "/"
        file = folder + os.path.basename(self.datapath)
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.exists(file):
            shutil.copy2(self.datapath, file)
# ===================================================================================
    ## @brief データフレームをxlsxから読み込み
    @MyLogger.deco
    def DBRead(self):
        self.df = pd.read_excel(self.datapath, engine='openpyxl', dtype='object')
        self.OnDataFrameUpdate()
# ===================================================================================
    ## @brief データフレームを辞書データから読み込み
    @MyLogger.deco
    def DBImportDict(self, arg_dict):
        self.df = pd.DataFrame.from_dict(arg_dict, orient='index', dtype="object")
        self.DBWrite()
# ===================================================================================
    ## @brief データフレームをxlsxに書き込み
    @MyLogger.deco
    def DBWrite(self):
        self.df.to_excel(self.datapath, index=False)
        self.OnWrite()
# ===================================================================================
    ## @brief データフレームから指定列の重複を削除
    # @note
    # keepに'first/last'を設定することで残す行を選択可能
    @MyLogger.deco
    def DBDropDuplicates(self, column, keep='last'):
        self.df.drop_duplicates(subset=[column], keep=keep, inplace=True)
        self.OnDataFrameUpdate()
# ===================================================================================
    ## @brief データフレームを指定列で並び替え
    @MyLogger.deco
    def DBSort(self, column, ascending=True):
        self.df.sort_values(by=[column], ascending=ascending, inplace=True)
        self.OnDataFrameUpdate()
# ===================================================================================
    ## @brief データフレームを指定列と値でフィルタ
    @MyLogger.deco
    def DBFilter(self, column, value, mode='contains'):
        if mode=='contains':
            self.df = self.df[self.df[column].astype(str).str.contains(value)]
        else: #if mode='fullmatch':
            self.df = self.df[self.df[column].astype(str).str.fullmatch(value)]
        self.OnDataFrameUpdate()
# ===================================================================================
    ## @brief データフレームに行を追加
    # @note
    # DataFrameのappendが遅いので、辞書を引数に渡した場合は辞書を更新する
    @MyLogger.deco
    def DBAppendRow(self, row, arg_dict=None):
        # サイズが一致しない場合、仮の列名を追加
        while len(row) > len(self.columns):
            self.DBAppendColumn(['Column'+str(len(self.df.columns))])
        # 行追加
        dt = datetime.datetime.now()
        temp = {'timestamp/date':dt.strftime("%Y/%m/%d"),
                'timestamp/time':dt.strftime('%X')}
        for k,v in zip(self.columns, row):
            temp[k] = v
        if arg_dict != None:
            arg_dict[len(arg_dict)] = temp
            return arg_dict
        else:
            self.df = self.df.append(temp, ignore_index=True)
            self.OnDataFrameUpdate()
# ===================================================================================
    ## @brief データフレームに列を追加
    @MyLogger.deco
    def DBAppendColumn(self, columns, value=''):
        for column in columns:
            if not column in self.df.columns:
                self.df.insert(len(self.df.columns), column, value)
            else:
                MyLogger.warning('column ', column, ' is already exist')
        self.OnDataFrameUpdate()
        self.DBWrite()
# ===================================================================================
    ## @brief 指定列だけ取り出し
    @MyLogger.deco
    def GetListByColumn(self, column):
        return self.df.loc[:,column].values.tolist()
# ===================================================================================
    ## @brief データフレーム列ラベルを取得
    # @note
    # Timestamp用の列を意識しなくていいように削除して渡す。
    @MyLogger.deco
    def GetColumns(self):
        return self.columns
# ===================================================================================
    ## @brief データフレーム行indexを取得
    @MyLogger.deco
    def GetRows(self):
        return self.rows
# ===================================================================================
    ## @brief データフレームを辞書型に変換して取得
    @MyLogger.deco
    def GetDict(self):
        return self.dict
# ===================================================================================
    ## @brief データフレームを文字列型に変換して取得
    # @note
    # データフレームにto_stringというメソッドがあるが、
    # TAB区切りの方が好みなので自作
    @MyLogger.deco
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
                value = str(value)
                if isFirstColumn:
                    ret += value
                    isFirstColumn = False
                else:
                    ret += '\t' + value
            ret += '\n'
        return ret
# ===================================================================================
    ## @brief データフレームをHTML文字列に変換して取得
    @MyLogger.deco
    def GetHTML(self):
        return self.df.to_html(index=False)
# ===================================================================================
    ## @brief Excel更新時のコールバック登録
    @MyLogger.deco
    def AddCallbackOnWrite(self, callback):
        self.OnWriteCallback.append(callback)
# ===================================================================================
    ## @brief データフレームの内容を属性に反映
    @MyLogger.deco
    def OnDataFrameUpdate(self):
        self.columns = list(self.df.columns)[2:]
        self.rows = list(self.df.index)
        self.dict = self.df.to_dict('index')
# ===================================================================================
    ## @brief Excel更新時のコールバック呼び出し
    @MyLogger.deco
    def OnWrite(self):
        for callback in self.OnWriteCallback:
            callback()
# ===================================================================================
if __name__ == '__main__':
    @MyLogger.deco
    def main():
        db = MyDataBase.GetInstance('MyDataBaseSample.xlsx')
        db.DBAppendColumn(['data/column1', 'data/column2', 'data/column3'])
        MyLogger.SetFraction(100)
        dict = db.GetDict()
        for i in range(100):
            MyLogger.SetNumerator(i)
            db.DBAppendRow([str(i),str(i),str(i)], dict)
        db.DBImportDict(dict)
        MyLogger.success(db.GetColumns())
        MyLogger.success(db.GetDict())
        MyLogger.success(db.GetStr())
        MyLogger.success(db.GetHTML())
        db.DBSort('data/column3', ascending=False)
        db.DBDropDuplicates('data/column3')
        db.DBWrite()
    main()
    input('press any key ...')
# ===================================================================================