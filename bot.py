from flask import Flask, request, abort
import json, requests
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

line_bot_api = LineBotApi('Z7FgW5zgSO1G9BaHiMJOCKTByoH6Fl9gFIam59JdkfVXaavM8k8DEsEfLZpWmBlNDbWv/q4wYA0mY/gJWLfNUBFX8yNp+5A5THgSjLzx6DTLVi5x69Ejbd1JRLBOtiS7/HoOmKHJDvmmlDEt2DXj1QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1b8e881368efe90738ce5c3341898c35')

@app.route("/")
def hello():
    return "This is BP_LINEBOT!"

@app.route("/bot", methods=['POST'])
def bot():
        # ข้อความที่ต้องการส่งกลับ
    replyQueue = list()

    # ข้อความที่ได้รับมา
    msg_in_json = request.get_json()
    msg_in_string = json.dumps(msg_in_json)

    replyToken = msg_in_json["events"][0]['replyToken']

    userID =  msg_in_json["events"][0]['source']['userId']
    msgType =  msg_in_json["events"][0]['message']['type']

    if msgType != 'text':
        reply(replyToken, ['Only text is allowed.'])
        return 'OK',200


    text = msg_in_json["events"][0]['message']['text'].lower().strip()

    replyQueue.append('นี่คือรูปแบบข้อความที่รับส่ง')

    # ทดลอง Echo ข้อความกลับไปในรูปแบบที่ส่งไปมา (แบบ json)
    replyQueue.append(msg_in_string)
    reply(replyToken, replyQueue[:5])
    return 'OK', 200

def reply(replyToken, textList):

    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': LINE_API_KEY
    }
    msgs = []
    for text in textList:
        msgs.append({
            "type":"text",
            "text":text
        })
    data = json.dumps({
        "replyToken":replyToken,
        "messages":msgs
    })
    requests.post(LINE_API, headers=headers, data=data)
    return

if __name__ == "__main__":
    app.run()
