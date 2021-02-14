# ===================================================================================
import os
import json
from PIL import ImageDraw
from PIL import Image
import pyautogui
import numpy
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, request, render_template
app = Flask(__name__)
streamed_data = {}
# ===================================================================================
## @brief index.htmlを表示
@app.route('/')
def index():
    print("show index.html")
    global streamed_data
    client_ip = str(request.environ['REMOTE_ADDR'])
    streamed_data[client_ip] = []
    print("connected from "+ client_ip)
    print(streamed_data)
    return render_template('index.html')
# ===================================================================================
## @brief スクリーンショットを更新
# @note
# index.html側で画面サイズを固定値入力しているのでそのうち直したい
@app.route('/updateScreenshot')
def updateScreenshot():
    print("update screenshot")
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        maxwidth, maxheight = pyautogui.size()
        im = pyautogui.screenshot()
        im.mode = 'RGBA'
        draw = ImageDraw.Draw(im)
        for y in range(0, maxheight, 100):
            for x in range(0, maxwidth, 100):
                rect = [x,y,x+100,y+100]
                draw.rectangle(rect, outline=(80,0,0))
        # im.show()
        im = numpy.array(im)
        im = im.tobytes()
    try:
        ws.send(im)
    except:
        print("some error in updateScreenshot")
    return ""
# ===================================================================================
## @brief ログ表示を更新
@app.route('/updateLog')
def updateLog():
    print("update log")
    global streamed_data
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        client_ip = str(request.environ['REMOTE_ADDR'])
        if not client_ip in streamed_data:
            streamed_data[client_ip] = []
        send_data = []
        lines = open(os.path.dirname(__file__)+"/../log/output.html", "r", encoding="utf-8").readlines()
        for line in lines:
            if not line in streamed_data[client_ip]:
                send_data.append(line)
    try:
        if send_data:
            ws.send(json.dumps({"data":send_data}))
            for data in send_data:
                streamed_data[client_ip].append(data)
            # for data in streamed_data[client_ip]:
            #     print(data)
    except:
        print("some error in updateLog")
    return ""
# ===================================================================================
if __name__ == "__main__":
    app.debug = True
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()
# ===================================================================================