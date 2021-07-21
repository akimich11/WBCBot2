from config import phrases, TOKEN
from telebot import types, TeleBot
from models.subject_model import subject_model
from models.user_model import user_model
from .user import User, Button
from .workbook import Workbook


class Bot(TeleBot):
    def __init__(self, token):
        super().__init__(token, threaded=False)

    def welcome(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(phrases['find-workbook'])
        item2 = types.KeyboardButton(phrases['send-workbook'])
        item3 = types.KeyboardButton(phrases['delete-workbook'])
        markup.add(item1, item2, item3)
        with open('assets/changelog.txt', encoding='utf-8') as f:
            self.send_message(message.chat.id, phrases['welcome-message'] + f.read())
        self.send_message(message.chat.id, phrases['actions'], reply_markup=markup)

    def help_reply(self, message):
        with open('assets/help.txt', encoding='utf-8') as f:
            self.send_message(message.chat.id, phrases['help-message'] + f.read())

    def send_upload_markup(self, user: User):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(phrases['submit-button'])
        item2 = types.KeyboardButton(phrases['cancel-button'])
        markup.add(item1, item2)
        self.send_message(user.id, phrases['upload-text'] + phrases['submit-button'],
                          reply_markup=markup)

    def send_users(self, message):
        output = ""
        for user_id in user_model.users:
            output += str(user_model.users[user_id])
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
        for subj_id in subject_model.subjects:
            items.append(types.InlineKeyboardButton(subject_model.subjects[subj_id].name, callback_data=str(subj_id)))
        markup.add(*items)
        self.send_message(to_user.id, phrases['choose-subject'], reply_markup=markup)

    def send_default_markup(self, to_user: User):
        to_user.button_state = Button.NONE
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(phrases['find-workbook'])
        item2 = types.KeyboardButton(phrases['send-workbook'])
        item3 = types.KeyboardButton(phrases['delete-workbook'])
        markup.add(item1, item2, item3)
        self.send_message(to_user.id, phrases['anything-else'], reply_markup=markup)

    def send_workbook(self, to_user, workbook):
        if isinstance(workbook, Workbook):
            self.send_document(to_user.id, workbook.link)
        else:
            with open(workbook, 'rb') as f:
                file_id = self.send_document(to_user.id, f).document.file_id
            return file_id

    def send_workbooks_list(self, to_user, workbooks):
        if len(workbooks) != 0:
            markup = types.InlineKeyboardMarkup(row_width=1)
            items = [types.InlineKeyboardButton(str(workbook), callback_data=str(i))
                     for i, workbook in enumerate(workbooks)]
            items.append(types.InlineKeyboardButton(phrases['cancel-button'], callback_data=phrases['cancel-button']))
            markup.add(*items)
            self.send_message(to_user.id, workbooks[0].subject.name +
                              "\n" + phrases['choose-workbook'], reply_markup=markup)
            to_user.subject_id = workbooks[0].subject.id
        else:
            self.send_message(to_user.id, phrases['not-found'])
            self.send_default_markup(to_user)

    def send_banned_list(self, chat_id):
        output = phrases['banlist']
        for user_id in user_model.users:
            if user_model.users[user_id].is_banned:
                output += str(user_model.users[user_id]) + "\n"
        self.send_message(chat_id, output)


bot = Bot(TOKEN)
