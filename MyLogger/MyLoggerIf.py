################################################################################
from MyLogger import MyLogger
import os
################################################################################
## @brief BrowserLogging開始
# @note
# スレッド化しようと思ったけど、Errorが出たので後回し
# 雑にos.systemからpythonを起動
def StartBrowserLogging():
    basedir = os.path.dirname(os.path.abspath(__file__))
    import subprocess
    proc = subprocess.Popen('python ' + basedir + '/BrowserLogging/BrowserLogging.py', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # os.system('python ' + basedir + '/BrowserLogging/BrowserLogging.py')
    # os.system('start ' + basedir + '/BrowserLogging/BrowserLogging.py')
    info('start BrowserLogging')
################################################################################
## @brief インスタンス取得
def isElapsed(second):
    return MyLogger.GetInstance().isElapsed(second)
################################################################################
## @brief インスタンス取得
def getElapsedTime():
    return MyLogger.GetInstance().getElapsedTime()
################################################################################
## @brief インスタンス取得
def setLogLevel(level='DEBUG'):
    MyLogger.GetInstance().setLogLevel(level)
################################################################################
## @brief 開始ログと終了ログを出力するDecorator
def showTrace(func):
    return MyLogger.GetInstance().showTrace(func)
################################################################################
## @brief 開始ログと終了ログを出力するDecorator(memory_profile付き)
def showTraceAndProfile(func):
    return MyLogger.GetInstance().showTraceAndProfile(func)
################################################################################
## @brief 進捗率登録
def setProgress(numerator, fraction):
    MyLogger.GetInstance().setProgress(numerator, fraction)
################################################################################
## @brief sakuraレベルログ
def sakura(*args, **kwargs):
    MyLogger.GetInstance().printLog("SAKURA", *args, **kwargs)
################################################################################
## @brief criticalレベルログ
def critical(*args, **kwargs):
    MyLogger.GetInstance().printLog("CRITICAL", *args, **kwargs)
################################################################################
## @brief errorレベルログ
def error(*args, **kwargs):
    MyLogger.GetInstance().printLog("ERROR", *args, **kwargs)
################################################################################
## @brief successレベルログ
def success(*args, **kwargs):
    MyLogger.GetInstance().printLog("SUCCESS", *args, **kwargs)
################################################################################
## @brief warningレベルログ
def warning(*args, **kwargs):
    MyLogger.GetInstance().printLog("WARNING", *args, **kwargs)
################################################################################
## @brief noticeレベルログ
def notice(*args, **kwargs):
    MyLogger.GetInstance().printLog("NOTICE", *args, **kwargs)
################################################################################
## @brief infoレベルログ
def info(*args, **kwargs):
    MyLogger.GetInstance().printLog("INFO", *args, **kwargs)
################################################################################
## @brief verboseレベルログ
def verbose(*args, **kwargs):
    MyLogger.GetInstance().printLog("VERBOSE", *args, **kwargs)
################################################################################
## @brief debugレベルログ
def debug(*args, **kwargs):
    MyLogger.GetInstance().printLog("DEBUG", *args, **kwargs)
################################################################################
## @brief spamレベルログ
def spam(*args, **kwargs):
    MyLogger.GetInstance().printLog("SPAM", *args, **kwargs)
################################################################################
## @brief sakuraレベルログ
def SAKURA(*args, **kwargs):
    MyLogger.GetInstance().printLog("SAKURA", *args, **kwargs)
################################################################################
## @brief criticalレベルログ
def CRITICAL(*args, **kwargs):
    MyLogger.GetInstance().printLog("CRITICAL", *args, **kwargs)
################################################################################
## @brief errorレベルログ
def ERROR(*args, **kwargs):
    MyLogger.GetInstance().printLog("ERROR", *args, **kwargs)
################################################################################
## @brief successレベルログ
def SUCCESS(*args, **kwargs):
    MyLogger.GetInstance().printLog("SUCCESS", *args, **kwargs)
################################################################################
## @brief warningレベルログ
def WARNING(*args, **kwargs):
    MyLogger.GetInstance().printLog("WARNING", *args, **kwargs)
################################################################################
## @brief noticeレベルログ
def NOTICE(*args, **kwargs):
    MyLogger.GetInstance().printLog("NOTICE", *args, **kwargs)
################################################################################
## @brief infoレベルログ
def INFO(*args, **kwargs):
    MyLogger.GetInstance().printLog("INFO", *args, **kwargs)
################################################################################
## @brief verboseレベルログ
def VERBOSE(*args, **kwargs):
    MyLogger.GetInstance().printLog("VERBOSE", *args, **kwargs)
################################################################################
## @brief debugレベルログ
def DEBUG(*args, **kwargs):
    MyLogger.GetInstance().printLog("DEBUG", *args, **kwargs)
################################################################################
## @brief spamレベルログ
def SPAM(*args, **kwargs):
    MyLogger.GetInstance().printLog("SPAM", *args, **kwargs)
################################################################################
## @brief sleep
def sleep(second):
    MyLogger.GetInstance().sleep(second)
################################################################################
if __name__ == '__main__':
    setLogLevel("spam")
    @showTraceAndProfile
    def test3():
        while not isElapsed(10):
            sleep(3)
    @showTrace
    def test2():
        for i in range(10):
            setProgress(i, 10)
            success('logging with progress')
        test3()
    @showTrace
    def test1():
        sakura('This is SAKURA. (99)')
        critical('This is CRITICAL. (50)')
        error('This is ERROR. (40)')
        success('This is SUCCESS. (35)')
        warning('This is WARNING. (30)')
        notice('This is NOTICE. (25)')
        info('This is INFO. (20)')
        verbose('This is VERBOSE. (15)')
        debug('This is DEBUG. (10)')
        spam('This is SPAM. (5)')
        test2()
    StartBrowserLogging()
    test1()
################################################################################