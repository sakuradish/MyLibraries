# MyDataBase
# できること
- Excelのテーブルを読み込む・書き込む
- 行・列追加
- 列指定の重複行削除
- 列指定のソート
- HTML文字列に変換
- 文字列に変換
- 辞書型に変換
- 毎日初回起動時にExcelをバックアップ

# サンプルコード
```python
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
```
