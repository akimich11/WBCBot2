from datetime import datetime
from pytz import timezone


class Workbook:
    tz = timezone('Europe/Minsk')

    def __init__(self, user_id, user_first_name, subject, link, last_modified=None):
        self.user_id = user_id
        self.user_first_name = user_first_name
        self.subject = subject
        self.link = link
        self.last_modified = last_modified or datetime.now(Workbook.tz)

    def serialize(self):
        return [None, self.subject.id, self.user_id, self.link, self.last_modified.strftime("%d.%m.%Y в %H:%M")]

    def __str__(self):
        return "{}, изменено {}".format(self.user_first_name, self.last_modified)
