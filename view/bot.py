from telebot import types, TeleBot

from model.subject_model import subject_model
from model.user_model import user_model
from user import User, Button
from workbook import Workbook


class Bot(TeleBot):
    PHRASE1 = "Найти дз"
    PHRASE2 = "Отправить тетрадку"
    FORMATS = ("jpg", "jpeg", "png")

    def welcome(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(self.PHRASE1)
        item2 = types.KeyboardButton(self.PHRASE2)
        markup.add(item1, item2)
        with open('../assets/changelog.txt', encoding='utf-8') as f:
            self.send_message(message.chat.id, "Привет, я бот с тетрадками, версия 3.0.\n"
                                               "Вот изменилось по сравнению с предыдущей версией:\n\n" + f.read())
        self.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=markup)

    def help_reply(self, message):
        with open('../assets/help.txt', encoding='utf-8') as f:
            self.send_message(message.chat.id, "Список команд, доступных администраторам:\n\n" + f.read())

    def send_upload_markup(self, user: User):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("готово")
        item2 = types.KeyboardButton("отмена")
        markup.add(item1, item2)
        self.send_message(user.id,
                          'Тогда просто кидай фотки, а я сделаю всё остальное.' +
                          ' Когда все фотки загрузятся, нажми кнопку "готово"',
                          reply_markup=markup)

    def send_users(self, message):
        output = ""
        for key in user_model.users:
            output += str(user_model.users[key])
        self.send_message(message.chat.id, output)

    def send_files(self, to_user: User, files):
        if len(files) > 1:
            input_documents = []
            for file_id in files:
                input_documents.append(types.InputMediaDocument(file_id))
            groups = [input_documents[i: i + 10] for i in range(0, len(input_documents), 10)]
            for group in groups:
                self.send_media_group(to_user.id, group)
        elif len(files) == 1:
            self.send_document(to_user.id, files[0])

    def send_workbook_markup(self, to_user: User):
        markup = types.InlineKeyboardMarkup(row_width=2)
        items = []
        for key in subject_model.subjects:
            items.append(types.InlineKeyboardButton(subject_model.subjects[key].name, callback_data=str(key)))
        markup.add(*items)
        self.send_message(to_user.id, 'По какому предмету?', reply_markup=markup)

    def send_default_markup(self, to_user: User):
        to_user.button_state = Button.NONE
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(self.PHRASE1)
        item2 = types.KeyboardButton(self.PHRASE2)
        markup.add(item1, item2)
        self.send_message(to_user.id, "Что-нибудь ещё?", reply_markup=markup)

    def send_workbook(self, to_user, workbook):
        if isinstance(workbook, Workbook):
            self.send_document(to_user.id, workbook.link)
        else:
            with open(workbook, 'rb') as f:
                file_id = self.send_document(to_user.id, f).document.file_id
            return file_id

    def send_workbooks_list(self, to_user, workbooks):
        if len(workbooks) != 0:
            output = ""
            for i, workbook in enumerate(workbooks):
                output += str(i + 1) + '. ' + str(workbook) + '\n'
            items = [str(i + 1) for i in range(len(workbooks))] + ["отмена"]
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            markup.add(*items)
            self.send_message(to_user.id, "Вот что у меня есть по предмету " + workbooks[0].subject.name
                              + ".\n" + output + "Что тебе нужно?", reply_markup=markup)
            to_user.subject_id = workbooks[0].subject.id
        else:
            self.send_message(to_user.id, "Ничего не нашёл :(")
            self.send_default_markup(to_user)

    def send_banned_list(self, to_user: User):
        output = "Список заблокированных пользователей:\n"
        for user_id in user_model.users:
            if user_model.users[user_id].is_banned:
                output += str(user_model.users[user_id]) + "\n"
        self.send_message(to_user.id, output)
