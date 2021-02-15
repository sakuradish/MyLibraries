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
    db = MyDataBase('task.xlsx')
    db.DFAppendColumn(['project', 'task', 'status'])
    db.DFAppendRow(['プロジェクトX','洗濯','OPEN'])
    db.DFAppendRow(['プロジェクトX','家事','DOING'])
    db.DFAppendRow(['プロジェクトY','会議','DONE'])
    db.DFAppendRow(['プロジェクトY','営業','OPEN'])
    mylogger.success(db.GetColumns())
    mylogger.success(db.GetDict())
    mylogger.success(db.GetStr())
    mylogger.success(db.GetHTML())
    db.DFSort('status', ascending=False)
    db.DFDropDuplicates('project')
    db.DFWrite()
```
