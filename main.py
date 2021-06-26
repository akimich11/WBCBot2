from bot import Bot
from user import Button
from telebot import types

bot = Bot('1471952931:AAFp0m8i76vG0urF-Q8OeGfQeCmJCdKaoMs')

if __name__ == '__main__':
    bot.send_message(270241310, "перезагрузился")


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.create_user(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(Bot.PHRASE1)
    item2 = types.KeyboardButton(Bot.PHRASE2)
    markup.add(item1, item2)
    with open('data/changelog.txt', encoding='utf-8') as f:
        bot.send_message(message.chat.id, "Привет, я бот с тетрадками, версия 3.0.\n"
                                          "Вот изменилось по сравнению с предыдущей версией:\n\n" + f.read())
    bot.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_reply(message):
    if bot.users[message.chat.id].is_admin:
        with open('data/help.txt', encoding='utf-8') as f:
            bot.send_message(message.chat.id, "Список команд, доступных администраторам:\n\n" + f.read())
    else:
        bot.send_message(message.chat.id, "Команда доступна только администраторам")


@bot.message_handler(commands=['users'])
def send_users(message):
    if not bot.users[message.chat.id].is_admin:
        bot.send_message(message.chat.id, "Команда доступна только администраторам")
    else:
        output = ""
        for key in bot.users:
            output += str(bot.users[key])
        bot.send_message(message.chat.id, output)


def admin_console(message, func):
    if not bot.users[message.chat.id].is_admin:
        bot.send_message(message.chat.id, "Команда доступна только администраторам")
        return False
    else:
        command, arg = message.text.split(maxsplit=1)
        if arg != "":
            return func(arg)


@bot.message_handler(commands=['make_admin'])
def make_admin(message):
    if admin_console(message, bot.make_admin):
        bot.send_message(message.chat.id, "Пользователь теперь администратор")


@bot.message_handler(commands=['remove_admin'])
def make_admin(message):
    if admin_console(message, bot.remove_admin):
        bot.send_message(message.chat.id, "Пользователь больше не администратор")


@bot.message_handler(commands=['ban'])
def ban_user(message):
    admin_console(message, bot.ban)
    bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['unban'])
def unban_user(message):
    admin_console(message, bot.unban)
    bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['create'])
def create_subject(message):
    if admin_console(message, bot.create_subject):
        bot.send_message(message.chat.id, "Предмет создан")
    else:
        bot.send_message(message.chat.id, "Предмет не создан")


@bot.message_handler(commands=['remove'])
def create_subject(message):
    if admin_console(message, bot.remove_subject):
        bot.send_message(message.chat.id, "Предмет удалён")
    else:
        bot.send_message(message.chat.id, "Предмет не удалён")


@bot.message_handler(content_types=['photo'])
def append_photo(message):
    user = bot.get_user(message)
    user.photos.append(message.photo[-1].file_id)


@bot.message_handler(content_types=['document'])
def append_file(message):
    user = bot.get_user(message)
    extension = message.document.file_name.split(".")[1]
    if extension.lower() in Bot.FORMATS:
        user.files.append(message.document.file_id)
    else:
        bot.send_message(user.user_id, "Расширение файла (" + extension + ") не поддерживается")


@bot.message_handler(content_types=['text'])
def reply(message):
    # if bot.is_user_banned(message):
    #    bot.send_message(message.chat.id, "Вы забанены, бот для вас недоступен")
    # else:
    user = bot.get_user(message)
    if message.text == Bot.PHRASE1:
        user.button_state = Button.FIND
        bot.send_markup(user)

    elif message.text == Bot.PHRASE2:
        user.button_state = Button.SEND
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("готово")
        item2 = types.KeyboardButton("отмена")
        markup.add(item1, item2)
        bot.send_message(user.user_id,
                         'Тогда просто кидай фотки, а я сделаю всё остальное.' +
                         ' Когда все фотки загрузятся, нажми кнопку "готово"',
                         reply_markup=markup)

    elif message.text == "готово":
        if len(user.photos) == 0 and len(user.files) == 0:
            bot.send_message(user.user_id, "Сначала скинь фотки")
        else:
            bot.send_markup(user)

    elif message.text == "отмена":
        # user.photos.clear()
        # user.files.clear()
        # user.subject_id = -1
        bot.send_cycle(user)

    elif user.subject_id != -1:
        pass
        # key = int(message.text)
        # files = file.get_file_id(user.subject_id, key - 1)
        # user.subject_id = -1
        # send_group(user, files)
        # send_cycle(user)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        user = bot.get_user(call)
        subject_id = int(call.data) - 1
        subject = bot.get_subject(subject_id)

        if user.button_state == Button.SEND:
            workbook = subject.get_workbook(user, subject_id)
            bot.edit_message_text("Идёт загрузка фотографий...", user.user_id, call.message.message_id,
                                  reply_markup=None)
            old_index, new_index = bot.update_photos(user, subject_id)
            bot.edit_message_text("Идёт создание pdf...", user.user_id, call.message.message_id)
            filenames = workbook.create_pdfs(old_index, new_index)
            bot.edit_message_text("Тетрадка загружена", user.user_id, call.message.message_id)
            docs = []
            for filename in filenames:
                docs.append(bot.send_document(call.message.chat.id, open(filename, "rb")))
            workbook.append_pdfs(old_index, docs)
            bot.send_cycle(user)

        # elif user.button_state == Button.FIND:
        #     bot.delete_message(user.user_id, call.message.message_id)
        #
        #     docs, lines_number = file.get_documents_list(subject_id)
        #     if lines_number != 0:
        #         items = ["отмена"]
        #         for i in range(lines_number):
        #             items.append(str(i + 1))
        #         markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        #         markup.add(*items)
        #         bot.send_message(user.user_id, "Вот что у меня есть по предмету " + docs + "\nЧто тебе нужно?",
        #                            reply_markup=markup)
        #         user.subject_id = subject_id
        #     else:
        #         bot.send_message(user.user_id, "Ничего не нашёл :(")
        #         bot.send_cycle(user)


bot.polling(none_stop=True)
