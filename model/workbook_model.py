import img2pdf
import os
from PyPDF2 import PdfFileMerger


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

    @staticmethod
    def save_file(bot, file_id, full_name):
        file_to_save = bot.get_file(file_id)
        file_extension = os.path.splitext(file_to_save.file_path)[1]
        filename = full_name + file_extension.lower()
        with open(filename, "wb") as new_file:
            new_file.write(bot.download_file(file_to_save.file_path))
        return filename

    def save_files(self, bot, file_ids, directory, idx):
        for f_id in file_ids:
            idx += 1
            self.save_file(bot, f_id, directory + "\\" + str(idx))
        file_ids.clear()
        return idx

    def update_photos(self, bot, user, subject_id):
        query_result = self.cursor.execute("""SELECT link FROM workbooks WHERE user_id=? AND subject_id=?""",
                                           [user.user_id, subject_id]).fetchone()
        if query_result is None:
            wb_link = None
        else:
            wb_link = query_result[0]

        parent_dir = '..\\tmp'
        directory = str(user.user_id)
        path = os.path.join(parent_dir, directory)
        if not os.path.isdir(path):
            os.mkdir(path)
        if wb_link is not None:
            self.save_file(bot, wb_link, path + "\\" + user.user_id)
        photos_num = len(user.photos) + len(user.files)
        idx = 0
        idx = self.save_files(bot, user.photos, path, idx)
        self.save_files(bot, user.files, path, idx)
        return photos_num

    @staticmethod
    def convert(image_list, filename):
        with open(filename, "wb") as f:
            f.write(img2pdf.convert(*image_list))

    @staticmethod
    def sort_by_number(filename):
        return int(filename.split("\\")[-1].split(".")[0])

    @staticmethod
    def merge(old_workbook, new_photos):
        if old_workbook is not None:
            with open(old_workbook, 'rb') as orig, open(new_photos, 'rb') as new:
                pdf = PdfFileMerger()
                pdf.append(orig)
                pdf.append(new)
                pdf.write(new_photos)

    def create_workbook(self, user, subject):
        parent_dir = '..\\tmp'
        directory = str(user.user_id)
        path = os.path.join(parent_dir, directory)
        image_list = []
        old_workbook = None
        for filename in sorted(os.listdir(path), key=self.sort_by_number):
            if filename.split(".")[1] != 'pdf':
                image_list.append(path + '\\' + filename)
            else:
                old_workbook = filename
        new_photos = subject.name + "_" + user.first_name + '.pdf'
        self.convert(image_list, path + '\\' + new_photos)
        self.merge(old_workbook, new_photos)
        return new_photos

    def update_workbook(self):
        pass

    def get_workbook(self):
        pass

    def download_photos(self, user, subject_id):
        pass
        # model.pdf.update_photos(self, user, subject_id)
