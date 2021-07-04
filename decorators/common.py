import traceback
import functools
from config import phrases, AKIM_ID
from base.bot import bot
from models.user_model import user_model


def admin_only(func):
    @functools.wraps(func)
    def wrapped(message, *args, **kwargs):
        if not user_model.get_user(message).is_admin:
            bot.send_message(message.chat.id, phrases['admin-only'])
            return False
        return func(message, *args, **kwargs)
    return wrapped


def ban_checker(func):
    @functools.wraps(func)
    def wrapped(message, *args, **kwargs):
        if user_model.get_user(message).is_banned:
            bot.send_message(message.chat.id, phrases['access-error'])
            return False
        return func(message, *args, **kwargs)
    return wrapped


def exception_handler(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except BaseException:
            bot.send_message(AKIM_ID, 'Unexpected error:\n' + traceback.format_exc())
            if len(args):
                bot.send_message(AKIM_ID, 'Caused by ' + user_model.get_user(args[0]).first_name)
                if hasattr(args[0], 'message'):
                    chat_id = args[0].message.chat.id
                else:
                    chat_id = args[0].chat.id
                bot.send_message(chat_id, phrases['unexpected-error'])
            return None
    return wrapped