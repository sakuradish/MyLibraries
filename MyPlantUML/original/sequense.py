################################################################################
import sys
sys.path.append("../..//MyLogger/")
from MyLoggerIf import *
################################################################################
# import time
# import math
# import sys
# import os
# import re
# import logging
# import coloredlogs
# import inspect
# from memory_profiler import profile
# import traceback
################################################################################
class sequenceManager:
    ################################################################################
    ## @brief 初期化処理
    @showTrace
    def __init__(self):
        self.stack = []
        pass
    ################################################################################
    ## @brief インスタンス取得
    @classmethod
    @showTrace
    def GetInstance(cls):
        if not hasattr(cls, 'this_'):
            cls.this_ = cls()
        return cls.this_
    ################################################################################
    ## @brief インスタンス取得
    @showTrace
    def push(self, from_entity, to_entity, message):
        for k,v in globals().items():
            if id(v) == id(from_entity):
                from_entity = k
        for k,v in globals().items():
            if id(v) == id(to_entity):
                to_entity = k
        self.stack.append({"from":from_entity, "to":to_entity, "message":message})
    ################################################################################
    ## @brief 初期化処理
    @showTrace
    def draw(self):
        ################################################################################
        ## @brief 初期化処理
        @showTrace
        def drawBase():
            entities = {}
            for stack in self.stack:
                entities[stack["from"]] = {}
                entities[stack["to"]] = {}
            sakura(entities)

            maxentitynamelength = 0
            for entity in entities.keys():
                if maxentitynamelength < len(entity):
                    maxentitynamelength = len(entity)
            sakura(maxentitynamelength)

            maxmessagelength = 0
            for stack in self.stack:
                if maxmessagelength < len(stack["message"]):
                    maxmessagelength = len(stack["message"])
            sakura(maxmessagelength)
            
            entity_w = 40 + maxentitynamelength * 5
            entity_space = 60 + maxmessagelength * 5
            horizontalline_y1 = 40
            horizontalline_y2 = 70 + len(self.stack) * 30

            
                

            # 縦横・間隔等をstackから出力
            text = ""
            text += '<line style="stroke:#A80036;stroke-width:1.0;stroke-dasharray:5.0,5.0;" x1="28" x2="28" y1="' + str(horizontalline_y1) + '" y2="' + str(horizontalline_y2) + '"/>' + "\n"
            text += '<line style="stroke:#A80036;stroke-width:1.0;stroke-dasharray:5.0,5.0;" x1="88" x2="88" y1="' + str(horizontalline_y1) + '" y2="' + str(horizontalline_y2) + '"/>' + "\n"
            
            text += '<rect fill="#FEFECE" filter="url(#f1ovyoxgkqkxtz)" height="30.2969" style="stroke:#A80036;stroke-width:1.5;" width="43" x="5" y="5"/>' + "\n"
            text += '<text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="29" x="12" y="24.9951">Bob' + "\n"
            text += '</text>' + "\n"
            text += '<rect fill="#FEFECE" filter="url(#f1ovyoxgkqkxtz)" height="30.2969" style="stroke:#A80036;stroke-width:1.5;" width="43" x="5" y="88.4297"/>' + "\n"
            text += '<text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="29" x="12" y="108.4248">Bob' + "\n"
            text += '</text>' + "\n"

            text += '<rect fill="#FEFECE" filter="url(#f1ovyoxgkqkxtz)" height="30.2969" style="stroke:#A80036;stroke-width:1.5;" width="49" x="62" y="5"/>' + "\n"
            text += '<text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="35" x="69" y="24.9951">Alice' + "\n"
            text += '</text>' + "\n"
            text += '<rect fill="#FEFECE" filter="url(#f1ovyoxgkqkxtz)" height="30.2969" style="stroke:#A80036;stroke-width:1.5;" width="49" x="62" y="88.4297"/>' + "\n"
            text += '<text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="35" x="69" y="108.4248">Alice' + "\n"
            text += '</text>' + "\n"
            return text
        ################################################################################
        ## @brief 初期化処理
        @showTrace
        def drawMessage():
            text = ""
            text += '<polygon fill="#A80036" points="76.5,67.4297,86.5,71.4297,76.5,75.4297,80.5,71.4297" style="stroke:#A80036;stroke-width:1.0;"/>' + "\n"
            text += '<line style="stroke:#A80036;stroke-width:1.0;" x1="28.5" x2="82.5" y1="71.4297" y2="71.4297"/>' + "\n"
            text += '<text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="30" x="35.5" y="66.3638">hello' + "\n"
            text += '</text>' + "\n"
            return text
        ################################################################################
        text = ""
        text += '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + "\n"
        text += '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" contentScriptType="application/ecmascript" contentStyleType="text/css" height="172px" preserveAspectRatio="none" style="width:163px;height:172px;background:#FFFFFF;" version="1.1" viewBox="0 0 163 172" width="163px" zoomAndPan="magnify">' + "\n"
        text += '<defs>' + "\n"
        text += '<filter height="300%" id="f1ovyoxgkqkxtz" width="300%" x="-1" y="-1">' + "\n"
        text += '<feGaussianBlur result="blurOut" stdDeviation="2.0"/>' + "\n"
        text += '<feColorMatrix in="blurOut" result="blurOut2" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .4 0"/>' + "\n"
        text += '<feOffset dx="4.0" dy="4.0" in="blurOut2" result="blurOut3"/>' + "\n"
        text += '<feBlend in="SourceGraphic" in2="blurOut3" mode="normal"/>' + "\n"
        text += '</filter>' + "\n"
        text += '</defs>' + "\n"
        text += '<g>' + "\n"
        text += drawBase()
        text += drawMessage()
        text += '</g>' + "\n"
        text += '</svg>' + "\n"
        open("output.svg", "w", encoding="utf-8").write(text)
################################################################################
## @brief sequence作図クラス
class entity:
    ################################################################################
    ## @brief 初期化処理
    @showTrace
    def __init__(self):
        pass
    ################################################################################
    ## @brief 初期化処理
    @showTrace
    def call(self, entity, message):
        sequenceManager.GetInstance().push(self, entity, message)
###############################################################################
if __name__ == '__main__':
    Bob = entity()
    Alice = entity()
    Bob.call(Alice, "Hello")
    Bob.call(Alice, "GoodBye")
    sequenceManager.GetInstance().draw()
###############################################################################