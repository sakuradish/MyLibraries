# MyLogger
# できること
- 色付きのログ出力
- @mylogger.decoを使用して、関数の開始/終了のログを出力
- @mylogger.decomemoを使用して、関数の開始/終了のログを出力＋メモリ使用率を表示
- localhost:8000にアクセスすることで、スクリーンショットとログ出力をスマホから確認可能
# サンプルコード
```python
if __name__ == '__main__':
    mylogger = mylogger.GetInstance('DEBUG')
    mylogger.StartBrowserLogging()
    @mylogger.decomemo
    def test():
        mylogger.critical('This is CRITICAL. (50)')
        mylogger.error('This is ERROR. (40)')
        mylogger.success('This is SUCCESS. (35)')
        mylogger.warning('This is WARNING. (30)')
        mylogger.notice('This is NOTICE. (25)')
        mylogger.info('This is INFO. (20)')
        mylogger.verbose('This is VERBOSE. (15)')
        mylogger.debug('This is DEBUG. (10)')
        mylogger.spam('This is SPAM. (5)')
    test()
```