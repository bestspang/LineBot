from oauth2client.service_account import ServiceAccountCredentials
import json, requests, random, os, errno, sys, tempfile, configparser
import dialogflow, gspread, pprint

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('BPLINEBOT-57c70064e9b9.json', scope)
client = gspread.authorize(creds)

sheet = client.open('lineUser').worksheet('user')
pp = pprint.PrettyPrinter()
user_id = sheet.col_values(3)[1:]
isApprove = sheet.col_values(4)[1:][0] == "APPROVE"
a= [1,2]
print(len(a))
print(sheet.col_values(4)[1:][0])
print(user_id)
print(isApprove)

#sheet.update_cell(1, 1, newdata)
#pp.pprint(balance)
#price = "เงินเดือนของ {} จะได้รับในเดือนนี้ {} บาทครับผม!".format(usern, balance)
