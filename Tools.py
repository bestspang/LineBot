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
    def __init__(self, name, id, line_id):
        self.name = name
        self.id = id
        self.line_id = line_id
        self.marks = []

    def average(self):
        return sum(self.marks) / len(self.marks)
