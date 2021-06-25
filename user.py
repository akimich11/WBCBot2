from datetime import datetime
from enum import Enum
from pytz import timezone


class Button(Enum):
    SEND = 1
    FIND = 2
    NONE = 3


class User:
    tz = timezone('Europe/Minsk')

    def __init__(self, message):
        self.user_id = message.from_user.id
        self.first_name = message.from_user.first_name
        self.last_name = message.from_user.last_name
        self.username = message.from_user.username
        self.last_seen = datetime.now(self.tz)
        self.button_state = Button.NONE
        self.subject_id = -1
        self.photos = []
        self.files = []

    def get_access_time(self):
        return "{} - {} {} ({})".format(self.last_seen.strftime("%d.%m.%Y в %H:%M"),
                                        self.first_name, self.last_name, self.user_id)

    def __str__(self):
        if self.username is not None:
            return "{} {} {} @{}".format(self.user_id, self.first_name, self.last_name, self.username)
        return "{} {} {}".format(self.user_id, self.first_name, self.last_name)
