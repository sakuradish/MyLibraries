################################################################################
import os
import json
import pyautogui
import re
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, request, render_template
app = Flask(__name__)
streamed_data = {}
################################################################################
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
################################################################################
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
        lines = open(os.path.dirname(__file__)+"/../log/output.log", "r", encoding="utf-8").readlines()
        for line in lines:
            result = re.fullmatch("\[(.*?)\]\[(.*?)\]\[(.*?)\]\[(.*)\].*", line, re.S)
            line = "<div>"
            line += '[<span class="asctime">' + result.group(1) + "</span>]"
            line += '[<span class="levelname">' + result.group(2) + "</span>]"
            line += '[<span class="funcname">' + result.group(3) + "</span>]"
            line += '[<span class="' + result.group(2) + '">' + result.group(4) + "</span>]"
            line += "</div>"
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
################################################################################
if __name__ == "__main__":
    app.debug = True
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()
################################################################################