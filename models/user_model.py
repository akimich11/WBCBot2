import mysql.connector as mysql
import config
from base.user import User
from decorators import database


class UserModel:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.users = dict()
        self.create_database()

    @database.connector
    def create_database(self):
        users_create_query = """CREATE TABLE IF NOT EXISTS users (
                                id INT PRIMARY KEY, first_name TEXT, last_name TEXT, username TEXT,
                                is_admin INT DEFAULT 0, is_banned INT DEFAULT 0);"""
        self.cursor.execute(users_create_query)
        self.cursor.execute("""SELECT * FROM users""")
        data = self.cursor.fetchall()
        if data is not None:
            for row in data:
                self.users[row[0]] = User(*row)

    @database.connector
    def create_user(self, message):
        insert_user = (
            message.from_user.id, message.from_user.first_name, message.from_user.last_name,
            message.from_user.username,
            message.from_user.id == config.AKIM_ID, 0)  # akim is admin by default, others not
        self.cursor.execute("""INSERT IGNORE INTO users VALUES (%s,%s,%s,%s,%s,%s)""", insert_user)
        return User(*insert_user)

    def get_user(self, message):
        if message.from_user.id not in self.users:
            self.users[message.from_user.id] = self.create_user(message)
        return self.users[message.from_user.id]

    @database.connector
    def ban(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_banned = True
        self.cursor.execute("UPDATE users SET is_banned=1 WHERE id=" + str(user_id))
        return True

    @database.connector
    def unban(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_banned = False
        self.cursor.execute("UPDATE users SET is_banned=0 WHERE id=" + str(user_id))
        return True

    @database.connector
    def make_admin(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_admin = True
        self.cursor.execute("UPDATE users SET is_admin=1 WHERE id=" + str(user_id))
        return True

    @database.connector
    def remove_admin(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_admin = False
        self.cursor.execute("UPDATE users SET is_admin=0 WHERE id=" + str(user_id))
        return True


user_model = UserModel()
