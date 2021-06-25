class Subject:

    def __init__(self, name, subject_id):
        self.id = subject_id
        self.name = name

    def __str__(self):
        # print workbooks list here
        return "Предмет {}".format(self.name)
