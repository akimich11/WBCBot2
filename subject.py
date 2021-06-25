import os


class Subject:
    def __init__(self, name):
        self.name = name
        path = "data/" + name
        if not os.path.exists(path):
            os.mkdir(path)
            with open(path + "/" + name + ".csv", "w"):
                pass
        else:
            workbooks = os.listdir(path)
