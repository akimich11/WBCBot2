from subject import Subject


class SubjectModel:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.conn = connection
        subjects_create_query = """CREATE TABLE IF NOT EXISTS subjects (
                                   name text, id integer primary key);"""
        self.cursor.execute(subjects_create_query)
        self.conn.commit()
        self.subjects = dict()
        for row in self.cursor.execute("""SELECT * FROM subjects""").fetchall():
            self.subjects[row[1]] = Subject(*row)

    def create_subject(self, subject_name):
        insert_subject = (subject_name, None)
        self.cursor.execute("""INSERT INTO subjects VALUES (?,?)""", insert_subject)
        self.conn.commit()
        index = self.cursor.execute("""SELECT id FROM subjects WHERE name=?""", (subject_name,)).fetchone()[0]
        self.subjects[index] = Subject(subject_name, index)
        return True

    def remove_subject(self, subject_name):
        index = self.cursor.execute("""SELECT id FROM subjects WHERE name=?""", (subject_name,)).fetchone()
        if index is not None:
            self.cursor.execute("""DELETE FROM subjects WHERE id=?""", [index[0]])
            self.conn.commit()
            self.subjects.pop(index[0])
            return True
        return False

    def get_subject(self, subject_id):
        return self.subjects[subject_id]
