from user import User
from subject import Subject
import sqlite3
from model.user_model import UserModel
from model.subject_model import SubjectModel
from model.workbook_model import WorkbookModel


class Model:
    def __init__(self):
        self.conn = sqlite3.connect("../assets/identifier.sqlite")
        self.cursor = self.conn.cursor()

        self.user_model = UserModel(self.cursor, self.conn)
        self.subject_model = SubjectModel(self.cursor, self.conn)
        self.workbook_model = WorkbookModel(self.cursor, self.conn)
