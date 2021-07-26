# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import reply
import receive
from flask import Flask, request, current_app
import queue

SECRET_KEY = b'\xa7o\x83\x8f\x04~\xd6\xaf\xa1\xd5\x87\xb8&\x05\xbcf\x07\xed\xcd7H\xf7\x93\x8e'

app = Flask(__name__)
app.secret_key = SECRET_KEY

with app.app_context():
    current_app.que = queue.Queue(maxsize=10000)

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        try:
            signature = request.args.get('signature')
            timestamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            echostr = request.args.get('echostr')
            token = "Minsky123"

            lst = [token, timestamp, nonce]
            lst.sort()
            sha1 = hashlib.sha1()
            for item in lst:
                sha1.update(item.encode('utf-8'))
            hashcode = sha1.hexdigest()
            print("handle/GET func: hashcode, signature: ", hashcode, signature)
            if hashcode == signature:
                return echostr
            else:
                return ""
        except Exception as Argument:
            print(Argument)
            return str(Argument)
        # print('queue:',current_app.que.qsize(),'\nlist:',current_app.lst)
    elif request.method == 'POST':
        try:
            webData = request.data.decode('utf-8')
            # print("Handle Post webdata is ", webData)
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                content = recMsg.Content.decode('utf-8')
                if len(content) <= 30:
                    replyContent = "您的弹幕将经过筛选后发送~"
                    with app.app_context():
                        # print(content)
                        if current_app.que.full():
                            replyContent = "当前弹幕发送人数过多，请稍后重试~"
                        else:
                            current_app.que.put_nowait(content.replace('\n', ' '))
                else:
                    replyContent = "弹幕限制30字~"
                replyMsg = reply.TextMsg(toUser, fromUser, replyContent)
                return replyMsg.send()
            else:
                print('received without process')
                return 'success'
        except Exception as Argument:
            print(Argument)
            return str(Argument)


@app.route('/danmu', methods=['GET'])
def danmu():
    if request.method == 'GET':
        try:
            items = []
            with app.app_context():
                while not current_app.que.empty():
                    items.append(current_app.que.get())
            return '\n'.join(items)
        except Exception as Argument:
            print(Argument)
            return str(Argument)

if __name__ == '__main__':
    app.run()