import csv
from Member import Member

class Tools:
    def __init__(self, name, id, line_id):
        self.name = name
        self.id = id
        self.line_id = line_id
        self.marks = []

    def average(self):
        return sum(self.marks) / len(self.marks)

    @classmethod
    def friend(cls, origin, friend_name, *args, **kwargs):
        return cls(friend_name, origin.salary, *args, **kwargs)

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
