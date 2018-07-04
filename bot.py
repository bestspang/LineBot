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


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)

if __name__ == "__main__":
    app.run()
