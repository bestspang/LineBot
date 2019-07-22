from oauth2client.service_account import ServiceAccountCredentials
import gspread, pprint, functools, csv, datetime
from user import User

class Member:
    def __init__(self, line_bot_api):
        #self.name = name
        #self.id = id
        #self.line_id = line_id
        #self.marks = []
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('static/key/BPLINEBOT-57c70064e9b9.json', scope)
        self.line_bot_api = line_bot_api
        self.client = gspread.authorize(creds)

    def check_permission(number):
        def my_decorator(func):
            @functools.wraps(func)
            def is_user_allow(*args, **kwargs):
                if number in [0,4]:
                    func(*args, **kwargs)
                else:
                    print("You have no permission!")
            return is_user_allow
        return my_decorator

    def get_all_member_ids(self):
        sheet = self.client.open('userCheckin').worksheet('userStatus')
        user_id = sheet.col_values(2)[1:]
        return user_id

    def get_all_member_names(self):
        sheet = self.client.open('userCheckin').worksheet('userStatus')
        user_id = sheet.col_values(3)[1:]
        return user_id

    def get_key_by_name(self, input):
        key = self.get_all_member_ids()
        name = self.get_all_member_names()
        try:
            line_key = key[name.index(input)]
        except:
            return False
        return line_key

    def is_member(self, input):
        sheet = self.client.open('lineUser').worksheet('user')
        user_id = sheet.col_values(3)[1:]
        if input in user_id:
            # sheet.col_values(4)[1:][user_id.index(input)]
            return True
        else:
            return False
        # pp.pprint(balance)
        # sheet = client.open('testSpreadsheet').sheet1
        # pp = pprint.PrettyPrinter()
        # sheet.update_cell(1, 1, newdata)

    @classmethod
    def friend(cls, origin, friend_name, *args, **kwargs):
        return cls(friend_name, origin.salary, *args, **kwargs)

    def check_opt(input, opt):
        if input == opt:
            return True
        else:
            return False

    # @staticmethod
    # def gsheet_to_csv(self, input, opt):
    #     sheet = self.client.open('userCheckin').worksheet('userStatus')
    #     for i, worksheet in enumerate(sheet.worksheets()):
    #         filename = docid + '-worksheet' + str(i) + '.csv'
    #         with open(filename, 'w', newline='') as f:
    #             writer = csv.writer(f)
    #             writer.writerows(worksheet.get_all_values())

    @staticmethod
    def is_working(self, input_id):
        sheet = self.client.open('userCheckin').worksheet('userStatus')
        user_id = sheet.col_values(2)[1:]
        return int(sheet.col_values(4)[1:][user_id.index(input_id)])

    @staticmethod
    def who_work(self):
        sheet = self.client.open('userCheckin').worksheet('userStatus')
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

    @staticmethod
    def member_rank(self, input):
        if self.is_member(input) and self.is_approve(input):
            sheet = self.client.open('lineUser').worksheet('user')
            user_id = sheet.col_values(3)[1:]
            return sheet.col_values(6)[1:][user_id.index(input)]
        else:
            return False

    @staticmethod
    def is_approve(self, input):
        sheet = self.client.open('lineUser').worksheet('user')
        user_id = sheet.col_values(3)[1:]
        if input in user_id and sheet.col_values(4)[1:][user_id.index(input)] == "APPROVE":
            return True
        else:
            return False

    @staticmethod
    def add_member(self, input):
        sheet = self.client.open('lineUser').worksheet('user')
        profile = self.line_bot_api.get_profile(input)
        now = datetime.datetime.now()
        row_num = len(sheet.col_values(3)[1:])
        row = [row_num + 1, profile.display_name, input, "WAITING", now.strftime('%Y/%m/%d'),"4",profile.picture_url]
        index = row_num + 2
        sheet.insert_row(row, index)
        to = "C374667ff440b48857dafb57606ff4600"
        self.line_bot_api.push_message(to, TextSendMessage(text=profile.display_name + 'ได้สมัครสมาชิก!'))

    @staticmethod
    def is_approve_new_member(self):
        sheet = self.client.open('lineUser').worksheet('user')
        name = sheet.col_values(2)[-1]
        confirm_template = ConfirmTemplate(text='Approve หรือ ไม่?', actions=[
            PostbackAction(label='Yes',text='Yes!',data='member_yes'),
            PostbackAction(label='No',text='No!',data='member_no'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        to = "U7612d77bbca83f04d6acf5e27333edeb"
        self.line_bot_api.push_message(to, [TextSendMessage(text="คุณ "+name),
        TextSendMessage(text="สมาชิกใหม่ได้ทำการกรอกเอกสาร!\nจะ APPROVE หรือไม่?"),
        template_message])

    def approve_member(self, boo):
        if boo == 1:
            sheet = self.client.open('lineUser').worksheet('user')
            row_num = len(sheet.col_values(3)[1:])
            sheet.update_cell(row_num+1, 4, "APPROVE")
            sheet.update_cell(row_num+1, 6, "1")
        else:
            pass

    @staticmethod
    def checkin_out(self, input_id, type):
        profile = self.line_bot_api.get_profile(input_id)
        now = datetime.datetime.now() + datetime.timedelta(seconds = 25200)
        sheet = self.client.open('userCheckin').worksheet('userStatus')
        user_id = sheet.col_values(2)[1:]
        user_name = sheet.col_values(3)[1:]
        sheet2 = self.client.open('userCheckin').worksheet('log')
        row_num = len(sheet2.col_values(1)[1:])
        #int(sheet.col_values(4)[1:][user_id.index(input_id)])
        # check is_in
        sheet.update_cell(user_id.index(input_id) + 2, 4, type)
        # update log
        row = [row_num + 1,now.strftime('%Y/%m/%d'),now.strftime("%I:%M %p"), user_id.index(input_id) + 1,type]
        index = row_num + 2
        sheet2.insert_row(row, index)
        to = "C374667ff440b48857dafb57606ff4600"
        to_user = input_id
        if type == "1":
            text = "Check-In!"
            sheet.update_cell(user_id.index(input_id) + 2, 5, now.strftime("%I:%M %p"))
        elif type == "0":
            text = "Check-out!"
            total_work =  (datetime.datetime.now() + datetime.timedelta(seconds = 25200)) - datetime.datetime.strptime(sheet.cell(user_id.index(input_id) + 2, 5).value, '%I:%M %p')
            total_work = "คุณทำงานทั้งหมดเป็นเวลา {} ช.ม. {} นาที {} วินาที".format(total_work.seconds//3600,(total_work.seconds//60)%60,total_work.seconds%60)
            sheet.update_cell(user_id.index(input_id) + 2, 5, '')
            self.line_bot_api.push_message(to_user, TextSendMessage(text=total_work))

        self.line_bot_api.push_message(to, TextSendMessage(text=profile.display_name + 'ได้ทำการ ' + text))

####

class AddMember(Member):
    def __init__(self, name, id, line_id, salary, job_title):
        super().__init__(name, id, line_id)
        self.salary = salary
        self.job_title = job_title

#best = AddMember("Best", 1, "a", 15000, "R&D Director")
#taan = AddEmployee.friend(best, "Taan", 2, "b", job_title="CTO")
