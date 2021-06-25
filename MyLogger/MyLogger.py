################################################################################
import time
import math
import sys
import os
import re
import logging
import coloredlogs
import inspect
from memory_profiler import profile
import traceback
################################################################################
## @brief loggingクラス
class MyLogger:
    LEVEL_TABLE = {
        'SPAM':5,
        'DEBUG':10,
        'VERBOSE':15,
        'INFO':20,
        'NOTICE':25,
        'WARNING':30,
        'SUCCESS':35,
        'ERROR':40,
        'CRITICAL':50,
        'SAKURA':99
    }
    LEVEL_CONFIG = {}
    ################################################################################
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
                            fmt='[ %(asctime)s ][ %(levelname)8s ][ %(funcName)6s ][ %(message)s ]', datefmt='%H:%M:%S')
        # ログをファイル出力
        basedir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(basedir+'/log/'):
            os.makedirs(basedir+'/log/')
        handler = logging.FileHandler(basedir+'/log/output.log', 'w', 'utf-8')
        handler.setFormatter(logging.Formatter(
            '[ %(asctime)s ][ %(levelname)8s ][ %(funcName)6s ][ %(message)s ]', datefmt='%H:%M:%S'))
        logger.addHandler(handler)
        # メンバ変数初期化
        self.stack = {}
        self.stacklevel = 0
        self.numerator = ''
        self.fraction = ''
################################################################################
    ## @brief インスタンス取得
    @classmethod
    def GetInstance(cls, level='DEBUG'):
        filename = os.path.basename(inspect.stack()[1].filename)
        if not hasattr(cls, 'this_'):
            # loggingモジュールの設定としては、全ログ出力するようにしておく。
            # MyLogger内でファイルごとに出力レベルを管理する。
            cls.this_ = cls('SPAM')
        if not hasattr(cls, 'LEVEL_CONFIG'):
            cls.LEVEL_CONFIG = {}
        # 同じファイル名は想定していない。
        cls.LEVEL_CONFIG[filename] = level
        cls.this_.info("set log level " + level + "(" + str(cls.LEVEL_TABLE[level]) + ") for " + filename)
        cls.this_.sakura(cls.LEVEL_CONFIG)
        return cls.this_
################################################################################
    ## @brief 開始ログと終了ログを出力するDecoratorの共通処理部
    def decoSub(self, func, frameinfo, memory=False, *args, **kwargs):
        try:
            pwd = os.getcwd()
            self.start(frameinfo)
            if not memory:
                ret = func(*args,**kwargs)
            else:
                ret = profile(func)(*args,**kwargs)
            self.finish()
            os.chdir(pwd)
            return ret
        except Exception as e:
            self.critical("+++++++++++++++++++++++++++++++++++")
            for i in range(len(self.stack)):
                stack = self.stack[i].copy()
                del stack['start']
                stack = list(stack.values())
                self.critical(stack)
            self.critical("+++++++++++++++++++++++++++++++++++")
            self.critical(type(e))
            self.critical(e)
            self.critical(traceback.format_exc())
            self.critical("+++++++++++++++++++++++++++++++++++")
            input("press any key to exit ...")
            sys.exit()
################################################################################
    ## @brief 開始ログと終了ログを出力するDecorator
    @classmethod
    def deco(cls, func):
        frameinfo = inspect.stack()[1]
        def decowrapper(*args,**kwargs):
            cls.GetInstance().decoSub(func, frameinfo, memory=False, *args, **kwargs)
        return decowrapper
################################################################################
    ## @brief 開始ログと終了ログを出力するDecorator(memory_profile付き)
    def decomemo(self, func):
        frameinfo = inspect.stack()[1]
        def decowrapper(*args,**kwargs):
            self.decoSub(func, frameinfo, memory=True, *args, **kwargs)
        return decowrapper
################################################################################
    ## @brief 進捗率分子登録
    def SetNumerator(self, numerator):
        self.numerator = str(numerator)
################################################################################
    ## @brief 進捗率分母登録
    def SetFraction(self, fraction):
        self.fraction = str(fraction)
################################################################################
    ## @brief 開始ログ出力
    def start(self, frameinfo):
        self.stack[self.stacklevel] = {}
        self.stack[self.stacklevel]['level'] = ('■' * (self.stacklevel) + '□□□□□□□□□□')[:10]
        self.stack[self.stacklevel]['file'] = os.path.basename(frameinfo.filename)
        self.stack[self.stacklevel]['func'] = re.sub(".*def (.*)\(.*\n", "\\1", frameinfo.code_context[0])
        self.stack[self.stacklevel]['start'] = round(time.time(), 2)
        for i in range(len(self.stack)):
            start = self.stack[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stack[i]['elapsedTime'] = elapsedTime
        self.stacklevel += 1
        self.debug("+++++++++++++++++++++++++++++++++++")
        for i in range(len(self.stack)):
            stack = self.stack[i].copy()
            del stack['start']
            stack = list(stack.values())
            if i == len(self.stack)-1:
                self.debug("Enter >>>", stack)
            else:
                self.debug("         ", stack)
        self.debug("+++++++++++++++++++++++++++++++++++")
################################################################################
    ## @brief 終了ログ出力
    def finish(self):
        for i in range(len(self.stack)):
            start = self.stack[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stack[i]['elapsedTime'] = elapsedTime
        self.debug("+++++++++++++++++++++++++++++++++++")
        for i in range(len(self.stack)):
            stack = self.stack[i].copy()
            del stack['start']
            stack = list(stack.values())
            if i == len(self.stack)-1:
                self.debug("Exit  <<<", stack)
            elif i == len(self.stack)-2:
                self.debug("Enter >>>", stack)
            else:
                self.debug("         ", stack)
        self.debug("+++++++++++++++++++++++++++++++++++")
        self.stacklevel -= 1
        del self.stack[self.stacklevel]
################################################################################
    ## @brief timeout判定
    def isTimeOut(self, timeout):
        if len(self.stack) < 1:
            return False
        for i in range(len(self.stack)):
            start = self.stack[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stack[i]['elapsedTime'] = elapsedTime
        # start = self.stack[self.stacklevel-1]['start']
        # elapsedTime = round(time.time() - start, 2)
        elapsedTime = self.stack[self.stacklevel-1]['elapsedTime']
        if timeout < elapsedTime:
            self.warning(elapsedTime,"/",timeout,"elapsed")
            return True
        else:
            self.info(elapsedTime,"/",timeout,"elapsed")
            return False
################################################################################
    def makeMessage(self, args, frameinfo):
        msg = ''
        for arg in args:
            msg += str(arg) + " "
        msg = '[' + frameinfo.filename + ':' + str(frameinfo.lineno) + '] ' + msg
        msg = '[' + self.numerator + '/' + self.fraction + '] ' + msg
        if msg.find('\n') != -1:
            msg = msg.strip(" ")
            msg = msg.strip("\t")
            msg = '\n' + msg + '\n'
        return msg
################################################################################
    def isNeedToLog(self, level, frameinfo):
        return MyLogger.LEVEL_TABLE[level] >= MyLogger.LEVEL_TABLE[MyLogger.LEVEL_CONFIG[frameinfo.filename]]
################################################################################
    ## @brief sakuraレベルログ
    def sakura(self, *args, **kwargs):
        if self.isNeedToLog("SAKURA", inspect.stack()[1]):
            self.origin_sakura(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief criticalレベルログ
    def critical(self, *args, **kwargs):
        if self.isNeedToLog("CRITICAL", inspect.stack()[1]):
            self.origin_critical(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief errorレベルログ
    def error(self, *args, **kwargs):
        if self.isNeedToLog("ERROR", inspect.stack()[1]):
            self.origin_error(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief successレベルログ
    def success(self, *args, **kwargs):
        if self.isNeedToLog("SUCCESS", inspect.stack()[1]):
            self.origin_success(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief warningレベルログ
    def warning(self, *args, **kwargs):
        if self.isNeedToLog("WARNING", inspect.stack()[1]):
            self.origin_warning(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief noticeレベルログ
    def notice(self, *args, **kwargs):
        if self.isNeedToLog("NOTICE", inspect.stack()[1]):
            self.origin_notice(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief infoレベルログ
    def info(self, *args, **kwargs):
        if self.isNeedToLog("INFO", inspect.stack()[1]):
            self.origin_info(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief verboseレベルログ
    def verbose(self, *args, **kwargs):
        if self.isNeedToLog("VERBOSE", inspect.stack()[1]):
            self.origin_verbose(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief debugレベルログ
    def debug(self, *args, **kwargs):
        if self.isNeedToLog("DEBUG", inspect.stack()[1]):
            self.origin_debug(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief spamレベルログ
    def spam(self, *args, **kwargs):
        if self.isNeedToLog("SPAM", inspect.stack()[1]):
            self.origin_spam(self.makeMessage(args, inspect.stack()[1]), **kwargs)
################################################################################
    ## @brief ログ出力
    # @note
    # オリジナルログ関数を使用したときに、
    # 呼び出し元関数が良い感じにログに表示されるように
    # stacklevelを調整している。
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=3):
        self.origin_log(level, msg, args, exc_info, extra, stack_info, stacklevel)
################################################################################
if __name__ == '__main__':
    MyLogger = MyLogger.GetInstance('DEBUG')
    @MyLogger.decomemo
    def test3():
        while not MyLogger.isTimeOut(1):
            pass
    @MyLogger.deco
    def test2():
        MyLogger.SetFraction(10)
        for i in range(10):
            MyLogger.SetNumerator(i)
            MyLogger.success('logging with progress')
        test3()
    @MyLogger.deco
    def test1():
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
        test2()
    test1()
#============================================================================================================================================================================================================================================================