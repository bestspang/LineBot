from oauth2client.service_account import ServiceAccountCredentials
import gspread, pprint


class Member:
    def __init__(self):
        #self.name = name
        #self.id = id
        #self.line_id = line_id
        #self.marks = []
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('BPLINEBOT-57c70064e9b9.json', scope)
        client = gspread.authorize(creds)

    def member_rank(input):
        if is_member(input) and is_approve(input):
            sheet = client.open('lineUser').worksheet('user')
            user_id = sheet.col_values(3)[1:]
            return sheet.col_values(6)[1:][user_id.index(input)]
        else:
            return False

    def get_all_member_ids():
            sheet = client.open('lineUser').worksheet('user')
            user_id = sheet.col_values(3)[1:]
            return user_id

    def is_member(input):
            sheet = client.open('lineUser').worksheet('user')
            user_id = sheet.col_values(3)[1:]
            if input in user_id:
                return True
            else:
                return False

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
            line_bot_api.push_message(to, TextSendMessage(text=profile.display_name + 'ได้สมัครสมาชิก!'))

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

    @classmethod
    def friend(cls, origin, friend_name, *args, **kwargs):
        return cls(friend_name, origin.salary, *args, **kwargs)

####

class AddMember(Member):
    def __init__(self, name, id, line_id, salary, job_title):
        super().__init__(name, id, line_id)
        self.salary = salary
        self.job_title = job_title

#best = AddMember("Best", 1, "a", 15000, "R&D Director")
#taan = AddEmployee.friend(best, "Taan", 2, "b", job_title="CTO")
