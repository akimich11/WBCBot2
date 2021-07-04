from enum import Enum


class Button(Enum):
    SEND = 1
    FIND = 2
    DELETE = 3
    NONE = 4


class User:
    def __init__(self, user_id, first_name, last_name, username, is_admin, is_banned):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.is_admin = is_admin
        self.is_banned = is_banned
        self.button_state = Button.NONE
        self.subject_id = -1
        self.photos = []
        self.files = []
        self.workbooks_list = []

    def __str__(self):
        if self.username is not None:
            return "{} {} {} @{}\n".format(self.id, self.first_name, self.last_name, self.username)
        return "{} {} {}\n".format(self.id, self.first_name, self.last_name)
