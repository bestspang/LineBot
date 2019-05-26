from flask import Flask, request, abort
import json, requests, random, os
import dialogflow
import numpy as np
import pandas as pd
from pythainlp.tokenize import word_tokenize, isthai
from bs4 import BeautifulSoup as soup
from html.parser import HTMLParser
from urllib.request import urlopen as uReq
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

line_bot_api = LineBotApi('Z7FgW5zgSO1G9BaHiMJOCKTByoH6Fl9gFIam59JdkfVXaavM8k8DEsEfLZpWmBlNDbWv/q4wYA0mY/gJWLfNUBFX8yNp+5A5THgSjLzx6DTLVi5x69Ejbd1JRLBOtiS7/HoOmKHJDvmmlDEt2DXj1QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1b8e881368efe90738ce5c3341898c35')
#profile = line_bot_api.get_group_member_profile(group_id, user_id)

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

def getData(track_id):
    if track_id == 0:
        return 0
    print("\n")
    url = 'https://th.kerryexpress.com/th/track/?track=' + track_id
    print("connecting.. : " + url + "\n")

    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',})
    site_request = requests.get(url, headers=headers)
    site_content = soup(site_request.content, "html.parser")
    site_data = site_content.findAll("div", {"class":"col colStatus"})
    return site_data

def getQuote():
    print("\n")
    url = 'http://quotes.rest/qod.json'
    print("connecting.. : " + url + "\n")

    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',})
    site_request = requests.get(url, headers=headers)
    site_content = soup(site_request.content, "html.parser")
    data = json.loads(site_request.text)

    quote = data['contents']['quotes']
    quote = [quote[0]['quote'], quote[0]['author']]
    quote = "{} - {}".format(quote[0], quote[1])
    return quote

def cleanData(site_data, ind=0):
    list = []
    lay1 = ['status piority-success', 'status normaly-waiting']
    lay2 = ['date', 'd1', 'd2']
    for i in range(len(lay1)):
        status = site_data[0].findAll("div", {"class":lay1[i]})
        if status is not None:
            for j in range(len(status)):
                for k in range(len(lay2)):
                    data = status[j].findAll("div", {"class":lay2[k]})
                    if k == 0:
                        data = data[0].findAll("div")
                        data = [data[m].text.replace(' ', '').strip() for m in range(2)]
                        data = [''.join(data[n].split('e')[1:3]) for n in range(2)]
                    elif k == 1 and i == 0:
                        data = data[0].text.replace(' ', '').strip()
                        data = [data.split('(')[0],data. split('(')[1].split(')')[0], data.split('\n')[2]]
                    elif k == 1 and i != 0:
                        data = data[0].text.replace(' ', '').strip()
                        data = [data, None, None]
                    else:
                        data = data[0].text.replace(' ', '').strip()
                        data = [data]

                    list.append(data)
    return list

def list_flatten(l, a=None):
    if a is None:
        a = []
    for i in l:
        if isinstance(i, list):
            list_flatten(i, a)
        else:
            a.append(i)
    return a

def makeNP(outlist):
    head_list = ['date', 'time', 'status', 'receiver', 'name', 'city']
    num = int(len(outlist) / 6)
    a = np.array(outlist)
    a = a.reshape((num, 6))
    return a

def extractWord(text):
    a = word_tokenize(text, engine='newmm')
    b = []
    for h in a:
        if h != ' ':
            b.append(h.lower())
    return b

def getSymbol(lists):
    for i in range(len(lists)):
        if isthai(lists[i])['thai'] == 0:
            return lists[i].upper()
    return 0

def getTable(stock_quote):
    if stock_quote == 0:
        return 0
    #url = 'http://www.settrade.com/C13_MarketSummary.jsp?detail=SET50'
    url = 'https://www.settrade.com/C04_01_stock_quote_p1.jsp?txtSymbol='+ stock_quote +'&ssoPageId=9&selectPage=1'
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    return page_soup.findAll("div", {"class":"col-xs-6"})#("table", {"class":"table table-info"})

def stockPrice(stock_quote):
    if stock_quote == 0 or stock_quote == None:
        return 0
    price = getTable(stock_quote)
    try:
        price = price[2].text.strip()
        text = ('หุ้น {} ราคาปัจจุบันอยู่ที่ {} บาท'.format(stock_quote, price))
        return (text, price)
    except:
        return ('ไม่มีข้อมูลหุ้นตัวนี้', None)

def makeDF(soupdata, ind=0):
    row_list = []
    head_list = []
    tr_list = soupdata[ind].findAll('tr')
    for tr in tr_list:
            th_list = tr.findAll('th')
            if th_list is not None:
                for th in th_list:
                    head_list.append(th.text.replace(' ', '').strip().split('\r')[0])
            td_list = tr.findAll('td')

            for td in td_list:
                row_list = np.append(row_list, td.text.replace(' ', '').strip())
    head_list[0] = 'SYMBOL'
    num_col = len(head_list)
    total_col = int(len(row_list)/num_col)
    row_list = np.reshape(row_list, (total_col, num_col) )
    return pd.DataFrame(columns = head_list, data = row_list)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    words_list = extractWord(event.message.text)
    if 'หุ้น' in words_list or 'ราคา' in words_list:
        symbo = getSymbol(words_list)
        price, money = stockPrice(symbo)
        if symbo == 'SET' or symbo == 'SET50':
            price = 'กำลังอัพเดทระบบ SET ค่ะหนูน้อย ใจเย็นๆ'
        elif price == 0:
            return 0
        else:
            if not is_number(money):
                price = 'ราคายังไม่มีการอัพเดทครัช'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=price))
        return 0

    if 'trackid' in words_list or 'รหัส' in words_list:
        #'รหัส SMLp000341000'.split(' ')[1].upper()
        price = 0
        if len(event.message.text.split(' ')) > 2:
            price = "โปรดพิม'รหัส'เว้นวรรคและตามด้วย'Track ID'"
        elif len(event.message.text.split(' ')) == 1:
            price = "รหัสอะไรฟะ บอกกูด้วย"
        else:
            track_id = event.message.text.split(' ')[1].upper()
            data = getData(track_id)
            clean_data = cleanData(data)
            flat_data = list_flatten(clean_data)
            np = makeNP(flat_data)
            if str(np[0][3]) == 'None':
                price = ('ขณะนี้{} เมื่อวันที่ {} เวลา {} ที่จังหวัด{}'.format(np[0][2], np[0][0], np[0][1], np[0][5]))
            else:
                price = ('ขณะนี้{} เมื่อวันที่ {} เวลา {} โดยคุณ{} ที่จังหวัด{}'.format(np[0][2], np[0][0], np[0][1], np[0][3], np[0][5]))

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=price))
        return 0

    if event.message.text.lower().replace(' ','') == 'Most Active Value'.lower().replace(' ',''):
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='Most Active Value'))
        return 0
    if event.message.text.lower().replace(' ','') == 'Most Active Volume'.lower().replace(' ',''):
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='Most Active Volume'))
        return 0
    if event.message.text.lower().replace(' ','') == 'Top Gainers'.lower().replace(' ',''):
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='Top Gainers'))
        return 0
    if event.message.text.lower().replace(' ','') == 'Top Losers'.lower().replace(' ',''):
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='Top Losers'))
        return 0

    if 'ทดลอง' in words_list or 'test' in words_list:
        price = 'นี้คือระบบ test ครับ'
        quote = getQuote()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=price))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=quote))
        return 0

    ce = random.randint(1,10)
    if 'แบม' in words_list or 'บี้' in words_list:
        text = ['ตูดหมึก', 'ปากห้อย', 'อ้วน', 'ขี้โม้', 'ไม่เชื่อ!', 'เด็กอ้วน', 'แก้มดุ่ย', 'บี้']
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text[random.randint(0,7)]))
        return 0

    if ce > 6 and ce < 9:
        text = ['ตูดหมึก', 'หอย', 'WTF!', 'ขี้โม้', 'ไม่เชื่อ!', 'แม่ย้อย', 'พ่อง', 'โฮ่งง', 'สลัดผัก']
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text[random.randint(0,8)]))

if __name__ == "__main__":
    app.run()
