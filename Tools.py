from Member import Member
from threading import Thread
import csv, json, requests, math, os, time, random

class Tools:
    def __init__(self):
        self.result = None

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

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False


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
