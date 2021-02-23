# ===================================================================================
import time
import math
import sys
import os
import logging
import coloredlogs
import inspect
from memory_profiler import profile
import traceback
# ===================================================================================
## @brief loggingクラス
class MyLogger:
    ## @brief 初期化処理
    def __init__(self, level='DEBUG'):
        # ログレベル追加
        logger = logging.getLogger(__file__+level)
        logging.SPAM = 5 # DEBUGの下
        logging.VERBOSE = 15 # DEBUGとINFOの間
        logging.NOTICE = 25 # INFOとWARNINGの間
        logging.SUCCESS = 35 # WARNINGとERRORの間
        logging.SAKURA = 99 # 一番上
        logging.addLevelName(logging.SPAM, 'SPAM')
        logging.addLevelName(logging.VERBOSE, 'VERBOSE')
        logging.addLevelName(logging.NOTICE, 'NOTICE')
        logging.addLevelName(logging.SUCCESS, 'SUCCESS')
        logging.addLevelName(logging.SAKURA, 'SAKURA')
        setattr(logger, 'spam', lambda message, *args: logger._log(logging.SPAM, message, args))
        setattr(logger, 'verbose', lambda message, *args: logger._log(logging.VERBOSE, message, args))
        setattr(logger, 'notice', lambda message, *args: logger._log(logging.NOTICE, message, args))
        setattr(logger, 'success', lambda message, *args: logger._log(logging.SUCCESS, message, args))
        setattr(logger, 'sakura', lambda message, *args: logger._log(logging.SAKURA, message, args))
        # 自作ログ関数を噛ませるために、オリジナルを保存
        self.origin_sakura = logger.sakura
        self.origin_critical = logger.critical
        self.origin_error = logger.error
        self.origin_success = logger.success
        self.origin_warning = logger.warning
        self.origin_notice = logger.notice
        self.origin_info = logger.info
        self.origin_verbose = logger.verbose
        self.origin_debug = logger.debug
        self.origin_spam = logger.spam
        self.origin_log = logger._log
        logger._log = self._log
        # コンソール上のログを色付け
        coloredlogs.CAN_USE_BOLD_FONT = True
        coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'},
                                            'hostname': {'color': 'magenta'},
                                            'levelname': {'color': 'black', 'bold': True},
                                            'name': {'color': 'blue'},
                                            'programname': {'color': 'cyan'}
                                            }
        coloredlogs.DEFAULT_LEVEL_STYLES = {
                                            'info': {},
                                            'notice': {'color': 'magenta'},
                                            'verbose': {'color': 'blue'},
                                            'success': {'color': 'green', 'bold': True},
                                            'spam': {'color': 'cyan'},
                                            'critical': {'color': 'red', 'bold': True},
                                            'error': {'color': 'red'},
                                            'debug': {'color': 'green'},
                                            'warning': {'color': 'yellow'},
                                            'sakura': {'color': 200, 'bold': True},
                                            }
        coloredlogs.install(level=level, logger=logger,
                            fmt='[ %(asctime)s ][ %(levelname)8s ][ %(funcName)6s ][ %(message)s ]', datefmt='%Y/%m/%d %H:%M:%S')
        # ログをファイル出力
        basedir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(basedir+'/log/'):
            os.makedirs(basedir+'/log/')
        handler = logging.FileHandler(basedir+'/log/output.log', 'w', 'utf-8')
        handler.setFormatter(logging.Formatter(
            '[ %(asctime)s ][ %(levelname)8s ][ %(funcName)6s ][ %(message)s ]', datefmt='%Y/%m/%d %H:%M:%S'))
        logger.addHandler(handler)
        # BrowserLogging用にHTMLフォーマットでもファイル出力
        handler = logging.FileHandler(basedir+'/log/output.html', 'w', 'utf-8')
        handler.setFormatter(logging.Formatter(
            '<div>[ <span class="asctime">%(asctime)s</span> ][ <span class="levelname">%(levelname)8s</span> ][ <span class="funcName">%(funcName)6s</span> ][ <span class="%(levelname)s"> %(message)s</span> ]</div>', datefmt='%Y/%m/%d %H:%M:%S'))
        logger.addHandler(handler)
        # メンバ変数初期化
        self.stack = {}
        self.stacklevel = 0
        self.numerator = ''
        self.fraction = ''
        # 初期化処理のログ
        self.info('level is ', level)
        self.info(basedir+'/log/output.log')
        self.info(basedir+'/log/output.html')
# ===================================================================================
    ## @brief BrowserLogging開始
    # @note
    # スレッド化しようと思ったけど、Errorが出たので後回し
    # 雑にos.systemからpythonを起動
    def StartBrowserLogging(self):
        basedir = os.path.dirname(os.path.abspath(__file__))
        os.system('start ' + basedir + '/BrowserLogging/BrowserLogging.py')
        self.info('start BrowserLogging')
# ===================================================================================
    ## @brief インスタンス取得
    # @note
    # ログレベルは最初に呼ばれた時のもので統一される
    @classmethod
    def GetInstance(cls, level='DEBUG'):
        if not hasattr(cls, 'this_'):
            cls.this_ = cls(level=level)
        return cls.this_
# ===================================================================================
    ## @brief 開始ログと終了ログを出力するDecorator
    def deco(self, func):
        filename =os.path.basename(inspect.stack()[1].filename)
        funcname = inspect.stack()[1].code_context[0]
        funcname = funcname[funcname.find('def ')+4:]
        funcname = funcname[:funcname.find('('):]
        def decowrapper(*args,**kwargs):
            try:
                self.start(filename, funcname)
                ret = func(*args,**kwargs)
                self.finish()
                return ret
            except Exception as e:
                for i in range(1,self.stacklevel+1,1):
                    stack = self.stack[i].copy()
                    del stack['start']
                    self.critical(stack)
                self.critical(type(e))
                self.critical(e)
                self.critical(traceback.format_exc())
                sys.exit()
        return decowrapper
# ===================================================================================
    ## @brief メモリ使用率表示付きDecorator
    def decomemo(self, func):
        filename =os.path.basename(inspect.stack()[1].filename)
        funcname = inspect.stack()[1].code_context[0]
        funcname = funcname[funcname.find('def ')+4:]
        funcname = funcname[:funcname.find('('):]
        def decowrapper(*args,**kwargs):
            try:
                self.start(filename, funcname)
                ret = profile(func)(*args,**kwargs)
                self.finish()
                return ret
            except Exception as e:
                for i in range(1,self.stacklevel+1,1):
                    stack = self.stack[i].copy()
                    del stack['start']
                    self.critical(stack)
                self.critical(type(e))
                self.critical(e)
                self.critical(traceback.format_exc())
                sys.exit()
        return decowrapper
# ===================================================================================
    ## @brief 進捗率分子登録
    def SetNumerator(self, numerator):
        self.numerator = str(numerator)
# ===================================================================================
    ## @brief 進捗率分母登録
    # @note
    # 新しい分母設定時(新しいFor文の処理に移るときなどを想定)には、
    # 分子をリセットする。
    def SetFraction(self, fraction):
        self.numerator = ''
        self.fraction = str(fraction)
# ===================================================================================
    ## @brief 開始ログ出力
    def start(self, filename, funcname):
        file = filename
        func = funcname
        start = time.time()
        self.stacklevel += 1
        self.stack[self.stacklevel] = {}
        levelString = ''
        for i in range(1,self.stacklevel+1,1):
            levelString += '■'
        levelString = (levelString+'□□□□□□□□□□')[:10]
        self.stack[self.stacklevel]['level'] = levelString
        self.stack[self.stacklevel]['file'] = file
        self.stack[self.stacklevel]['func'] = func
        self.stack[self.stacklevel]['start'] = round(start, 2)
        stack = self.stack[self.stacklevel].copy()
        del stack['start']
        self.debug(stack)
# ===================================================================================
    ## @brief 終了ログ出力
    def finish(self):
        for i in range(1,self.stacklevel+1,1):
            start = self.stack[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stack[i]['elapsedTime'] = elapsedTime
        stack = self.stack[self.stacklevel].copy()
        del stack['start']
        self.debug(stack)
        self.stacklevel -= 1
# ===================================================================================
    ## @brief sakuraレベルログ
    def sakura(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_sakura(msg, **kwargs)
# ===================================================================================
    ## @brief criticalレベルログ
    def critical(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_critical(msg, **kwargs)
# ===================================================================================
    ## @brief errorレベルログ
    def error(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_error(msg, **kwargs)
# ===================================================================================
    ## @brief successレベルログ
    def success(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_success(msg, **kwargs)
# ===================================================================================
    ## @brief warningレベルログ
    def warning(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_warning(msg, **kwargs)
# ===================================================================================
    ## @brief noticeレベルログ
    def notice(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_notice(msg, **kwargs)
# ===================================================================================
    ## @brief infoレベルログ
    def info(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_info(msg, **kwargs)
# ===================================================================================
    ## @brief verboseレベルログ
    def verbose(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_verbose(msg, **kwargs)
# ===================================================================================
    ## @brief debugレベルログ
    def debug(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_debug(msg, **kwargs)
# ===================================================================================
    ## @brief spamレベルログ
    def spam(self, *args, **kwargs):
        msg = ''
        for arg in args:
            msg += str(arg) + "\t"
        self.origin_spam(msg, **kwargs)
# ===================================================================================
    ## @brief ログ出力
    # @note
    # オリジナルログ関数を使用したときに、
    # 呼び出し元関数が良い感じにログに表示されるように
    # stacklevelを調整している。
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=3):
        msg = msg.strip(" ")
        msg = msg.strip("\t")
        if self.numerator != '' and self.fraction != '':
            msg = '[' + self.numerator + '/' + self.fraction + '] ' + msg
        if msg.find('\n') != -1:
            msg = '\n' + msg + '\n'
        self.origin_log(level, msg, args, exc_info, extra, stack_info, stacklevel)
# ===================================================================================
if __name__ == '__main__':
    MyLogger = MyLogger.GetInstance('DEBUG')
    MyLogger.StartBrowserLogging()
    @MyLogger.deco
    def test():
        MyLogger.SetFraction(10)
        for i in range(10):
            MyLogger.SetNumerator(i)
            MyLogger.success('logging with progress')
        MyLogger.sakura('This is SAKURA. (99)')
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
#============================================================================================================================================================================================================================================================