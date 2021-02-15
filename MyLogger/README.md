# MyLogger
# できること
- 色付きのログ出力
- @MyLogger.decoを使用して、関数の開始/終了のログを出力
- @MyLogger.decomemoを使用して、関数の開始/終了のログを出力＋メモリ使用率を表示
- localhost:8000にアクセスすることで、スクリーンショットとログ出力をスマホから確認可能
# サンプルコード
```python
if __name__ == '__main__':
    MyLogger = MyLogger.GetInstance('DEBUG')
    MyLogger.StartBrowserLogging()
    @MyLogger.deco
    def test():
        MyLogger.SetFraction(10)
        for i in range(10):
            MyLogger.SetNumerator(i)
            MyLogger.success('logging with progress')
        MyLogger.ResetProgress()
        MyLogger.critical('This is CRITICAL. (50)')
        MyLogger.error('This is ERROR. (40)')
        MyLogger.success('This is SUCCESS. (35)')
        MyLogger.warning('This is WARNING. (30)')
        MyLogger.notice('This is NOTICE. (25)')
        MyLogger.info('This is INFO. (20)')
        MyLogger.verbose('This is VERBOSE. (15)')
        MyLogger.debug('This is DEBUG. (10)')
        MyLogger.spam('This is SPAM. (5)')
    test()
```