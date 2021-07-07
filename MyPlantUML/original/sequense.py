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
    stack = []
    ################################################################################
    @classmethod
    @showTrace
    def push(cls, from_entity, to_entity, message):
        cls.stack.append({"from":from_entity.getName(), "to":to_entity.getName(), "message":message})
    ################################################################################
    @classmethod
    @showTrace
    def draw(self):
        ################################################################################
        def getHeader(w,h):
            return \
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?> \n\
            <svg xmlns="http://www.w3.org/2000/svg" \n\
                 xmlns:xlink="http://www.w3.org/1999/xlink" \n\
                 contentScriptType="application/ecmascript" \n\
                 contentStyleType="text/css" \n\
                 height="'+str(h)+'px" \n\
                 preserveAspectRatio="none" \n\
                 style="width:'+str(w)+'px;height:'+str(h)+'px;background:#FFFFFF;" \n\
                 version="1.1" \n\
                 viewBox="0 0 '+str(w)+' '+str(h)+'" \n\
                 width="'+str(w)+'px" \n\
                 zoomAndPan="magnify"> \n\
            <defs> \n\
            <filter height="300%" id="f1ovyoxgkqkxtz" width="300%" x="-1" y="-1"> \n\
            <feGaussianBlur result="blurOut" stdDeviation="2.0"/> \n\
            <feColorMatrix in="blurOut" result="blurOut2" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .4 0"/> \n\
            <feOffset dx="4.0" dy="4.0" in="blurOut2" result="blurOut3"/> \n\
            <feBlend in="SourceGraphic" in2="blurOut3" mode="normal"/> \n\
            </filter> \n\
            </defs> \n\
            <g>' + '\n'
        ################################################################################
        def getFooter():
            return \
            '</g> \n\
            </svg>' + '\n'
        ################################################################################
        def drawLine(x1,y1,x2,y2):
            return \
            '<line \n\
            style="stroke:#A80036;stroke-width:1.0;stroke-dasharray:5.0,5.0;" \n\
            x1="'+str(x1)+'" \n\
            x2="'+str(x2)+'" \n\
            y1="'+str(y1)+'" \n\
            y2="'+str(y2)+'" \n\
            />' + "\n"
        ################################################################################
        def drawArrow(x1,y1,x2,y2,direction="TORIGHT"):
            if direction=="TORIGHT":
                return \
                '<polygon \n\
                fill="#A80036" \n\
                points="\n\
                '+str(x2-7)+','+str(y2-7)+',\n\
                '+str(x2-3)+','+str(y2)+',\n\
                '+str(x2-7)+','+str(y2+7)+',\n\
                '+str(x2)+','+str(y2)+'" \n\
                style="stroke:#A80036;stroke-width:1.0;" \n\
                />' + "\n" + drawLine(x1,x2,y1,y2)
            elif direction=="TOLEFT":
                return \
                '<polygon \n\
                fill="#A80036" \n\
                points="\n\
                '+str(x1+7)+','+str(y1+7)+',\n\
                '+str(x1+3)+','+str(y1)+',\n\
                '+str(x1+7)+','+str(y1-7)+',\n\
                '+str(x1)+','+str(y1)+'" \n\
                style="stroke:#A80036;stroke-width:1.0;" \n\
                />' + "\n" + drawLine(x1,x2,y1,y2)
            else:
                critical("NOT SUPPORTED")
        ################################################################################
        def drawRect(x,y,w,h):
            return \
            '<rect \n\
            fill="#FEFECE" \n\
            filter="url(#f1ovyoxgkqkxtz)" \n\
            height="'+str(h)+'" \n\
            style="stroke:#A80036;stroke-width:1.5;" \n\
            width="'+str(w)+'" \n\
            x="'+str(x)+'" \n\
            y="'+str(y)+'" \n\
            />' + "\n"
        ################################################################################
        def drawText(x,y,w,message):
            return \
            '<text \n\
            fill="#000000" \n\
            font-family="sans-serif" \n\
            font-size="14" \n\
            lengthAdjust="spacing" \n\
            textLength="'+str(w)+'" \n\
            x="'+str(x)+'" \n\
            y="'+str(y)+'"\n\
            >'+str(message)+'</text>' + "\n"
        ################################################################################
        entities = {}
        for stack in self.stack:
            entities[stack["from"]] = {}
            entities[stack["to"]] = {}
        maxEntityNameLength = max([len(entity) for entity in entities.keys()])
        maxMessageLength = max([len(stack["message"]) for stack in self.stack])
        # ベースとなる縦線とオブジェクト達のレイアウトを計算
        arrowLength_v = 20 + (maxMessageLength * 10)
        arrowLength_h = 20 + (len(self.stack) * 20)
        for entity in entities.keys():
            entities[entity]["top_x"] = 10 + list(entities.keys()).index(entity) * arrowLength_v
            entities[entity]["top_y"] = 10
            entities[entity]["top_w"] = 20 + (maxEntityNameLength * 10)
            entities[entity]["top_h"] = 30
            entities[entity]["bottom_x"] = entities[entity]["top_x"]
            entities[entity]["bottom_y"] = entities[entity]["top_y"] + entities[entity]["top_h"] + arrowLength_h
            entities[entity]["bottom_w"] = entities[entity]["top_w"]
            entities[entity]["bottom_h"] = entities[entity]["top_h"]

        text = ""
        text += getHeader(1000,1000)
        for entity,params in entities.items():
            text += drawLine(params["top_x"]+(params["top_w"]/2),\
                             params["top_y"]+params["top_h"],\
                             params["bottom_x"]+(params["bottom_w"]/2),\
                             params["bottom_y"])
            text += drawRect(params["top_x"],params["top_y"],params["top_w"],params["top_h"])
            text += drawText(params["top_x"]+10,params["top_y"]+(params["top_h"]/2),(maxEntityNameLength * 10),entity)
            text += drawRect(params["bottom_x"],params["bottom_y"],params["bottom_w"],params["bottom_h"])
            text += drawText(params["bottom_x"]+10,params["bottom_y"]+(params["bottom_h"]/2),(maxEntityNameLength * 10),entity)
        for stack in self.stack:
            # TODO : drawing communication message
            sakura(self.stack.index(stack),stack)
        text += getFooter()
        ################################################################################
        open("output.svg", "w", encoding="utf-8").write(text)
################################################################################
## @brief sequence作図クラス
class entity:
    ################################################################################
    @showTrace
    def __init__(self, name):
        self.name = name
    ################################################################################
    @showTrace
    def call(self, entity, message):
        sequenceManager.push(self, entity, message)
    ################################################################################
    @showTrace
    def getName(self):
        return self.name
###############################################################################
if __name__ == '__main__':
    Bob = entity("Bob")
    Alice = entity("Alice")
    Bob.call(Alice, "Hello")
    Bob.call(Alice, "GoodBye")
    sequenceManager.draw()
###############################################################################