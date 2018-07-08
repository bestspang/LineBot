from flask import Flask, request, abort
import json, requests, random, os
import dialogflow
from pythainlp.tokenize import word_tokenize
from bs4 import BeautifulSoup as soup
from html.parser import HTMLParser
from urllib.request import urlopen as uReq
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

def extractWord(text):
    a = word_tokenize(alist, engine='newmm')
    b = []
    for h in a:
        if h != ' ':
            b.append(h)
    return b

def checkth(lists):
    for i in range(len(lists)):
        if isthai(lists[i])['thai'] == 0:
            return lists[i]
    return 0

def stockPrice(stock_quote):
    if stock_quote == 0:
        return 0
    stock_quote = stock_quote.upper()
    url = 'https://www.settrade.com/C04_01_stock_quote_p1.jsp?txtSymbol='+ stock_quote +'&ssoPageId=9&selectPage=1'
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    price = page_soup.findAll("div", {"class":"col-xs-6"})
    try:
        price = price[2].text.strip()
        return ('หุ้น {} ราคาปัจจุบันอยู่ที่ {} บาท'.format(stock_quote, price))
    except:
        return ('ไม่มีข้อมูลหุ้นตัวนี้')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    words_list = extractWord(event.message.text)
    if 'หุ้น' in words_list and 'ราคา' in words_list:
        price = (stockPrice(checkth(words_list)))
        if price == None:
            return 0
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=price))
        return 0
    ce = random.randint(1,10)

    if ce > 6 and ce < 9:
        line_bot_api.reply_message(
            event.reply_token,
            #TextSendMessage(text=event.message.text)
            text = ['ตูดหมึก', 'หอย', 'WTF!', 'ขี้โม้', 'ไม่เชื่อ!', 'แม่ย้อย', 'พ่อง', 'โฮ่งง', 'สลัดผัก']
            TextSendMessage(text=text[random.randint(0,8)])

if __name__ == "__main__":
    app.run()
