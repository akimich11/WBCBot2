from collections import OrderedDict
import pickle


def sort_by_time(user):
    return user.last_seen


class UserDict(OrderedDict):
    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        with open("data/users.pickle", "wb") as file:
            file.write(pickle.dumps(self))

    def access_by_time(self):
        output = "Время доступа к боту:\n"
        access_list = sorted(list(self.values()), key=sort_by_time)
        for user in access_list:
            output += user.get_access_time() + "\n"
        return output

    def __str__(self):
        output = "Список пользователей бота:\n"
        for user in self:
            output += str(self[user]) + "\n"
        return output
