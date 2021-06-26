import img2pdf
import os
from glob import glob
from controller.controller import model


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

    def convert(self, image_list):
        with open("name.pdf", "wb") as f:
            f.write(img2pdf.convert(image_list))

    def download_files(self, bot, file_ids, directory, idx):
        for f_id in file_ids:
            file_to_save = bot.get_file(f_id)
            file_extension = os.path.splitext(file_to_save.file_path)[1]
            filename = directory + "/" + str(idx) + file_extension.lower()
            idx += 1
            with open(filename, "wb") as new_file:
                new_file.write(bot.download_file(file_to_save.file_path))
        file_ids.clear()
        return idx

    def update_photos(self, bot, user, subject_id):
        idx = 1
        parent_dir = 'photos/' + model.subjects[subject_id].name
        directory = str(user.user_id)
        path = os.path.join(parent_dir, directory)
        if not os.path.isdir(path):
            os.mkdir(path)
        else:
            jpg_list = glob(path + '/' + '*.jpg')
            jpg_list += glob(path + '/' + '*.jpeg')
            jpg_list += glob(path + '/' + '*.png')
            max_el = 0
            for i in jpg_list:
                a = int((i.split('/')[-1]).split(".")[0])
                if a > max_el:
                    max_el = a
            idx = max_el + 1
        directory = parent_dir + '/' + directory
        old_index = idx
        idx = self.download_files(bot, user.photos, directory, idx)
        new_index = self.download_files(bot, user.files, directory, idx)
        return [old_index, new_index]

    def create_workbook(self):
        pass

    def update_workbook(self):
        pass

    def get_workbook(self):
        pass

    def download_photos(self, user, subject_id):
        pass
        # model.pdf.update_photos(self, user, subject_id)
