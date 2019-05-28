from flask import Flask, request, abort, send_from_directory, jsonify, render_template
import json, requests, random, os, errno, sys, tempfile
import dialogflow, pusher
import numpy as np
import pandas as pd
from pythainlp.tokenize import word_tokenize, isthai
from bs4 import BeautifulSoup as soup
from html.parser import HTMLParser
from urllib.request import urlopen as uReq
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

app = Flask(__name__)

line_bot_api = LineBotApi('Z7FgW5zgSO1G9BaHiMJOCKTByoH6Fl9gFIam59JdkfVXaavM8k8DEsEfLZpWmBlNDbWv/q4wYA0mY/gJWLfNUBFX8yNp+5A5THgSjLzx6DTLVi5x69Ejbd1JRLBOtiS7/HoOmKHJDvmmlDEt2DXj1QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1b8e881368efe90738ce5c3341898c35')
#profile = line_bot_api.get_group_member_profile(group_id, user_id)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

def detect_intent_texts(project_id, session_id, text, language_code):
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
    return "This is BP_LINEBOT2 (Mr.Doge)!"

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

    if 'ทดลอง' in words_list or 'test' in words_list:
        price = 'นี้คือระบบ test ครับ'
        textn = text.replace('ทดลอง ', '').replace('test ', '')
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=price))
        print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./path_to.json"
        project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
        fulfillment_text = detect_intent_texts(project_id, "unique", textn, 'th')
        response_text = fulfillment_text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text))
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
                URIAction(label='ใบลา', uri='https://forms.gle/wjE4tsFsVSGKcnH26'),
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
    elif text == 'flex':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
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
                                        text='Shinjuku, Tokyo',
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
                                        text="10:00 - 23:00",
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
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
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
    app.run()
