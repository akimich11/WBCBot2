from PIL import Image
from user import User
from bot import Bot


class Workbook:
    def __init__(self, user: User, subject_id):
        self.user = user
        self.subject_id = subject_id
        self.pdfs = []

    @staticmethod
    def open_image(filename):
        try:
            temp = Image.open(filename + ".jpg")
        except FileNotFoundError:
            try:
                temp = Image.open(filename + ".png")
                temp = temp.convert('RGB')
            except FileNotFoundError:
                temp = Image.open(filename + ".jpeg")
        image = temp.copy()
        temp.close()
        return image

    def create_pdfs(self, old_index, new_index):
        im_list = []
        pdf_list = []
        directory = 'photos/' + Bot.SUBJECTS[self.subject_id] + '/' + str(self.user.user_id) + '/'

        new_photos = new_index - old_index
        remainder = (old_index - 1) % 20
        photos_to_append = new_photos + remainder
        start_position = new_index - photos_to_append
        complete_pdfs = (old_index - 1) // 20

        iterations = (photos_to_append - 1) // 20 + 1
        for i in range(iterations):
            if i == 0:
                im1 = self.open_image(directory + str(start_position))
                j = (start_position + 1) % 20
            else:
                im1 = self.open_image(directory + str(20 * (complete_pdfs + i) + 1))
                j = 2
            while j < 21:
                page_number = 20 * (complete_pdfs + i) + j
                if page_number > new_index - 1:
                    break
                im_list.append(self.open_image(directory + str(page_number)))
                j += 1
            pdf_filename = directory + Bot.SUBJECTS[self.subject_id] + "_" + self.user.first_name \
                           + "_" + str(complete_pdfs + i + 1) + ".pdf "
            im1.save(pdf_filename, "PDF", resolution=100.0, save_all=True, append_images=im_list)
            pdf_list.append(pdf_filename)
            im1.close()
            im_list.clear()
            return pdf_list

    def append_pdfs(self, old_index, docs):
        # directory = 'photos/' + Bot.SUBJECTS[self.subject_id] + "/"
        # subject_database = directory + Bot.SUBJECTS[self.subject_id] + '.csv'
        # lines = self.remove_line_by_id(subject_database, str(self.user.user_id))
        # with open(subject_database, 'w', encoding='utf-8') as f:
        #     tz = timezone('Europe/Minsk')
        #     now = datetime.now(tz)
        #     f.write(lines + str(self.user.user_id) + ',' + self.user.first_name + ',' +
        #     now.strftime("%d.%m.%Y в %H:%M") + '\n')
        # student_files = directory + str(self.user.user_id) + "/" + self.user.first_name + '.txt'
        if old_index % 20 != 1:
            self.pdfs.pop()
        self.pdfs.extend(docs)

