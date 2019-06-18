import gspread
import pandas as pd
#from flask_restful import Resource, reqparse
from oauth2client.service_account import ServiceAccountCredentials

class User:
    def __init__(self, _id, line_id, name, is_in, time):
        self.id = _id
        self.name = name
        self.line_id = line_id
        self.is_in = is_in
        self.time = time
        # scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        # creds = ServiceAccountCredentials.from_json_keyfile_name('bplinebot-3ccea59ad6d6.json', scope)
        # client = gspread.authorize(creds)

    def get_sheet(self, spread, sheet):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('bplinebot-3ccea59ad6d6.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(spread).worksheet(sheet)
        return sheet

    @classmethod
    def find_by_name(cls, name):
        data = ('userCheckin', 'userStatus').get_all_values()
        df = pd.DataFrame(data[1:], columns = data[0])
        try:
            #df[df['USER_KEY']==name]['USER_KEY'].iloc[0]
            row = df[df['NAME']==name].values.tolist()[0]
        except:
            row = None
        print(row)
        if row:
            user = cls(*row)#row[0], row[1], row[2]
        else:
            user = None
        return user

    @classmethod
    def find_by_id(cls, line_id):
        data = ('userCheckin', 'userStatus').get_all_values()
        df = pd.DataFrame(data[1:], columns = data[0])
        try:
            #df[df['USER_KEY']==username]['USER_KEY'].iloc[0]
            row = df[df['USER_KEY']==line_id].values.tolist()[0]
        except:
            row = None

        if row:
            user = cls(*row)#row[0], row[1], row[2]
        else:
            user = None
        return user

# class UserRegister(Resource):
#
#     parser = reqparse.RequestParser()
#     parser.add_argument('username',
#         type=str,
#         required=True,
#         help="This field cannot be left blank!"
#     )
#     parser.add_argument('password',
#         type=str,
#         required=True,
#         help="This field cannot be left blank!"
#     )
#
#     def post(self):
#         data = UserRegister.parser.parse_args()
#
#         connection = sqlite3.connect('data.db')
#         cursor = connection.cursor()
#
#         query = "INSERT INTO users VALUES (NULL, ?, ?)"
#         cursor.execute(query, (data['username'], data['password']))
#
#         connection.commit()
#         connection.close()
#
#         return {"message": "User created successfully."}, 201
