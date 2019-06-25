from Member import Member
from threading import Thread
import csv, json, requests, math, os, time, random
from pythainlp.tokenize import word_tokenize
from pythainlp.util import isthai
from bs4 import BeautifulSoup as soup
import numpy as np
#from html.parser import HTMLParser
from urllib.request import urlopen as uReq
from urllib.request import urlretrieve as uRet

class Tools:
    def __init__(self):
        self.result = None

    def get_sheet(spread, sheet):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('bplinebot-3ccea59ad6d6.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(spread).worksheet(sheet)
        return sheet

    def extractWord(self, text):
        a = word_tokenize(text, engine='newmm')
        b = []
        for h in a:
            if h != ' ':
                b.append(h.lower())
        return b

    def getQuote(self):
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


class Hoon:
    def __init__(self):
        pass

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def getSymbol(lists):
        for i in range(len(lists)):
            if isthai(lists[i]) == 0:
                return lists[i].upper()
        return 0

    @staticmethod
    def getTable(stock_quote):
        if stock_quote == 0:
            return 0
        url = 'https://www.settrade.com/C04_01_stock_quote_p1.jsp?txtSymbol='+ stock_quote +'&ssoPageId=9&selectPage=1'
        uClient = uReq(url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        return page_soup.findAll("div", {"class":"col-xs-6"})#("table", {"class":"table table-info"})

    @staticmethod
    def stockPrice(stock_quote):
        if stock_quote == 0 or stock_quote == None:
            return 0
        price = Hoon.getTable(stock_quote)
        try:
            price = price[2].text.strip()
            text = ('หุ้น {} ราคาปัจจุบันอยู่ที่ {} บาท'.format(stock_quote, price))
            return (text, price)
        except:
            return ('ไม่มีข้อมูลหุ้นตัวนี้', None)

    @staticmethod
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

    @staticmethod
    def get_hoon(words_list):
        symbol = Hoon.getSymbol(words_list)
        price, money = Hoon.stockPrice(symbol)
        if symbol == 'SET' or symbol == 'SET50':
            price = 'กำลังอัพเดทระบบ SET ค่ะหนูน้อย ใจเย็นๆ'
        elif price == 0:
            return 0
        else:
            if not Hoon.is_number(money):
                price = 'ราคายังไม่มีการอัพเดทครัช'
        return price

    def getData(self, track_id):
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

    def cleanData(self, site_data, ind=0):
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

    def list_flatten(self, l, a=None):
        if a is None:
            a = []
        for i in l:
            if isinstance(i, list):
                list_flatten(i, a)
            else:
                a.append(i)
        return a

    def makeNP(self, outlist):
        head_list = ['date', 'time', 'status', 'receiver', 'name', 'city']
        num = int(len(outlist) / 6)
        a = np.array(outlist)
        a = a.reshape((num, 6))
        return a

    def get_shipping_stat(self, text):
        try:
            price = 0
            if len(text.split(' ')) > 2:
                price = "โปรดพิม'รหัส'เว้นวรรคและตามด้วย'Track ID'"
            elif len(text.split(' ')) == 1:
                price = "รหัสอะไรฟะ บอกกูด้วย"
            else:
                track_id = text.split(' ')[1].upper()
                data = self.getData(track_id)
                clean_data = self.cleanData(data)
                flat_data = self.list_flatten(clean_data)
                np = self.makeNP(flat_data)
                if str(np[0][3]) == 'None':
                    price = ('ขณะนี้{} เมื่อวันที่ {} เวลา {} ที่จังหวัด{}'.format(np[0][2], np[0][0], np[0][1], np[0][5]))
                else:
                    price = ('ขณะนี้{} เมื่อวันที่ {} เวลา {} โดยคุณ{} ที่จังหวัด{}'.format(np[0][2], np[0][0], np[0][1], np[0][3], np[0][5]))

        except:
            price = "ระบบขัดข้องกรุณาลองใหม่ภายหลัง"
        return price


print(Hoon.get_hoon(['ราคา', 'global']))
# print(hoon.get_shipping_stat("trackid ED900406685TH"))



class Vote:
    def __init__(self):
        self.result = None
        self.topic = None
        self.total_vote = 0

    def vote_topic(self, topic):
        self.total_vote = 0
        self.topic = topic
        mem = Member()
        with open('vote.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            #writer.writerow(['NAME', 'VOTE'])
            for i in mem.get_all_member_names():
                writer.writerow([i, None])
            writer.close()
        return self.topic

    def send_vote(self):
        #self.topic
        pass

    def check_if_done(self):
        pass

    def check_vote(self):
        with open('vote.csv', 'rb') as f:
                reader = csv.reader(f)
                # read file row by row
                for row in reader:
                    if row[1] == 1:
                        self.total_vote += 1
                    elif row[1] == 0:
                        self.total_vote -= 1
        reader.close()
        return self.total_vote

class RandomThread(Thread):
    def __init__(self, socketio, thread_stop_event):
        self.delay = 31
        self.otp = ""
        self.socketio = socketio
        self.thread_stop_event = thread_stop_event
        #self.Thread = Thread
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
        t = 0
        while not self.thread_stop_event.isSet():
            if t <= 0:
                t = self.delay
                number = self.randomNumberGenerator()
            t -= 1
            #print(time)
            self.socketio.emit('newnumber', {'number': number}, namespace='/test')
            self.socketio.emit('newtime', {'time': t}, namespace='/test')
            time.sleep(1)

    def run(self):
        #self.randomNumberGenerator()
        self.timeCountdown()
