import gevent.monkey
gevent.monkey.patch_all()
from gevent.pywsgi import WSGIServer
from flask_socketio import SocketIO, emit
from flask import Flask, request, abort, send_from_directory, jsonify, render_template, url_for, copy_current_request_context
from oauth2client.service_account import ServiceAccountCredentials
import json, requests, random, os, errno, sys, configparser
import dialogflow, gspread, pprint, datetime, math, functools #tempfile
from time import sleep
import numpy as np
import pandas as pd
from pythainlp.tokenize import word_tokenize
from pythainlp.util import isthai
from bs4 import BeautifulSoup as soup
from html.parser import HTMLParser
from urllib.request import urlopen as uReq
from urllib.request import urlretrieve as uRet
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import *
from threading import Thread, Event

__author__ = 'bestspang'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

class RandomThread(Thread):
    def __init__(self):
        self.delay = 31
        self.otp = ""
        super(RandomThread, self).__init__()

    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of magical random numbers
        print("Making random numbers")
        #while not thread_stop_event.isSet():
        digits = "0123456789"
        number = ""
        for i in range(6):
            number += digits[math.floor(random.random() * 10)]
        os.environ["OTP_BACKUP"]=number
        print(number)
        return number
        #socketio.emit('newnumber', {'number': number}, namespace='/test')
        #sleep(self.delay)

    def timeCountdown(self):
        #infinite loop of magical random numbers
        print("Counting down")
        time = 0
        while not thread_stop_event.isSet():
            if time <= 0:
                time = self.delay
                number = self.randomNumberGenerator()
            time -= 1
            #print(time)
            socketio.emit('newnumber', {'number': number}, namespace='/test')
            socketio.emit('newtime', {'time': time}, namespace='/test')
            sleep(1)

    def run(self):
        #self.randomNumberGenerator()
        self.timeCountdown()

config = configparser.ConfigParser()
config.read("config.ini")
#info = [NICKNAME,FIRST_NAME,FN_TH,LAST_NAME,LN_TH,E_MAIL,PERSONAL_ID,DOB,ADDR,MOBILE_NO,BANK_S,BANK_NO,BRANCHES]
line_bot_api = LineBotApi(config['line_bot']['line_bot_api'])
handler = WebhookHandler(config['line_bot']['handler'])
#profile = line_bot_api.get_group_member_profile(group_id, user_id)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

os.environ["DIALOGFLOW_PROJECT_ID"]="bplinebot"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./BPLINEBOT-0106b42afbf3.json"

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('BPLINEBOT-57c70064e9b9.json', scope)
client = gspread.authorize(creds)

def check_opt(input, opt):
    if input == opt:
        return True
    else:
        return False

def is_working(input_id):
    sheet = client.open('userCheckin').worksheet('userStatus')
    user_id = sheet.col_values(2)[1:]
    return int(sheet.col_values(4)[1:][user_id.index(input_id)])

def who_work():
    sheet = client.open('userCheckin').worksheet('userStatus')
    user_name = sheet.col_values(3)[1:]
    text = ""
    is_in = sheet.col_values(4)[1:]
    is_in = [int(i) for i in is_in]
    if sum(is_in) > 0:
        text += "ที่ออฟฟิศมี : \n"
        for i in range(len(is_in)):
            if is_in[i] == 1:
                text += "{}\n".format(user_name[i])
        text += 'กำลังทำงานครับผม!'
    else:
        text = 'ไม่มีคนอยู่ที่ทำงานเลยครับ!'
    return text

def checkin_out(input_id, type):
    profile = line_bot_api.get_profile(input_id)
    now = datetime.datetime.now() + datetime.timedelta(seconds = 25200)
    sheet = client.open('userCheckin').worksheet('userStatus')
    user_id = sheet.col_values(2)[1:]
    user_name = sheet.col_values(3)[1:]
    sheet2 = client.open('userCheckin').worksheet('log')
    row_num = len(sheet2.col_values(1)[1:])
    #int(sheet.col_values(4)[1:][user_id.index(input_id)])
    # check is_in
    sheet.update_cell(user_id.index(input_id) + 2, 4, type)
    # update log
    row = [row_num + 1,now.strftime('%Y/%m/%d'),now.strftime("%I:%M %p"), user_id.index(input_id) + 1,type]
    index = row_num + 2
    sheet2.insert_row(row, index)
    to = "C374667ff440b48857dafb57606ff4600"
    if type == "1":
        text = "Check-In!"
    elif type == "0":
        text = "Check-out!"
    line_bot_api.push_message(to, TextSendMessage(text=profile.display_name + 'ได้ทำการ ' + text))

def member_rank(input):
    if is_member(input) and is_approve(input):
        sheet = client.open('lineUser').worksheet('user')
        user_id = sheet.col_values(3)[1:]
        return sheet.col_values(6)[1:][user_id.index(input)]
    else:
        return False

def is_member(input):
        sheet = client.open('lineUser').worksheet('user')
        pp = pprint.PrettyPrinter()
        user_id = sheet.col_values(3)[1:]
        if input in user_id:
            #sheet.col_values(4)[1:][user_id.index(input)]
            return True
        else:
            return False
        #pp.pprint(balance)
        #sheet = client.open('testSpreadsheet').sheet1
        #pp = pprint.PrettyPrinter()
        #sheet.update_cell(1, 1, newdata)

def is_approve(input):
        sheet = client.open('lineUser').worksheet('user')
        user_id = sheet.col_values(3)[1:]
        if input in user_id and sheet.col_values(4)[1:][user_id.index(input)] == "APPROVE":
            return True
        else:
            return False

def add_member(input):
        sheet = client.open('lineUser').worksheet('user')
        profile = line_bot_api.get_profile(input)
        now = datetime.datetime.now()
        row_num = len(sheet.col_values(3)[1:])
        row = [row_num + 1,profile.display_name, input, "WAITING", now.strftime('%Y/%m/%d'),"4",profile.picture_url]
        index = row_num + 2
        sheet.insert_row(row, index)
        to = "C374667ff440b48857dafb57606ff4600"
        #line_bot_api.push_message(to, TextSendMessage(text=profile.display_name + 'ได้สมัครสมาชิก!'))
        line_bot_api.reply_message(event.reply_token,
        TextSendMessage(text='กรุณากรอกข้อมูลของท่านตามลิงค์ด้านล่าง\nhttps://forms.gle/gXGxjsELh9hWy9Wx9'),
        TextSendMessage(text='ขอบคุณครับ'))

def is_approve_new_member():
    sheet = client.open('lineUser').worksheet('user')
    name = sheet.col_values(2)[-1]
    confirm_template = ConfirmTemplate(text='Approve หรือ ไม่?', actions=[
        PostbackAction(label='Yes',text='Yes!',data='member_yes'),
        PostbackAction(label='No',text='No!',data='member_no'),
    ])
    template_message = TemplateSendMessage(
        alt_text='Confirm alt text', template=confirm_template)
    to = "U7612d77bbca83f04d6acf5e27333edeb"
    line_bot_api.push_message(to, [TextSendMessage(text="คุณ "+name),
    TextSendMessage(text="สมาชิกใหม่ได้ทำการกรอกเอกสาร!\nจะ APPROVE หรือไม่?"),
    template_message])

def approve_member(boo):
    if boo == 1:
        sheet = client.open('lineUser').worksheet('user')
        row_num = len(sheet.col_values(3)[1:])
        sheet.update_cell(row_num+1, 4, "APPROVE")
        sheet.update_cell(row_num+1, 6, "1")
    else:
        pass

def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

def detect_intent_texts(project_id, session_id, text, language_code):
    import dialogflow_v2 as dialogflow
    # key_file_path = "./BPLINEBOT-0106b42afbf3.json"
    # credentials = Credentials.from_service_account_file(key_file_path)
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        return response.query_result.fulfillment_text

@app.route("/")
def hello():
    #return "This is BP_LINEBOT2 (Mr.Doge)!"
    return render_template('index.html')

@app.route("/notify")
def call_func():
    is_approve_new_member()
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

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

@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

@app.route('/images/<path:path>')
def send_images_content(path):
    return send_from_directory('images', path)
# @app.route('/get_movie_detail', methods=['POST'])
#     def get_movie_detail():
#         data = request.get_json(silent=True)
#         movie = data['queryResult']['parameters']['movie']
#         api_key = os.getenv('OMDB_API_KEY')
#
#         movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
#         movie_detail = json.loads(movie_detail)
#         response =  """
#             Title : {0}
#             Released: {1}
#             Actors: {2}
#             Plot: {3}
#         """.format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])
#
#         reply = {
#             "fulfillmentText": response,
#         }
#
#         return jsonify(reply)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'th')
    response_text = { "message":  fulfillment_text }
    return jsonify(response_text)

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
    data = json.loads(site_request.text)

    quote = data['contents']['quotes']
    quote = [quote[0]['quote'], quote[0]['author']]
    quote = "{} - {}".format(quote[0], quote[1])
    print(quote)
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
        if isthai(lists[i])['thai'] == 0: ### TO FIX TypeError: 'bool' object is not subscriptable
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
    global number
    text = event.message.text.lower()
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

    if 'ขอ' in words_list and ('balance' in words_list or 'ยอดเงิน' in words_list):
        sheet = client.open('AbbokIncomeAssesmentV02').sheet1
        pp = pprint.PrettyPrinter()
        balance = sheet.cell(23, 2).value
        #pp.pprint(balance)
        price = "ยอดเงินในบัญชีตอนนี้มีทั้งหมด {} บาทครับผม!".format(balance)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=price))
        return 0

    if 'ขอ' in words_list and ('สรุปค่าใช้จ่าย' in text):
        urls = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFS69FbmZBwkmCWtGWwDrA7YJyEpAmMyLHZ07FACjet8gxVX5WZ0DtVy2yW644QkY4d8UGctjfej0s/pubchart?oid=1508988021&format=image"
        headers = requests.utils.default_headers()
        headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',})
        #site_request = requests.get(url, headers=headers)
        uRet(urls, "static/image.png")
        sheet = client.open('AbbokIncomeAssesmentV02').worksheet("Summary2")
        #pp = pprint.PrettyPrinter()
        expense = sheet.cell(3, 14).value
        income = sheet.cell(2, 14).value

        #pp.pprint(balance)
        price = "รายจ่ายทั้งหมด {} บาท\nรายรับทั้งหมด {} บาท".format(expense, income)

        url = request.url_root + '/static/image.png'
        app.logger.info("url=" + url)
        line_bot_api.reply_message(
            event.reply_token,
            [
            ImageSendMessage(url, url),
            TextSendMessage(text=price)
            ]
        )

        return 0

    if 'ขอ' in words_list and ('เงินเดือน' in words_list or 'รายได้' in words_list):
        name = ["best", "แทน", "ทีม", "snook"]
        usern = None
        for i in words_list:
            if i in name:
                usern = i
        if usern == None:
            price = "กรุณาบอกชื่อด้วยครับ"
        else:
            sheet = client.open('AbbokIncomeAssesmentV02').get_worksheet(2)
            pp = pprint.PrettyPrinter()
            num = name.index(usern)
            balance = sheet.cell(num+2, 9).value
            #pp.pprint(balance)
            price = "เงินเดือนของ {} จะได้รับในเดือนนี้ {} บาทครับผม!".format(usern, balance)

        usern = None
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=price))
        return 0

    if ('เพิิ่ม' in words_list or 'add' in words_list) and ('ข้อมูล' in words_list or 'data' in words_list):
        newdata = text.split(' ')[-1]
        sheet = client.open('testSpreadsheet').sheet1
        pp = pprint.PrettyPrinter()
        sheet.update_cell(1, 1, newdata)
        # row = ["I'm","inserting","a","new","row","into","a,","Spreadsheet","using","Python"]
        # index = 3
        # sheet.insert_row(row, index)
        # sheet.row_count
        # sheet.delete_row(1)
        balance = sheet.cell(1, 1).value
        price = "เปลี่ยนข้อมูลเป็น : {} ".format(balance)

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

    if 'คำคม' in words_list or 'quote' in words_list:
        price = 'นี้คือระบบ test ครับ'
        quote = getQuote()
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text=price))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=quote))
        return 0
#fix google dialogflow
    if 'ทดลอง' in words_list:
        if 'ทดลอง ' in text:
            price = 'นี้คือระบบ test : '
            textn = text.replace('ทดลอง ', '').replace('test ', '')
            project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
            try:
                fulfillment_text = detect_intent_texts(project_id, "unique", textn, 'th')
            except:
                fulfillment_text = "ระบบผิดพลาด"
                pass
            response_text = fulfillment_text
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response_text))
        return 0

# test decorator

    if 'check' in words_list or 'checkin' in words_list:
        rank = member_rank(event.source.user_id)
        response_text = "รหัส(code)ไม่ถูกต้องครับ!"
        if rank in "01":
            if not is_working(event.source.user_id):
                if 'check ' in text or 'checkin ' in text:
                    textn = text.replace('checkin ', '').replace('check ', '')
                    try:
                        int(textn)
                    except:
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="กรุณาพิมพ์ check หรือ checkin\nตามด้วยเว้นวรรคและเลข 6 หลักครับ!"))
                        return 0

                    number = os.getenv('OTP_BACKUP')
                    if check_opt(textn, number) and textn is not None and len(textn) == 6:
                        checkin_out(event.source.user_id,"1")
                        response_text = "Check in สำเร็จแล้วครับ!"
                    else:
                        response_text = "รหัสที่คุณป้อน "+ textn + " ไม่ถูกต้อง!"
                else:
                    response_text = "กรุณาพิมพ์ check หรือ checkin ตามด้วยเว้นวรรคและเลข 6 หลักครับ!"
            else:
                response_text = "ไม่สามารถ check-in ได้เนื่องจากท่านยังไม่ได้ทำการ check-out!"
        else:
            response_text = "เฉพาะพนักงานที่มีสิิทธิ์ใช้คำสั่งดังกล่าว! rank: " + rank
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text))
        return 0

    if 'out' in words_list or 'checkout' in words_list:
        rank = member_rank(event.source.user_id)
        response_text = "รหัส(code)ไม่ถูกต้องครับ!"
        if rank in "01":
            if is_working(event.source.user_id):
                checkin_out(event.source.user_id,"0")
                response_text = "Check out สำเร็จแล้วครับ!"
            else:
                response_text = "ไม่สามารถ check-out ได้เนื่องจาก\nท่านยังไม่ได้ทำการ check-in!"
        else:
            response_text = "เฉพาะพนักงานที่มีสิิทธิ์ใช้คำสั่งดังกล่าว! rank: " + rank
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text))
        return 0

    if text == '!test':
        #is_approve_new_member()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))
        return 0

    if text == '!help':
        helpt = ["[จำเป็น]\n'!help'\n'check'or'checkin'-OTP\n'out'or'checkout'\n'ขอ'&ยอดเงิน'or'balance'\n'ขอ'&'เงินเดือน'or'รายได้'-\n'ขอ'&'ฟอร์ม'or'แบบฟอร์ม'\n'ขอ'&'เมนู'or'เมนูอื่นๆ'\n'ขอสรุปค่าใช้จ่าย'",
        "[ทั่วไป]\n'Abbok'\n'member'\n'ใคร'&'ทำงานอยู่'or'อยู่ที่ทำงาน'\n'trackid'or'รหัส'-รหัสไปรษณี\n'ราคา'or'หุ้น'-QUOTE\n'คำคม'or'quote'",
        "[ทดลอง]\n'!test'\n'เพิ่มข้อมูล'or'add data'-data\n'ทดลอง'-ประโยคเพื่อคุย\n'cast'or'castto'-t\n'profile'"]
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(text=helpt[0]),
            TextSendMessage(text=helpt[1]),
            TextSendMessage(text=helpt[2])])
        return 0

    if 'ใคร' in words_list and ('ทำงานอยู่' in text or 'อยู่ที่ทำงาน' in text):
        text == who_work()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))
        return 0

    #if text[:2] == 'is' and (text[2:6] == 'work' or text[2:9] == 'working'):
    #if 'iswork' in text:
    # if text[:2] == 'is' and (text[2:6] == 'work' or text[2:9] == 'working'):
    #     name = ["best", "taan", "team", "snook"]
    #     newdata = text.split(' ')[-1]
    #     sheet = client.open('userCheckin').worksheet('userStatus')
    #     user_id = sheet.col_values(2)[1:]
    #     text = "กรุณาเพิ่มคำสั่ง [-a, -n] หรือ ชื่อบุคคล"
    #     if newdata[0] == '-':
    #         if newdata[1] == 'a':
    #             user_name = sheet.col_values(3)[1:]
    #             is_in = [int(i) for i in sheet.col_values(4)[1:]]
    #             if sum(is_in) > 0:
    #                 text += "ที่ออฟฟิศมี\n"
    #                 for i in range(len(is_in)):
    #                     if is_in[i] == 1:
    #                         text += "{} กำลังทำงาน\n".format(user_name[i])
    #                     text += 'ครับผม!'
    #             else:
    #                 text = 'ไม่มีคนอยู่ที่ทำงานเลยครับ!'
    #
    #             #print all people who is working
    #     elif newdata in name:
    #         pass
    #         # find user_id from actual name
    #         #get user_id
    #         #int(sheet.col_values(4)[1:][user_id.index(input)])
    #         #is_working(user_id)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=text))
    #     return 0

    if 'cast' in words_list or 'castto' in words_list:
        rank = member_rank(event.source.user_id)
        if rank in "0":
            if 'cast ' in text or 'castto ' in text:
                textn = text.replace('cast ', '').replace('castto ', '')
                to = "C374667ff440b48857dafb57606ff4600"
                line_bot_api.push_message(to, TextSendMessage(text=textn))
            else:
                response_text = "กรุณาพิมพ์ cast หรือ castto\nตามด้วยประโยคที่ต้องการเผยแพร่!"
        else:
            response_text = "เฉพาะพนักงานที่มีสิิทธิ์ใช้คำสั่งดังกล่าว! rank: " + rank

        return 0

    ce = random.randint(1,10)
    if 'แบม' in words_list or 'บี้' in words_list:
        texts = ['ตูดหมึก', 'ปากห้อย', 'อ้วน', 'ขี้โม้', 'ไม่เชื่อ!', 'เด็กอ้วน', 'แก้มดุ่ย', 'บี้']
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=texts[random.randint(0,7)]))
        return 0

    if 'บุ๊ค' in words_list or 'book' in words_list or 'บุ๊ก' in words_list:
        texts = ['ตูดหมึก', 'จังกะเป', 'อ้วน', 'ขี้โม้', 'ไม่เชื่อ!', 'เด็กแว๊น', 'กิ๊บป่อง', 'ผีบ้า']
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=texts[random.randint(0,7)]))
        return 0

    ##################
    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='User id: ' + event.source.user_id),
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + profile.status_message)
                ]
            )

        elif isinstance(event.source, SourceGroup):
            #member_ids_res = line_bot_api.get_group_member_ids(event.source.group_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text="Bot is in a Group!"),
                    TextSendMessage(text='Group id: ' + event.source.group_id),
                    #TextSendMessage(text='Member ids: ' + str(member_ids_res.member_ids))
                ]
            )

        elif isinstance(event.source, SourceRoom):
            #member_ids_res = line_bot_api.get_room_member_ids(event.source.room_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text="Bot is in a Room!"),
                    TextSendMessage(text='Room id: ' + event.source.room_id),
                    #TextSendMessage(text='Member ids: ' + str(member_ids_res.member_ids))
                ]
            )

        else:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text="Bot can't use profile API without user ID")
                ]
            )

    if text == 'member':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            member = "You are not a member!"
            if is_member(event.source.user_id) and is_approve(event.source.user_id):
                member = "You are a member!"
                carousel_template = CarouselTemplate(columns=[
                    CarouselColumn(text='Member Setting', title='เมนูหลัก', actions=[
                        URIAction(label='ข้อมูลสมาชิก', uri='https://www.google.com'),
                        URIAction(label='เปลี่ยนแปลงข้อมูล', uri='https://www.google.com'),
                        PostbackAction(label='Coming soon..', data='comingsoon')
                    ]),
                ])
                template_member = TemplateSendMessage(
                    alt_text='Carousel alt text', template=carousel_template)
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='Hello! ' + profile.display_name),
                        TextSendMessage(text=member),
                        template_member
                    ]
                )
            elif is_member(event.source.user_id) and not is_approve(event.source.user_id):
                member = "your application is waiting to be approve!\nplease wait!"
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='Hello! ' + profile.display_name),
                        TextSendMessage(text=member)
                    ]
                )
            else:
                confirm_template = ConfirmTemplate(text='ต้องการสมัครสมาชิกหรือไหม?', actions=[
                    PostbackAction(label='Yes',text='Yes!',data='yes'),
                    PostbackAction(label='No',text='No!',data='no'),
                    #MessageAction(label='Yes', text='Yes!'),
                    #MessageAction(label='No', text='No!'),
                ])
                template_message = TemplateSendMessage(
                    alt_text='Confirm alt text', template=confirm_template)
                line_bot_api.reply_message(event.reply_token, [
                    TextSendMessage(text='Hello! ' + profile.display_name),
                    TextSendMessage(text=member),
                    template_message
                ])
                print(event.message.text.lower())

        elif isinstance(event.source, SourceGroup):
            #member_ids_res = line_bot_api.get_group_member_ids(event.source.group_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text="Bot is in a Group!"),
                    TextSendMessage(text='Group id: ' + event.source.group_id),
                    #TextSendMessage(text='Member ids: ' + str(member_ids_res.member_ids))
                ]
            )

    elif text == 'quota':
        quota = line_bot_api.get_message_quota()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='type: ' + quota.type),
                TextSendMessage(text='value: ' + str(quota.value))
            ]
        )
    elif text == 'quota_consumption':
        quota_consumption = line_bot_api.get_message_quota_consumption()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='total usage: ' + str(quota_consumption.total_usage)),
            ]
        )
    elif text == 'push':
        line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text='PUSH!'),
            ]
        )
    elif text == 'multicast':
        line_bot_api.multicast(
            [event.source.user_id], [
                TextSendMessage(text='THIS IS A MULTICAST MESSAGE'),
            ]
        )
    elif text == 'broadcast':
        line_bot_api.broadcast(
            [
                TextSendMessage(text='THIS IS A BROADCAST MESSAGE'),
            ]
        )
    elif text.startswith('broadcast '):  # broadcast 20190505
        date = text.split(' ')[1]
        print("Getting broadcast result: " + date)
        result = line_bot_api.get_message_delivery_broadcast(date)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='Number of sent broadcast messages: ' + date),
                TextSendMessage(text='status: ' + str(result.status)),
                TextSendMessage(text='success: ' + str(result.success)),
            ]
        )
    elif text == 'bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't leave from 1:1 chat"))

    elif text == 'image':
        url = request.url_root + '/static/doge.jpg'
        app.logger.info("url=" + url)
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(url, url)
        )
    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Do it?', actions=[
            MessageAction(label='Yes', text='Yes!'),
            MessageAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'buttons':
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping'),
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif 'ขอ' in words_list and ('ฟอร์ม' in words_list or 'แบบฟอร์ม' in words_list):
        buttons_template = ButtonsTemplate(
            title='แบบฟอร์มต่างๆ', text='โปรดเลือกด้านล่าง', actions=[
                URIAction(label='ใบลา', uri='https://forms.gle/hnrN52QHrwdMZwBy6'),
                URIAction(label='ใบติดต่อลูกค้า', uri='https://forms.gle/qheFfQVA2chNTfRD9'),
                URIAction(label='ใบเบิกเงิน', uri='https://forms.gle/junKJvXto2wXmm5e7'),
                URIAction(label='ใบ Feed Back', uri='https://forms.gle/JfWnr2oRdoXrnXmL8')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif 'ขอ' in words_list and ('เมนู' in words_list or 'เมนูอื่นๆ' in words_list):
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='Page 1', title='เมนูหลัก', actions=[
                URIAction(label='ไปยัง NAS', uri='http://bestspang.quickconnect.to'),
                URIAction(label='Trello', uri='https://trello.com/b/0WqzlKN6'),
                PostbackAction(label='ใบร่างใบเสนอราคา', data='comingsoon')
            ]),
            CarouselColumn(text='Page 2', title='อื่นๆ', actions=[
                URIAction(label='Abbok Login', uri='https://www.abbok.net/login'),
                URIAction(label='Fact Sheet', uri='https://docs.google.com/spreadsheets/d/1VEkNq4wPStfJ6Zfp3BOluY3hAkoP1V2AwkOmMImDU7o/edit?usp=sharing'),
                PostbackAction(label='ไม่มีไร', data='nothing')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'carousel':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping'),
                MessageAction(label='ใบร่างใบเสนอราคา', text='Coming Soon!'),
                MessageAction(label='ไม่มีไร', text='จ่ะ')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'image_carousel':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='datetime',
                                                            data='datetime_postback',
                                                            mode='datetime')),
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='date',
                                                            data='date_postback',
                                                            mode='date'))
        ])
        template_message = TemplateSendMessage(
            alt_text='ImageCarousel alt text', template=image_carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'imagemap':
        pass
    elif text == 'Abbok':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url=request.url_root + '/images/shopFront.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='https://www.abbok.net', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='ABBOK Office', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            #IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            #IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            #IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            #IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            #IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='Design and Technology', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='สวนหลวงสแควร์ ซอยจุฬาฯ 5 ถนนพระราม 1, กทมฯ',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 18:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:0912501735'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://www.abbok.net")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="Abbok's Infomation", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif text == 'quick_reply':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Quick reply',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="label1", data="data1")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="label2", text="text2")
                        ),
                        QuickReplyButton(
                            action=DatetimePickerAction(label="label3",
                                                        data="data3",
                                                        mode="date")
                        ),
                        QuickReplyButton(
                            action=CameraAction(label="label4")
                        ),
                        QuickReplyButton(
                            action=CameraRollAction(label="label5")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="label6")
                        ),
                    ])))
    else:
        pass

    ########## NEW #############

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'comingsoon':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='ระบบมาเร็วๆนี้ โฮ่งง'))
    elif event.postback.data == 'nothing':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='กดหาdad'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))

    elif event.postback.data == 'yes':
        txt = 'ใจเย็นๆโฮ่ง!\nส่งข้อมูลไปแล้วจ้า!'
        if not is_member(event.source.user_id):
            add_member(event.source.user_id)
            txt = 'บันทึกสมาชิกเรียบร้อย!\nกรุณารอการยืนยัน!'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=txt))
    elif event.postback.data == 'no':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='โอเคโฮ่งง!'))

    elif event.postback.data == 'member_yes':
        approve_member(1)
        txt = 'ยืนยันสมาชิกเรียบร้อย!'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=txt))
    elif event.postback.data == 'member_no':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='โอเคโฮ่งง!'))



@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))


# @handler.add(MemberJoinedEvent)
# def handle_member_joined(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(
#             text='Got memberJoined event. event={}'.format(
#                 event)))
#
#
# @handler.add(MemberLeftEvent)
# def handle_member_left(event):
#     app.logger.info("Got memberLeft event")



    ##################

    if ce > 6 and ce < 9:
        text = ['ตูดหมึก', 'หอย', 'WTF!', 'ขี้โม้', 'ไม่เชื่อ!', 'แม่ย้อย', 'พ่อง', 'โฮ่งง', 'สลัดผัก']
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text[random.randint(0,8)]))

if __name__ == "__main__":
    make_static_tmp_dir()
    socketio.run(app)
    #app.run()
