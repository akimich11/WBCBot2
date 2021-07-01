from user import Button
from model.subject_model import subject_model
from model.user_model import user_model
from model.workbook_model import workbook_model
from view.bot import Bot
import functools


bot = Bot('1471952931:AAFp0m8i76vG0urF-Q8OeGfQeCmJCdKaoMs')


if __name__ == '__main__':
    for user in user_model.users.values():
        if user.is_admin:
            bot.send_message(user.id, "перезагрузился")


def admin_only(func):
    @functools.wraps(func)
    def wrapped(message, *args, **kwargs):
        if not user_model.get_user(message).is_admin:
            bot.send_message(message.chat.id, "Команда доступна только администраторам")
            return False
        return func(message, *args, **kwargs)
    return wrapped


@bot.message_handler(commands=['start'])
def welcome(message):
    user_model.create_user(message)
    bot.welcome(message)


@bot.message_handler(commands=['help'])
@admin_only
def help_reply(message):
    bot.help_reply(message)


@bot.message_handler(commands=['users'])
@admin_only
def send_users(message):
    bot.send_users(message)


@bot.message_handler(commands=['make_admin'])
@admin_only
def make_admin(message):
    user_id = message.text.split(maxsplit=1)[1]
    if user_id != "" and user_id.isdigit() and user_model.make_admin(user_id):
        bot.send_message(message.chat.id, "Пользователь теперь администратор")


@bot.message_handler(commands=['remove_admin'])
@admin_only
def make_admin(message):
    command, user_id = message.text.split(maxsplit=1)
    if user_id != "" and user_id.isdigit() and user_model.remove_admin(user_id):
        bot.send_message(message.chat.id, "Пользователь больше не администратор")


@bot.message_handler(commands=['ban'])
@admin_only
def ban_user(message):
    command, user_id = message.text.split(maxsplit=1)
    if user_id != "" and user_id.isdigit() and user_model.ban(user_id):
        bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['unban'])
@admin_only
def unban_user(message):
    user_id = message.text.split(maxsplit=1)[1]
    if user_id != "" and user_id.isdigit() and user_model.unban(user_id):
        bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['create'])
@admin_only
def create_subject(message):
    command, subject_name = message.text.split(maxsplit=1)
    if subject_name != "" and subject_model.create_subject(subject_name):
        bot.send_message(message.chat.id, "Предмет создан")
    else:
        bot.send_message(message.chat.id, "Предмет не создан")


@bot.message_handler(commands=['remove'])
@admin_only
def remove_subject(message):
    command, subject_name = message.text.split(maxsplit=1)
    if subject_name != "" and subject_model.remove_subject(subject_name):
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
    user = user_model.get_user(message)
    if user.is_banned:
        bot.send_message(message.chat.id, "Вы заблокированы, бот для вас недоступен")
    else:
        if message.text == Bot.PHRASE1:
            user.button_state = Button.FIND
            bot.send_workbook_markup(user)

        elif message.text == Bot.PHRASE2:
            user.button_state = Button.SEND
            bot.send_upload_markup(user)

        elif message.text == "готово":
            if len(user.photos) == 0 and len(user.files) == 0:
                bot.send_message(user.id, "Загружено 0 фотографий, нужно больше")
            else:
                bot.send_workbook_markup(user)

        elif message.text == "отмена":
            user.photos.clear()
            user.files.clear()
            user.workbooks_list.clear()
            user.subject_id = -1
            bot.send_default_markup(user)

        elif user.subject_id != -1:
            key = int(message.text)
            workbook = user.workbooks_list[key - 1]
            user.subject_id = -1
            user.workbooks_list.clear()
            bot.send_workbook(user, workbook)
            bot.send_default_markup(user)


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

        elif user.button_state == Button.FIND:
            bot.delete_message(user.id, call.message.message_id)
            user.workbooks_list = workbook_model.get_workbooks_list(bot, user, subject.id)


bot.polling(none_stop=True)
