from base.subject import Subject
from decorators import database


class SubjectModel:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.subjects = dict()
        self.create_database()
        self.create_subject("Другое")

    @database.connector
    def create_database(self):
        subjects_create_query = """CREATE TABLE IF NOT EXISTS subjects (
                                   name VARCHAR(255) UNIQUE, id INT PRIMARY KEY AUTO_INCREMENT);"""
        self.cursor.execute(subjects_create_query)
        self.cursor.execute("""SELECT * FROM subjects""")
        result = self.cursor.fetchall()
        if result is not None:
            for row in result:
                self.subjects[row[1]] = Subject(*row)

    @database.connector
    def create_subject(self, subject_name):
        insert_subject = (subject_name, None)
        self.cursor.execute("""INSERT IGNORE INTO subjects VALUES (%s,%s)""", insert_subject)
        self.cursor.execute("""SELECT id FROM subjects WHERE name=%s""", (subject_name,))
        index = self.cursor.fetchone()[0]
        self.subjects[index] = Subject(subject_name, index)
        return True

    @database.connector
    def remove_subject(self, subject_name):
        self.cursor.execute("""SELECT id FROM subjects WHERE name=%s""", (subject_name,))
        index = self.cursor.fetchone()
        if index is not None:
            index = index[0]
            self.cursor.execute("""DELETE FROM subjects WHERE id=%s""", [index])
            self.subjects.pop(index)
            return True
        return False

    def get_subject(self, subject_id):
        return self.subjects[subject_id]


subject_model = SubjectModel()
