class User:
    def __init__(self, _id, name, line_id):
        self.id = _id
        self.name = name
        self.line_id = line_id
        self.line_name = None
        self.is_in = None
        self.approve_date = None
        self.pic_url = None
