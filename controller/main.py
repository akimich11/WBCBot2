from user import Button
from model.models import user_model, subject_model, workbook_model
from view.bot import Bot


# todo: commit decorator


bot = Bot('1471952931:AAFp0m8i76vG0urF-Q8OeGfQeCmJCdKaoMs')


if __name__ == '__main__':
    for user in user_model.users.values():
        if user.is_admin:
            bot.send_message(user.id, "перезагрузился")


@bot.message_handler(commands=['start'])
def welcome(message):
    user_model.create_user(message)
    bot.welcome(message)


@bot.message_handler(commands=['help'])
def help_reply(message):
    if user_model.users[message.chat.id].is_admin:
        bot.help_reply(message)
    else:
        bot.send_message(message.chat.id, "Команда доступна только администраторам")


@bot.message_handler(commands=['users'])
def send_users(message):
    if user_model.users[message.chat.id].is_admin:
        bot.send_users(message)
    else:
        bot.send_message(message.chat.id, "Команда доступна только администраторам")


def admin_console(message, func):
    if not user_model.users[message.chat.id].is_admin:
        bot.send_message(message.chat.id, "Команда доступна только администраторам")
        return False
    else:
        command, arg = message.text.split(maxsplit=1)
        if arg != "":
            return func(arg)


@bot.message_handler(commands=['make_admin'])
def make_admin(message):
    if admin_console(message, user_model.make_admin):
        bot.send_message(message.chat.id, "Пользователь теперь администратор")


@bot.message_handler(commands=['remove_admin'])
def make_admin(message):
    if admin_console(message, user_model.remove_admin):
        bot.send_message(message.chat.id, "Пользователь больше не администратор")


@bot.message_handler(commands=['ban'])
def ban_user(message):
    admin_console(message, user_model.ban)
    bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['unban'])
def unban_user(message):
    admin_console(message, user_model.unban)
    bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['create'])
def create_subject(message):
    if admin_console(message, subject_model.create_subject):
        bot.send_message(message.chat.id, "Предмет создан")
    else:
        bot.send_message(message.chat.id, "Предмет не создан")


@bot.message_handler(commands=['remove'])
def create_subject(message):
    if admin_console(message, subject_model.remove_subject):
        bot.send_message(message.chat.id, "Предмет удалён")
    else:
        bot.send_message(message.chat.id, "Предмет не удалён")


@bot.message_handler(content_types=['photo'])
def append_photo(message):
    user = user_model.get_user(message)
    user.photos.append(message.photo[-1].file_id)


@bot.message_handler(content_types=['document'])
def append_file(message):
    user = user_model.get_user(message)
    extension = message.document.file_name.split(".")[1]
    if extension.lower() in Bot.FORMATS:
        user.files.append(message.document.file_id)
    else:
        bot.send_message(user.id, "Расширение файла (" + extension + ") не поддерживается")


@bot.message_handler(content_types=['text'])
def reply(message):
    if user_model.users[message.chat.id].is_banned:
        bot.send_message(message.chat.id, "Вы заблокированы, бот для вас недоступен")
    else:
        user = user_model.get_user(message)
        if message.text == Bot.PHRASE1:
            user.button_state = Button.FIND
            bot.send_workbook_markup(user)

        elif message.text == Bot.PHRASE2:
            user.button_state = Button.SEND
            bot.send_upload_markup(user)

        elif message.text == "готово":
            if len(user.photos) == 0 and len(user.files) == 0:
                bot.send_message(user.id, "Сначала скинь фотки")
            else:
                bot.send_workbook_markup(user)

        elif message.text == "отмена":
            user.photos.clear()
            user.files.clear()
            user.subject_id = -1
            bot.send_default_markup(user)

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
        user = user_model.get_user(call)
        subject = subject_model.get_subject(int(call.data))

        if user.button_state == Button.SEND:
            bot.edit_message_text("Идёт загрузка фотографий...", user.id, call.message.message_id,
                                  reply_markup=None)
            workbook_model.update_photos(bot, user, subject.id)
            bot.edit_message_text("Идёт создание pdf...", user.id, call.message.message_id)
            wb_name = workbook_model.create_workbook(user, subject)
            bot.edit_message_text("Тетрадка загружена", user.id, call.message.message_id)
            wb_link = bot.send_workbook(user, wb_name)
            workbook_model.add_workbook(user, subject, wb_link)
            bot.send_default_markup(user)

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
