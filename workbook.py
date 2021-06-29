from datetime import datetime
from pytz import timezone


class Workbook:
    tz = timezone('Europe/Minsk')

    def __init__(self, user_id, subject_id, link):
        self.user_id = user_id
        self.subject_id = subject_id
        self.link = link
        self.last_modified = datetime.now(Workbook.tz)

    def serialize(self):
        return [None, self.subject_id, self.user_id, self.link, self.last_modified]

    def __str__(self):
        return "{} {}".format(self.user_id, self.last_modified)
