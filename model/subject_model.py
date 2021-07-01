import sqlite3
from subject import Subject
from decorators import db_connector


class SubjectModel:
    def __init__(self):
        self.conn = sqlite3.connect("../assets/identifier.sqlite", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.subjects = dict()
        self.create_database()
        self.create_subject("Другое")

    @db_connector
    def create_database(self):
        subjects_create_query = """CREATE TABLE IF NOT EXISTS subjects (
                                   name text UNIQUE, id integer primary key);"""
        self.cursor.execute(subjects_create_query)
        for row in self.cursor.execute("""SELECT * FROM subjects""").fetchall():
            self.subjects[row[1]] = Subject(*row)

    @db_connector
    def create_subject(self, subject_name):
        insert_subject = (subject_name, None)
        self.cursor.execute("""INSERT OR IGNORE INTO subjects VALUES (?,?)""", insert_subject)
        index = self.cursor.execute("""SELECT id FROM subjects WHERE name=?""", (subject_name,)).fetchone()[0]
        self.subjects[index] = Subject(subject_name, index)
        return True

    @db_connector
    def remove_subject(self, subject_name):
        index = self.cursor.execute("""SELECT id FROM subjects WHERE name=?""", (subject_name,)).fetchone()
        if index is not None:
            self.cursor.execute("""DELETE FROM subjects WHERE id=?""", [index[0]])
            self.subjects.pop(index[0])
            return True
        return False

    def get_subject(self, subject_id):
        return self.subjects[subject_id]


subject_model = SubjectModel()
