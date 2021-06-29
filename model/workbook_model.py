import img2pdf
import os
import shutil
from workbook import Workbook
from PyPDF2 import PdfFileMerger


def save_file(bot, file_id, full_name):
    file_to_save = bot.get_file(file_id)
    file_extension = os.path.splitext(file_to_save.file_path)[1]
    filename = full_name + file_extension.lower()
    with open(filename, "wb") as new_file:
        new_file.write(bot.download_file(file_to_save.file_path))
    return filename


def save_files(bot, file_ids, path, idx):
    for f_id in file_ids:
        idx += 1
        save_file(bot, f_id, path + "\\" + str(idx))
    file_ids.clear()
    return idx


def convert(image_list, filename):
    with open(filename, "wb") as f:
        f.write(img2pdf.convert(*image_list))


def sort_by_number(filename):
    return int(filename.split("\\")[-1].split(".")[0])


def merge(old_workbook, new_photos, filename):
    if old_workbook is not None:
        with open(old_workbook, 'rb') as orig, open(new_photos, 'rb') as new:
            pdf = PdfFileMerger()
            pdf.append(orig)
            pdf.append(new)
            pdf.write(filename)


class WorkbookModel:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.conn = connection
        workbooks_create_query = """CREATE TABLE IF NOT EXISTS workbooks (
                                    id integer primary key, subject_id integer, user_id integer, 
                                    link text, last_modified text,
                                    foreign key (subject_id) references subjects(id),
                                    foreign key (user_id) references users(id))"""
        self.cursor.execute(workbooks_create_query)
        self.conn.commit()

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

    def add_workbook(self, user, subject, wb_link):
        workbook = Workbook(user.id, subject.id, wb_link)
        self.cursor.execute("""DELETE FROM workbooks WHERE subject_id=? AND user_id=?""", [subject.id, user.id])
        self.conn.commit()
        self.cursor.execute("""INSERT INTO workbooks VALUES (?,?,?,?,?)""", workbook.serialize())
        self.conn.commit()
        shutil.rmtree('..\\tmp\\' + str(user.id) + '\\')
