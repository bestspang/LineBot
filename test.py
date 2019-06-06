from oauth2client.service_account import ServiceAccountCredentials
import json, requests, random, os, errno, sys, tempfile, configparser
import dialogflow, gspread, pprint

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('BPLINEBOT-57c70064e9b9.json', scope)
client = gspread.authorize(creds)

# sheet = client.open('lineUser').worksheet('user')
# key= "U7612d77bbca83f04d6acf5e27333edeb"
# pp = pprint.PrettyPrinter()
# user_id = sheet.col_values(3)[1:]
# print(user_id.index(key))
# isApprove = sheet.col_values(4)[1:][user_id.index(key)] == "APPROVE"
# print(sheet.col_values(4)[1:][0])
# print(user_id)
# print(isApprove)

words_list = ['ใคร','ทำงานอยู่']

if 'ใคร' in words_list and ('ทำงานอยู่' in words_list or 'อยู่ที่ทำงาน' in words_list):
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

print(text)
#sheet.update_cell(1, 1, newdata)
#pp.pprint(balance)
#price = "เงินเดือนของ {} จะได้รับในเดือนนี้ {} บาทครับผม!".format(usern, balance)
