import gspread
import pprint
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('BPLINEBOT-57c70064e9b9.json', scope)
client = gspread.authorize(creds)
sheet = client.open('AbbokIncomeAssesmentV02').get_worksheet(2)
pp = pprint.PrettyPrinter()
#data = sheet.get_all_records()
name = ["BEST", "TAAN", "TEAM", "SNOOK"]
num = name.index('TAAN')
balance = sheet.cell(num+2, 9).value
#pp.pprint(balance)
pp.pprint(balance)
print("เงินเดือน : " + balance)
