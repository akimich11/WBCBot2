from enum import Enum


class Button(Enum):
    SEND = 1
    FIND = 2
    NONE = 3


class User:
    def __init__(self, user_id, first_name, last_name, username, is_admin, is_banned):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.is_admin = is_admin
        self.is_banned = is_banned
        self.button_state = Button.NONE
        self.subject_id = -1

    def __str__(self):
        if self.username is not None:
            return "{} {} {} @{}\n".format(self.user_id, self.first_name, self.last_name, self.username)
        return "{} {} {}\n".format(self.user_id, self.first_name, self.last_name)
