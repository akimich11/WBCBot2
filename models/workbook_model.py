import os
import shutil
from base.workbook import Workbook
from base.subject import Subject
from decorators import database
from models.pdf import convert, merge, save_file, save_files


def sort_by_number(filename):
    return int(filename.split("/")[-1].split(".")[0])


class WorkbookModel:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.create_database()

    @database.connector
    def create_database(self):
        workbooks_create_query = """CREATE TABLE IF NOT EXISTS workbooks (
                                    id INT PRIMARY KEY AUTO_INCREMENT, subject_id INT, user_id INT, 
                                    link TEXT, last_modified TEXT,
                                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)"""
        self.cursor.execute(workbooks_create_query)

    @database.connector
    def update_photos(self, bot, user, subject_id):
        self.cursor.execute("""SELECT link FROM workbooks WHERE user_id=%s AND subject_id=%s""",
                               [user.id, subject_id])
        query_result = self.cursor.fetchone()
        if query_result is None:
            wb_link = None
        else:
            wb_link = query_result
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        path = 'tmp/' + str(user.id)
        os.mkdir(path)
        if wb_link is not None:
            save_file(bot, wb_link, path + "/" + str(user.id))
        idx = 0
        idx = save_files(bot, user.photos, path, idx)
        save_files(bot, user.files, path, idx)

    @staticmethod
    def create_workbook(user, subject):
        path = 'tmp/' + str(user.id)
        image_list = []
        old_workbook = None
        for filename in sorted(os.listdir(path), key=sort_by_number):
            if filename.split(".")[1] != 'pdf':
                image_list.append(path + '/' + filename)
            else:
                old_workbook = path + '/' + filename
        new_photos = path + '/new_photos.pdf'
        convert(image_list, new_photos)
        filename = path + '/' + subject.name + "_" + user.first_name + '.pdf'
        merge(old_workbook, new_photos, filename)
        return filename

    @database.connector
    def add_workbook(self, user, subject, wb_link):
        workbook = Workbook(user.id, user.first_name, subject, wb_link)
        self.cursor.execute("""DELETE FROM workbooks WHERE subject_id=%s AND user_id=%s""", [subject.id, user.id])
        self.cursor.execute("""INSERT INTO workbooks VALUES (%s,%s,%s,%s,%s)""", workbook.serialize())
        shutil.rmtree('tmp/' + str(user.id) + '/')

    @database.connector
    def get_workbooks_list(self, bot, user, subject_id):
        self.cursor.execute("""SELECT user_id, first_name, subject_id, name, link, last_modified 
                               FROM workbooks 
                               JOIN subjects s ON s.id = workbooks.subject_id 
                               JOIN users u ON u.id = workbooks.user_id
                               WHERE subject_id=%s""", [subject_id])
        data = self.cursor.fetchall()
        workbooks = []
        if data is not None:
            for row in data:
                workbooks.append(Workbook(row[0], row[1], Subject(row[3], row[2]), row[4], row[5]))
        bot.send_workbooks_list(user, workbooks)
        return workbooks

    @database.connector
    def delete_workbook(self, user_id, subject_name):
        self.cursor.execute("""DELETE workbooks FROM workbooks 
                               INNER JOIN subjects ON subjects.id = workbooks.subject_id
                               WHERE name=%s AND user_id=%s""", [subject_name, user_id])


workbook_model = WorkbookModel()
