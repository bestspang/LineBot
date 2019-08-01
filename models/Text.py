from oauth2client.service_account import ServiceAccountCredentials
from models.Member import Member
from models.Tools import Vote, Tools, RandomThread, Hoon
import requests, random

class Text:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

    def detect_intent_texts(self, session_id, text, language_code):
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

    def message_handler(self, event):
        text = event.message.text.lower()
        words_list = tools.extractWord(event.message.text)

        if 'หุ้น' in words_list or 'ราคา' in words_list:
            symbol = hoon.getSymbol(words_list)
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=symbol))
            return 0

        if 'trackid' in words_list or 'รหัส' in words_list:
            price = hoon.get_shipping_stat(event.message.text)
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=price))
            return 0

        if 'ขอ' in words_list and ('balance' in words_list or 'ยอดเงิน' in words_list):
            sheet = client.open('AbbokIncomeAssesmentV02').sheet1
            pp = pprint.PrettyPrinter()
            balance = sheet.cell(23, 2).value
            #pp.pprint(balance)
            price = f'ยอดเงินในบัญชีตอนนี้มีทั้งหมด {balance} บาทครับผม!'
            self.line_bot_api.reply_message(
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
            self.line_bot_api.reply_message(
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
            self.line_bot_api.reply_message(
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

            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=price))
            return 0

        if event.message.text.lower().replace(' ','') == 'Most Active Value'.lower().replace(' ',''):
            self.line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text='Most Active Value'))
            return 0
        if event.message.text.lower().replace(' ','') == 'Most Active Volume'.lower().replace(' ',''):
            self.line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text='Most Active Volume'))
            return 0
        if event.message.text.lower().replace(' ','') == 'Top Gainers'.lower().replace(' ',''):
            self.line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text='Top Gainers'))
            return 0
        if event.message.text.lower().replace(' ','') == 'Top Losers'.lower().replace(' ',''):
            self.line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text='Top Losers'))
            return 0

        if 'คำคม' in words_list or 'quote' in words_list:
            price = 'นี้คือระบบ test ครับ'
            quote = tools.getQuote()
            # self.line_bot_api.reply_message(
            #     event.reply_token,
            #     TextSendMessage(text=price))
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=quote))
            return 0
    #fix google dialogflow
        if 'ทดลอง' in words_list:
            if 'ทดลอง ' in text:
                price = 'นี้คือระบบ test : '
                textn = text.replace('ทดลอง ', '').replace('test ', '')
                project_id = config['DIALOGFLOW_PROJECT_ID']['id']
                try:
                    fulfillment_text = self.detect_intent_texts(project_id, "unique", textn, 'th')
                except:
                    fulfillment_text = "ระบบผิดพลาด"
                    pass
                response_text = fulfillment_text
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=response_text))
            return 0

    # test decorator

        if 'check' in words_list or 'checkin' in words_list:
            rank = mem.member_rank(event.source.user_id)
            response_text = "รหัส(code)ไม่ถูกต้องครับ!"
            if rank in "01":
                if not mem.is_working(event.source.user_id):
                    if 'check ' in text or 'checkin ' in text:
                        textn = text.replace('checkin ', '').replace('check ', '')
                        try:
                            int(textn)
                        except:
                            self.line_bot_api.reply_message(event.reply_token,TextSendMessage(text="กรุณาพิมพ์ check หรือ checkin\nตามด้วยเว้นวรรคและเลข 6 หลักครับ!"))
                            return 0

                        number = os.getenv('OTP_BACKUP')
                        if Tools.check_opt(textn, number) and textn is not None and len(textn) == 6:
                            mem.checkin_out(event.source.user_id,"1")
                            response_text = "Check in สำเร็จแล้วครับ!"
                        else:
                            response_text = "รหัสที่คุณป้อน "+ textn + " ไม่ถูกต้อง!"
                    else:
                        response_text = "กรุณาพิมพ์ check หรือ checkin ตามด้วยเว้นวรรคและเลข 6 หลักครับ!"
                else:
                    response_text = "ไม่สามารถ check-in ได้เนื่องจากท่านยังไม่ได้ทำการ check-out!"
            else:
                response_text = "เฉพาะพนักงานที่มีสิิทธิ์ใช้คำสั่งดังกล่าว! rank: " + rank
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response_text))
            return 0

        if 'out' in words_list or 'checkout' in words_list:
            rank = mem.member_rank(event.source.user_id)
            response_text = "รหัส(code)ไม่ถูกต้องครับ!"
            if rank in "01":
                if mem.is_working(event.source.user_id):
                    mem.checkin_out(event.source.user_id,"0")
                    response_text = "Check out สำเร็จแล้วครับ!"
                else:
                    response_text = "ไม่สามารถ check-out ได้เนื่องจาก\nท่านยังไม่ได้ทำการ check-in!"
            else:
                response_text = "เฉพาะพนักงานที่มีสิิทธิ์ใช้คำสั่งดังกล่าว! rank: " + rank
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response_text))
            return 0

        if text == '!test':
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
            return 0

        if text == '!help':
            helpt = ["[จำเป็น]\n'!help'\n'check'or'checkin'-OTP\n'out'or'checkout'\n'ขอ'&ยอดเงิน'or'balance'\n'ขอ'&'เงินเดือน'or'รายได้'-\n'ขอ'&'ฟอร์ม'or'แบบฟอร์ม'\n'ขอ'&'เมนู'or'เมนูอื่นๆ'\n'ขอสรุปค่าใช้จ่าย'",
            "[ทั่วไป]\n'Abbok'\n'member'\n'ใคร'&'ทำงานอยู่'or'อยู่ที่ทำงาน'\n'trackid'or'รหัส'-รหัสไปรษณี\n'ราคา'or'หุ้น'-QUOTE\n'คำคม'or'quote'",
            "[ทดลอง]\n'!test'\n'เพิ่มข้อมูล'or'add data'-data\n'ทดลอง'-ประโยคเพื่อคุย\n'cast'or'castto'-t\n'profile'\n'!vote'"]
            self.line_bot_api.reply_message(
                event.reply_token,[
                TextSendMessage(text=helpt[0]),
                TextSendMessage(text=helpt[1]),
                TextSendMessage(text=helpt[2])])
            return 0

        if 'ใคร' in words_list and ('ทำงานอยู่' in text or 'อยู่ที่ทำงาน' in text):
            text = mem.who_work()
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
            return 0

        if 'cast' in words_list or 'castto' in words_list:
            rank = mem.member_rank(event.source.user_id)
            if rank in "0":
                if 'cast ' in text or 'castto ' in text:
                    textn = text.replace('cast ', '').replace('castto ', '')
                    to = "C374667ff440b48857dafb57606ff4600"
                    self.line_bot_api.push_message(to, TextSendMessage(text=textn))
                else:
                    response_text = "กรุณาพิมพ์ cast หรือ castto\nตามด้วยประโยคที่ต้องการเผยแพร่!"
            else:
                response_text = "เฉพาะพนักงานที่มีสิิทธิ์ใช้คำสั่งดังกล่าว! rank: " + rank

            return 0
        if 'แบม' in words_list or 'บี้' in words_list:
            texts = ['ตูดหมึก', 'ปากห้อย', 'อ้วน', 'ขี้โม้', 'ไม่เชื่อ!', 'เด็กอ้วน', 'แก้มดุ่ย', 'บี้']
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=texts[random.randint(0,7)]))
            return 0

        if 'บุ๊ค' in words_list or 'book' in words_list or 'บุ๊ก' in words_list:
            texts = ['ตูดหมึก', 'จังกะเป', 'อ้วน', 'ขี้โม้', 'ไม่เชื่อ!', 'เด็กแว๊น', 'กิ๊บป่อง', 'ผีบ้า']
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=texts[random.randint(0,7)]))
            return 0

        ##################
        if text == 'profile':
            if isinstance(event.source, SourceUser):
                profile = self.line_bot_api.get_profile(event.source.user_id)
                self.line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='User id: ' + event.source.user_id),
                        TextSendMessage(text='Display name: ' + profile.display_name),
                        TextSendMessage(text='Status message: ' + profile.status_message)
                    ]
                )

            elif isinstance(event.source, SourceGroup):
                #member_ids_res = self.line_bot_api.get_group_member_ids(event.source.group_id)
                self.line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text="Bot is in a Group!"),
                        TextSendMessage(text='Group id: ' + event.source.group_id),
                        #TextSendMessage(text='Member ids: ' + str(member_ids_res.member_ids))
                    ]
                )

            elif isinstance(event.source, SourceRoom):
                #member_ids_res = self.line_bot_api.get_room_member_ids(event.source.room_id)
                self.line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text="Bot is in a Room!"),
                        TextSendMessage(text='Room id: ' + event.source.room_id),
                        #TextSendMessage(text='Member ids: ' + str(member_ids_res.member_ids))
                    ]
                )

            else:
                self.line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text="Bot can't use profile API without user ID")
                    ]
                )

        if text == 'member':
            if isinstance(event.source, SourceUser):
                profile = self.line_bot_api.get_profile(event.source.user_id)
                member = "You are not a member!"
                if mem.is_member(event.source.user_id) and mem.is_approve(event.source.user_id):
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
                    self.line_bot_api.reply_message(
                        event.reply_token, [
                            TextSendMessage(text='Hello! ' + profile.display_name),
                            TextSendMessage(text=member),
                            template_member
                        ]
                    )
                elif mem.is_member(event.source.user_id) and not mem.is_approve(event.source.user_id):
                    member = "your application is waiting to be approve!\nplease wait!"
                    self.line_bot_api.reply_message(
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
                    self.line_bot_api.reply_message(event.reply_token, [
                        TextSendMessage(text='Hello! ' + profile.display_name),
                        TextSendMessage(text=member),
                        template_message
                    ])
                    print(event.message.text.lower())

            elif isinstance(event.source, SourceGroup):
                #member_ids_res = self.line_bot_api.get_group_member_ids(event.source.group_id)
                self.line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text="Bot is in a Group!"),
                        TextSendMessage(text='Group id: ' + event.source.group_id),
                        #TextSendMessage(text='Member ids: ' + str(member_ids_res.member_ids))
                    ]
                )

        elif text == 'quota':
            quota = self.line_bot_api.get_message_quota()
            self.line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='type: ' + quota.type),
                    TextSendMessage(text='value: ' + str(quota.value))
                ]
            )
        elif text == 'quota_consumption':
            quota_consumption = self.line_bot_api.get_message_quota_consumption()
            self.line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='total usage: ' + str(quota_consumption.total_usage)),
                ]
            )
        elif text == 'ขอชื่อพนักงาน' or text == 'ขอชื่อสมาชิิก':
            textn = mem.get_all_member_names()
            text = ""
            for i in textn:
                text += i + "\n"
            self.line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text=text),
                ]
            )
        elif text == 'push':
            self.line_bot_api.push_message(
                event.source.user_id, [
                    TextSendMessage(text='PUSH!'),
                ]
            )
        elif text == 'multicast':
            self.line_bot_api.multicast(
                [event.source.user_id], [
                    TextSendMessage(text='THIS IS A MULTICAST MESSAGE'),
                ]
            )
        elif text == 'broadcast':
            self.line_bot_api.broadcast(
                [
                    TextSendMessage(text='THIS IS A BROADCAST MESSAGE'),
                ]
            )
        elif text.startswith('broadcast '):  # broadcast 20190505
            date = text.split(' ')[1]
            print("Getting broadcast result: " + date)
            result = self.line_bot_api.get_message_delivery_broadcast(date)
            self.line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Number of sent broadcast messages: ' + date),
                    TextSendMessage(text='status: ' + str(result.status)),
                    TextSendMessage(text='success: ' + str(result.success)),
                ]
            )
        elif text == 'bye':
            if isinstance(event.source, SourceGroup):
                self.line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Leaving group'))
                self.line_bot_api.leave_group(event.source.group_id)
            elif isinstance(event.source, SourceRoom):
                self.line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Leaving group'))
                self.line_bot_api.leave_room(event.source.room_id)
            else:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Bot can't leave from 1:1 chat"))

        elif text == 'image':
            url = request.url_root + '/static/doge.jpg'
            app.logger.info("url=" + url)
            self.line_bot_api.reply_message(
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
            self.line_bot_api.reply_message(event.reply_token, template_message)

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
            self.line_bot_api.reply_message(event.reply_token, template_message)

        elif text == '!vote':
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="ระบบโหวตเร็วๆนี้"))

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
            self.line_bot_api.reply_message(event.reply_token, template_message)

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
            self.line_bot_api.reply_message(event.reply_token, template_message)

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
            self.line_bot_api.reply_message(event.reply_token, template_message)
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
            self.line_bot_api.reply_message(event.reply_token, template_message)
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
            self.line_bot_api.reply_message(
                event.reply_token,
                message
            )
        elif text == 'quick_reply':
            self.line_bot_api.reply_message(
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
            ce = random.randint(1,10)
            if ce > 6 and ce < 9:
                text = ['ตูดหมึก', 'หอย', 'WTF!', 'ขี้โม้', 'ไม่เชื่อ!', 'แม่ย้อย', 'พ่อง', 'โฮ่งง', 'สลัดผัก']
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text[random.randint(0,8)]))
