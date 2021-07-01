import sqlite3
from user import User
from decorators import db_connector


class UserModel:
    def __init__(self):
        self.conn = sqlite3.connect("../assets/identifier.sqlite", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.users = dict()
        self.create_database()

    @db_connector
    def create_database(self):
        users_create_query = """CREATE TABLE IF NOT EXISTS users (
                                id integer primary key, first_name text, last_name text, username text,
                                is_admin integer default 0, is_banned integer default 0);"""
        self.cursor.execute(users_create_query)
        for row in self.cursor.execute("""SELECT * FROM users""").fetchall():
            self.users[row[0]] = User(*row)

    @db_connector
    def create_user(self, message):
        if not self.cursor.execute("""SELECT * FROM users WHERE id=?""", (message.from_user.id,)).fetchall():
            insert_user = (
                message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                message.from_user.username, 0, 0)
            self.cursor.execute("""INSERT INTO users VALUES (?,?,?,?,?,?)""", insert_user)
            return User(*insert_user)

    def get_user(self, message):
        if message.from_user.id not in self.users:
            self.users[message.from_user.id] = self.create_user(message)
        return self.users[message.from_user.id]

    @db_connector
    def ban(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_banned = True
        self.cursor.execute("UPDATE users SET is_banned=1 WHERE id=" + str(user_id))
        return True

    @db_connector
    def unban(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_banned = False
        self.cursor.execute("UPDATE users SET is_banned=0 WHERE id=" + str(user_id))
        return True

    @db_connector
    def make_admin(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_admin = True
        self.cursor.execute("UPDATE users SET is_admin=1 WHERE id=" + str(user_id))
        return True

    @db_connector
    def remove_admin(self, user_id):
        user_id = int(user_id)
        self.users[user_id].is_admin = False
        self.cursor.execute("UPDATE users SET is_admin=0 WHERE id=" + str(user_id))
        return True


user_model = UserModel()
