import sqlite3
import functools


def db_connector(function):
    @functools.wraps(function)
    def wrapped(self, *args, **kwargs):
        self.conn = sqlite3.connect("assets/identifier.sqlite", check_same_thread=False)
        self.cursor = self.conn.cursor()
        result = function(self, *args, **kwargs)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        return result

    return wrapped
