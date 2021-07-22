from base.bot import bot
from base.user import Button
from config import phrases, ACCEPTED_FORMATS
from models.subject_model import subject_model
from models.user_model import user_model
from models.workbook_model import workbook_model
from decorators import common

if __name__ == '__main__':
    for user in user_model.users.values():
        if user.is_admin:
            bot.send_message(user.id, phrases['reboot'])


@bot.message_handler(commands=['start'])
def welcome(message):
    user_model.create_user(message)
    bot.welcome(message)


@bot.message_handler(commands=['help'])
@common.exception_handler
@common.admin_only
def help_reply(message):
    bot.help_reply(message)


@bot.message_handler(commands=['users'])
@common.exception_handler
@common.admin_only
def send_users(message):
    bot.send_users(message)


@bot.message_handler(commands=['make_admin'])
@common.exception_handler
@common.admin_only
def make_admin(message):
    user_id = message.text.split(maxsplit=1)[1]
    if user_id != "" and user_id.isdigit() and user_model.make_admin(user_id):
        bot.send_message(message.chat.id, phrases['admin-now'])


@bot.message_handler(commands=['remove_admin'])
@common.exception_handler
@common.admin_only
def make_admin(message):
    command, user_id = message.text.split(maxsplit=1)
    if user_id != "" and user_id.isdigit() and user_model.remove_admin(user_id):
        bot.send_message(message.chat.id, phrases['not-admin-anymore'])


@bot.message_handler(commands=['ban'])
@common.exception_handler
@common.admin_only
def ban_user(message):
    command, user_id = message.text.split(maxsplit=1)
    if user_id != "" and user_id.isdigit() and user_model.ban(user_id):
        bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['unban'])
@common.exception_handler
@common.admin_only
def unban_user(message):
    user_id = message.text.split(maxsplit=1)[1]
    if user_id != "" and user_id.isdigit() and user_model.unban(user_id):
        bot.send_banned_list(message.chat.id)


@bot.message_handler(commands=['create'])
@common.exception_handler
@common.admin_only
def create_subject(message):
    command, subject_name = message.text.split(maxsplit=1)
    if subject_name != "" and subject_model.create_subject(subject_name):
        bot.send_message(message.chat.id, phrases['subject-was-created'])
    else:
        bot.send_message(message.chat.id, phrases['subject-was-not-created'])


@bot.message_handler(commands=['remove'])
@common.exception_handler
@common.admin_only
def remove_subject(message):
    command, subject_name = message.text.split(maxsplit=1)
    if subject_name != "" and subject_model.remove_subject(subject_name):
        bot.send_message(message.chat.id, phrases['subject-was-removed'])
    else:
        bot.send_message(message.chat.id, phrases['subject-was-not-removed'])


@bot.message_handler(commands=['remove_workbook'])
@common.exception_handler
@common.admin_only
def remove_workbook(message):
    command, user_id, subject_name = message.text.split(maxsplit=2)
    workbook_model.delete_workbook(user_id, subject_name)
    bot.send_message(message.chat.id, phrases['workbook-was-deleted'])


@bot.message_handler(content_types=['photo'])
@common.exception_handler
def append_photo(message):
    user = user_model.get_user(message)
    user.photos.append(message.photo[-1].file_id)


@bot.message_handler(content_types=['document'])
@common.exception_handler
def append_file(message):
    user = user_model.get_user(message)
    extension = message.document.file_name.split(".")[1]
    if extension.lower() in ACCEPTED_FORMATS:
        user.files.append(message.document.file_id)
    else:
        bot.send_message(user.id, phrases['extension-error'] + extension)


@bot.message_handler(content_types=['text'])
@common.exception_handler
@common.ban_checker
def reply(message):
    user = user_model.get_user(message)
    if message.text == phrases['find-workbook']:
        user.button_state = Button.FIND
        bot.send_workbook_markup(user)

    elif message.text == phrases['send-workbook']:
        user.button_state = Button.SEND
        bot.send_upload_markup(user)

    elif message.text == phrases['delete-workbook']:
        user.button_state = Button.DELETE
        bot.send_workbook_markup(user)

    elif message.text == phrases['submit-button']:
        if len(user.photos) + len(user.files) == 0:
            bot.send_message(user.id, phrases['zero-photos-error'])
        else:
            bot.send_workbook_markup(user)

    elif message.text == phrases['cancel-button']:
        user.photos.clear()
        user.files.clear()
        user.workbooks_list.clear()
        user.subject_id = -1
        bot.send_default_markup(user)


@bot.callback_query_handler(func=lambda call: call.data == phrases['cancel-button'])
@common.exception_handler
@common.ban_checker
def callback_inline(call):
    user = user_model.get_user(call)
    bot.delete_message(user.id, call.message.message_id)
    user.subject_id = -1
    bot.send_default_markup(user)


@bot.callback_query_handler(func=lambda call: user_model.get_user(call).subject_id != -1)
@common.exception_handler
@common.ban_checker
def callback_inline(call):
    user = user_model.get_user(call)
    key = int(call.data)
    bot.delete_message(user.id, call.message.message_id)
    workbook = user.workbooks_list[key]
    user.subject_id = -1
    user.button_state = Button.NONE
    user.workbooks_list.clear()
    bot.send_workbook(user, workbook)
    bot.send_default_markup(user)


@bot.callback_query_handler(func=lambda call: user_model.get_user(call).button_state == Button.SEND)
@common.exception_handler
@common.ban_checker
def callback_inline(call):
    user = user_model.get_user(call)
    subject = subject_model.get_subject(int(call.data))

    bot.edit_message_text(phrases['downloading-photos'], user.id, call.message.message_id,
                          reply_markup=None)
    workbook_model.update_photos(bot, user, subject.id)
    bot.edit_message_text(phrases['creating-pdf'], user.id, call.message.message_id)
    wb_name = workbook_model.create_workbook(user, subject)
    bot.edit_message_text(phrases['workbook-is-ready'], user.id, call.message.message_id)
    wb_link = bot.send_workbook(user, wb_name)
    workbook_model.add_workbook(user, subject, wb_link)
    bot.send_default_markup(user)


@bot.callback_query_handler(func=lambda call: user_model.get_user(call).button_state == Button.FIND)
@common.exception_handler
@common.ban_checker
def callback_inline(call):
    user = user_model.get_user(call)
    subject = subject_model.get_subject(int(call.data))
    bot.delete_message(user.id, call.message.message_id)
    user.workbooks_list = workbook_model.get_workbooks_list(bot, user, subject.id)


@bot.callback_query_handler(func=lambda call: user_model.get_user(call).button_state == Button.DELETE)
@common.exception_handler
@common.ban_checker
def callback_inline(call):
    user = user_model.get_user(call)
    subject = subject_model.get_subject(int(call.data))
    bot.delete_message(user.id, call.message.message_id)
    workbook_model.delete_workbook(user.id, subject.name)
    bot.send_message(user.id, phrases['workbook-was-deleted'])


bot.polling(none_stop=True)
