from datetime import datetime
from pytz import timezone


class Workbook:
    tz = timezone('Europe/Minsk')

    def __init__(self, user_id, subject_id):
        self.user_id = user_id
        self.subject_id = subject_id
        self.last_modified = datetime.now(Workbook.tz)

    def __str__(self):
        return "{} {}".format(self.user_id, self.last_modified)
