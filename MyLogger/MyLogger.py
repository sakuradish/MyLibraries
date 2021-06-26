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
        'spam':{'level':'SPAM', 'value':5},          'SPAM':{'level':'SPAM', 'value':5},
        'debug':{'level':'DEBUG', 'value':10},       'DEBUG':{'level':'DEBUG', 'value':10},
        'verbose':{'level':'VERBOSE', 'value':15},   'VERBOSE':{'level':'VERBOSE', 'value':15},
        'info':{'level':'INFO', 'value':20},         'INFO':{'level':'INFO', 'value':20},
        'notice':{'level':'NOTICE', 'value':25},     'NOTICE':{'level':'NOTICE', 'value':25},
        'warning':{'level':'WARNING', 'value':30},   'WARNING':{'level':'WARNING', 'value':30},
        'success':{'level':'SUCCESS', 'value':35},   'SUCCESS':{'level':'SUCCESS', 'value':35},
        'error':{'level':'ERROR', 'value':40},       'ERROR':{'level':'ERROR', 'value':40},
        'critical':{'level':'CRITICAL', 'value':50}, 'CRITICAL':{'level':'CRITICAL', 'value':50},
        'sakura':{'level':'SAKURA', 'value':99},     'SAKURA':{'level':'SAKURA', 'value':99}
    }
    ################################################################################
    ## @brief 初期化処理
    def __init__(self, level='DEBUG'):
        level = self.LEVEL_TABLE[level]['level']
        self.level_map = {}
        self.block_map = {}
        self.func_map = {}
        # ログレベル追加
        logger = logging.getLogger(__file__+level)
        logging.SPAM = self.LEVEL_TABLE['SPAM']['value']
        logging.VERBOSE = self.LEVEL_TABLE['VERBOSE']['value']
        logging.NOTICE = self.LEVEL_TABLE['NOTICE']['value']
        logging.SUCCESS = self.LEVEL_TABLE['SUCCESS']['value']
        logging.SAKURA = self.LEVEL_TABLE['SAKURA']['value']
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
        # self.origin_sakura = logger.sakura
        # self.origin_critical = logger.critical
        # self.origin_error = logger.error
        # self.origin_success = logger.success
        # self.origin_warning = logger.warning
        # self.origin_notice = logger.notice
        # self.origin_info = logger.info
        # self.origin_verbose = logger.verbose
        # self.origin_debug = logger.debug
        # self.origin_spam = logger.spam
        self.func_map["SAKURA"] = logger.sakura
        self.func_map["CRITICAL"] = logger.critical
        self.func_map["ERROR"] = logger.error
        self.func_map["SUCCESS"] = logger.success
        self.func_map["WARNING"] = logger.warning
        self.func_map["NOTICE"] = logger.notice
        self.func_map["INFO"] = logger.info
        self.func_map["VERBOSE"] = logger.verbose
        self.func_map["DEBUG"] = logger.debug
        self.func_map["SPAM"] = logger.spam
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
    def GetInstance(cls):
        # ファイルごとに出力レベルを管理するので、一番低いレベルを設定しておく。
        if not hasattr(cls, 'this_'):
            cls.this_ = cls('SPAM')
        return cls.this_
################################################################################
    ## @brief ログ出力
    # @note
    # オリジナルログ関数を使用したときに、
    # 呼び出し元関数が良い感じにログに表示されるように
    # stacklevelを調整している。
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=4):
        self.origin_log(level, msg, args, exc_info, extra, stack_info, stacklevel)
################################################################################
    ## @brief sakuraレベルログ
    def printLog(self, level, *args, **kwargs):
        level = self.LEVEL_TABLE[level]['level']
        frameinfo = inspect.stack()[2]
        filename = os.path.basename(frameinfo.filename)
        if self.isNeedToLog(level, filename):
            self.func_map[level](self.makeMessage(args, filename, frameinfo.lineno))
################################################################################
    ## @brief sakuraレベルログ
    def sakura(self, *args, **kwargs):
        self.printLog("SAKURA", *args, **kwargs)
################################################################################
    ## @brief criticalレベルログ
    def critical(self, *args, **kwargs):
        self.printLog("CRITICAL", *args, **kwargs)
################################################################################
    ## @brief errorレベルログ
    def error(self, *args, **kwargs):
        self.printLog("ERROR", *args, **kwargs)
################################################################################
    ## @brief successレベルログ
    def success(self, *args, **kwargs):
        self.printLog("SUCCESS", *args, **kwargs)
################################################################################
    ## @brief warningレベルログ
    def warning(self, *args, **kwargs):
        self.printLog("WARNING", *args, **kwargs)
################################################################################
    ## @brief noticeレベルログ
    def notice(self, *args, **kwargs):
        self.printLog("NOTICE", *args, **kwargs)
################################################################################
    ## @brief infoレベルログ
    def info(self, *args, **kwargs):
        self.printLog("INFO", *args, **kwargs)
################################################################################
    ## @brief verboseレベルログ
    def verbose(self, *args, **kwargs):
        self.printLog("VERBOSE", *args, **kwargs)
################################################################################
    ## @brief debugレベルログ
    def debug(self, *args, **kwargs):
        self.printLog("DEBUG", *args, **kwargs)
################################################################################
    ## @brief spamレベルログ
    def spam(self, *args, **kwargs):
        self.printLog("SPAM", *args, **kwargs)
################################################################################
    ## @brief sakuraレベルログ
    def SAKURA(self, *args, **kwargs):
        self.printLog("SAKURA", *args, **kwargs)
################################################################################
    ## @brief criticalレベルログ
    def CRITICAL(self, *args, **kwargs):
        self.printLog("CRITICAL", *args, **kwargs)
################################################################################
    ## @brief errorレベルログ
    def ERROR(self, *args, **kwargs):
        self.printLog("ERROR", *args, **kwargs)
################################################################################
    ## @brief successレベルログ
    def SUCCESS(self, *args, **kwargs):
        self.printLog("SUCCESS", *args, **kwargs)
################################################################################
    ## @brief warningレベルログ
    def WARNING(self, *args, **kwargs):
        self.printLog("WARNING", *args, **kwargs)
################################################################################
    ## @brief noticeレベルログ
    def NOTICE(self, *args, **kwargs):
        self.printLog("NOTICE", *args, **kwargs)
################################################################################
    ## @brief infoレベルログ
    def INFO(self, *args, **kwargs):
        self.printLog("INFO", *args, **kwargs)
################################################################################
    ## @brief verboseレベルログ
    def VERBOSE(self, *args, **kwargs):
        self.printLog("VERBOSE", *args, **kwargs)
################################################################################
    ## @brief debugレベルログ
    def DEBUG(self, *args, **kwargs):
        self.printLog("DEBUG", *args, **kwargs)
################################################################################
    ## @brief spamレベルログ
    def SPAM(self, *args, **kwargs):
        self.printLog("SPAM", *args, **kwargs)
################################################################################
    def makeMessage(self, args, filename, lineno):
        msg = ''
        for arg in args:
            msg += str(arg) + " "
        msg = '[' + filename + ':' + str(lineno) + '] ' + msg
        msg = '[' + self.numerator + '/' + self.fraction + '] ' + msg
        if msg.find('\n') != -1:
            msg = msg.strip(" ")
            msg = msg.strip("\t")
            msg = '\n' + msg + '\n'
        return msg
################################################################################
    ## @brief インスタンス取得
    def setLogLevel(self, level='DEBUG', block=""):
        level = self.LEVEL_TABLE[level]['level']
        filename = os.path.basename(inspect.stack()[2].filename)
        if block == "":
            block = filename
        self.block_map[filename] = block
        # 同じファイル名は想定していない。
        self.level_map[block] = level
        self.INFO("set log level " + level + "(" + str(self.LEVEL_TABLE[level]['value']) + ") for " + block)
        self.SAKURA(self.level_map)
################################################################################
    def isNeedToLog(self, level, filename):
        if filename not in self.block_map:
            self.block_map[filename] = filename
            self.level_map[filename] = "DEBUG"
        return self.LEVEL_TABLE[level]['value'] >= self.LEVEL_TABLE[self.level_map[self.block_map[filename]]]['value']
################################################################################
    ## @brief 開始ログと終了ログを出力するDecorator
    def showTrace(self, func, frameinfo=None, memory=False):
        if frameinfo == None:
            frameinfo = inspect.stack()[2]
        def decowrapper(*args,**kwargs):
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
                    self.CRITICAL(stack)
                self.CRITICAL("+++++++++++++++++++++++++++++++++++")
                self.CRITICAL(type(e))
                self.CRITICAL(e)
                self.CRITICAL(traceback.format_exc())
                self.CRITICAL("+++++++++++++++++++++++++++++++++++")
                input("press any key to exit ...")
                sys.exit()
        return decowrapper
################################################################################
    ## @brief 開始ログと終了ログを出力するDecorator(memory_profile付き)
    def showTraceAndProfile(self, func):
        return self.showTrace(func, frameinfo=inspect.stack()[2], memory=True)
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
        self.DEBUG("+++++++++++++++++++++++++++++++++++")
        for i in range(len(self.stack)):
            stack = self.stack[i].copy()
            del stack['start']
            stack = list(stack.values())
            if i == len(self.stack)-1:
                self.DEBUG("Enter >>>", stack)
            else:
                self.DEBUG("         ", stack)
        self.DEBUG("+++++++++++++++++++++++++++++++++++")
################################################################################
    ## @brief 終了ログ出力
    def finish(self):
        for i in range(len(self.stack)):
            start = self.stack[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stack[i]['elapsedTime'] = elapsedTime
        self.DEBUG("+++++++++++++++++++++++++++++++++++")
        for i in range(len(self.stack)):
            stack = self.stack[i].copy()
            del stack['start']
            stack = list(stack.values())
            if i == len(self.stack)-1:
                self.DEBUG("Exit  <<<", stack)
            elif i == len(self.stack)-2:
                self.DEBUG("Enter >>>", stack)
            else:
                self.DEBUG("         ", stack)
        self.DEBUG("+++++++++++++++++++++++++++++++++++")
        self.stacklevel -= 1
        del self.stack[self.stacklevel]
################################################################################
    ## @brief 進捗率登録
    def setProgress(self, numerator, fraction):
        self.numerator = str(numerator)
        self.fraction = str(fraction)
################################################################################
    ## @brief timeout判定
    def isElapsed(self, second):
        if len(self.stack) < 1:
            return False
        for i in range(len(self.stack)):
            start = self.stack[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stack[i]['elapsedTime'] = elapsedTime
        elapsedTime = self.stack[self.stacklevel-1]['elapsedTime']
        if second < elapsedTime:
            self.WARNING(elapsedTime,"/",second,"elapsed")
            return True
        else:
            self.INFO(elapsedTime,"/",second,"elapsed")
            return False
###############################################################################
    ## @brief sleep
    def sleep(self, second):
        if second <= 0:
            self.ERROR("argument second is negative or zero")
        else:
            span = 3
            start = round(time.time(), 2)
            prev = -999
            while 1:
                elapsed = round(time.time() - start, 2)
                if elapsed - prev > span:
                    self.DEBUG("time sleeping " + str(elapsed) + " / " + str(second))
                    prev = elapsed
                    if elapsed >= second:
                        break
###############################################################################