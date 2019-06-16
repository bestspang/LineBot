class User:
    def __init__(self, _id, line_name, line_id, approve, user_type):
        self.id = _id
        self.line_name = line_name
        self.line_id = line_id
        self.approve = approve
        self.user_type = user_type
        is_in = None
        NAME = None
        approve_date = None
        pic_url = None
