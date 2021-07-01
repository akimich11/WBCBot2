import os
import shutil
from workbook import Workbook
from subject import Subject
from decorators import db_connector
from model.pdf import convert, merge, save_file, save_files

import sqlite3


def sort_by_number(filename):
    return int(filename.split("\\")[-1].split(".")[0])


class WorkbookModel:
    def __init__(self):
        self.conn = sqlite3.connect("../assets/identifier.sqlite", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_database()

    @db_connector
    def create_database(self):
        workbooks_create_query = """CREATE TABLE IF NOT EXISTS workbooks (
                                    id integer primary key, subject_id integer, user_id integer, 
                                    link text, last_modified text,
                                    foreign key (subject_id) references subjects(id) ON DELETE CASCADE,
                                    foreign key (user_id) references users(id) ON DELETE CASCADE)"""
        self.cursor.execute(workbooks_create_query)

    @db_connector
    def update_photos(self, bot, user, subject_id):
        query_result = self.cursor.execute("""SELECT link FROM workbooks WHERE user_id=? AND subject_id=?""",
                                           [user.id, subject_id]).fetchone()
        if query_result is None:
            wb_link = None
        else:
            wb_link = query_result[0]
        path = '..\\tmp\\' + str(user.id)
        os.mkdir(path)
        if wb_link is not None:
            save_file(bot, wb_link, path + "\\" + str(user.id))
        idx = 0
        idx = save_files(bot, user.photos, path, idx)
        save_files(bot, user.files, path, idx)

    @staticmethod
    def create_workbook(user, subject):
        path = '..\\tmp\\' + str(user.id)
        image_list = []
        old_workbook = None
        for filename in sorted(os.listdir(path), key=sort_by_number):
            if filename.split(".")[1] != 'pdf':
                image_list.append(path + '\\' + filename)
            else:
                old_workbook = path + '\\' + filename
        new_photos = path + '\\new_photos.pdf'
        convert(image_list, new_photos)
        filename = path + '\\' + subject.name + "_" + user.first_name + '.pdf'
        merge(old_workbook, new_photos, filename)
        return filename

    @db_connector
    def add_workbook(self, user, subject, wb_link):
        workbook = Workbook(user.id, user.first_name, subject, wb_link)
        self.cursor.execute("""DELETE FROM workbooks WHERE subject_id=? AND user_id=?""", [subject.id, user.id])
        self.cursor.execute("""INSERT INTO workbooks VALUES (?,?,?,?,?)""", workbook.serialize())
        shutil.rmtree('..\\tmp\\' + str(user.id) + '\\')

    @db_connector
    def get_workbooks_list(self, bot, user, subject_id):
        data = self.cursor.execute("""SELECT user_id, first_name, subject_id, name, link, last_modified 
                                                      FROM workbooks 
                                                      JOIN subjects s ON s.id = workbooks.subject_id 
                                                      JOIN users u ON u.id = workbooks.user_id
                                                      WHERE subject_id=?""", [subject_id]).fetchall()
        workbooks = []
        if data is not None:
            for row in data:
                workbooks.append(Workbook(row[0], row[1], Subject(row[3], row[2]), row[4], row[5]))
        bot.send_workbooks_list(user, workbooks)
        return workbooks


workbook_model = WorkbookModel()
