from telebot import types, TeleBot
from controller.controller import model
from user import User, Button


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
        self.send_message(user.user_id,
                          'Тогда просто кидай фотки, а я сделаю всё остальное.' +
                          ' Когда все фотки загрузятся, нажми кнопку "готово"',
                          reply_markup=markup)

    def send_users(self, message):
        output = ""
        for key in model.users:
            output += str(model.users[key])
        self.send_message(message.chat.id, output)

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

    def send_workbook_markup(self, to_user: User):
        markup = types.InlineKeyboardMarkup(row_width=2)
        i = 0
        items = []
        for key in model.subjects:
            i += 1
            items.append(types.InlineKeyboardButton(model.subjects[key].name, callback_data=str(i)))
        markup.add(*items, types.InlineKeyboardButton("Другое", callback_data=str(i + 1)))
        self.send_message(to_user.user_id, 'Из какой тетрадки?', reply_markup=markup)

    def send_default_markup(self, to_user: User):
        to_user.button_state = Button.NONE
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(self.PHRASE1)
        item2 = types.KeyboardButton(self.PHRASE2)
        markup.add(item1, item2)
        self.send_message(to_user.user_id, "Что-нибудь ещё?", reply_markup=markup)

    def send_banned_list(self, to_user: User):
        output = "Список забаненных пользователей:\n"
        for user_id in model.users:
            if model.users[user_id].is_banned:
                output += str(model.users[user_id]) + "\n"
        self.send_message(to_user, output)
