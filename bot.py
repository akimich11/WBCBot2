from telebot import TeleBot, types
from user import User, Button
from subject import Subject
from users_dict import UserDict, OrderedDict
from glob import glob
import os
import pickle


class Bot(TeleBot):
    PHRASE1 = "Найти дз"
    PHRASE2 = "Отправить тетрадку"
    FORMATS = ("jpg", "jpeg", "png")
    SUBJECTS = []

    def __init__(self, token):
        super().__init__(token, threaded=False)
        with open("data/users.pickle", "rb") as f:
            self.users = UserDict(pickle.loads(f.read()))
        with open("data/banned.pickle", "rb") as f:
            self.banned_users = OrderedDict(pickle.loads(f.read()))
        files = os.listdir("data")
        for el in files:
            if os.path.isdir("data/" + el):
                self.create_subject(el)

    def create_subject(self, name):
        Subject(name)
        self.SUBJECTS.append(name)

    def get_user(self, message):
        if message.from_user.id not in self.users:
            self.users[message.from_user.id] = User(message)
        return self.users[message.from_user.id]

    def get_subject(self, subject_id):
        pass

    def send_files(self, to_user: User, files):
        if len(files) > 1:
            input_documents = []
            for file_id in files:
                input_documents.append(types.InputMediaDocument(file_id))
            groups = [input_documents[i: i + 10] for i in range(0, len(input_documents), 10)]
            for group in groups:
                self.send_media_group(to_user.user_id, group)
        elif len(files) == 1:
            self.send_document(to_user.user_id, files[0])

    def send_markup(self, to_user: User):
        markup = types.InlineKeyboardMarkup(row_width=2)
        i = 0
        items = []
        for item in Bot.SUBJECTS:
            i += 1
            items.append(types.InlineKeyboardButton(item, callback_data=str(i)))
        markup.add(*items, types.InlineKeyboardButton("Другое", callback_data=str(i + 1)))
        self.send_message(to_user.user_id, 'Из какой тетрадки?', reply_markup=markup)

    def send_cycle(self, to_user: User):
        to_user.button_state = Button.NONE
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(self.PHRASE1)
        item2 = types.KeyboardButton(self.PHRASE2)
        markup.add(item1, item2)
        self.send_message(to_user.user_id, "Что-нибудь ещё?", reply_markup=markup)

    def ban(self, user_id):
        user_id = int(user_id)
        self.banned_users[user_id] = self.users[user_id]
        with open("data/banned.pickle", "wb") as f:
            f.write(pickle.dumps(self.banned_users))

    def unban(self, user_id):
        user_id = int(user_id)
        del self.banned_users[user_id]
        with open("data/banned.pickle", "wb") as f:
            f.write(pickle.dumps(self.banned_users))

    def send_banned_list(self, to_user: User):
        output = "Список забаненных пользователей:\n"
        for key in self.banned_users:
            output += str(self.banned_users[key]) + "\n"
        self.send_message(to_user, output)

    def is_user_banned(self, message):
        return message.chat.id in self.banned_users

    def download_files(self, file_ids, directory, idx):
        for f_id in file_ids:
            file_to_save = self.get_file(f_id)
            file_extension = os.path.splitext(file_to_save.file_path)[1]
            filename = directory + "/" + str(idx) + file_extension.lower()
            idx += 1
            with open(filename, "wb") as new_file:
                new_file.write(self.download_file(file_to_save.file_path))
        file_ids.clear()
        return idx

    def update_photos(self, user, subject_id):
        idx = 1
        parent_dir = 'photos/' + self.SUBJECTS[subject_id]
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
        idx = self.download_files(user.photos, directory, idx)
        new_index = self.download_files(user.files, directory, idx)
        return [old_index, new_index]
