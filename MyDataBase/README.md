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
```