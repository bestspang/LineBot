from flask import Flask, request, abort
import json, requests, random
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

line_bot_api = LineBotApi('Z7FgW5zgSO1G9BaHiMJOCKTByoH6Fl9gFIam59JdkfVXaavM8k8DEsEfLZpWmBlNDbWv/q4wYA0mY/gJWLfNUBFX8yNp+5A5THgSjLzx6DTLVi5x69Ejbd1JRLBOtiS7/HoOmKHJDvmmlDEt2DXj1QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1b8e881368efe90738ce5c3341898c35')

@app.route("/")
def hello():
    return "This is BP_LINEBOT2!"

@app.route("/bot", methods=['POST'])
def bot():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = ['ตูดหมึก', 'หอย', 'WTF!', 'ขี้โม้', 'ไม่เชื่อ!', 'แม่ย้อย', 'พ่อง', 'โฮ่งง', 'สลัดผัก']
    ce = random.randint(1,10)
    if ce > 6 and ce < 9:
        line_bot_api.reply_message(
            event.reply_token,
            #TextSendMessage(text=event.message.text)
            TextSendMessage(text=text[random.randint(0,8)]))

if __name__ == "__main__":
    app.run()
