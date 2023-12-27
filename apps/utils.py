import KnowWho.settings


def print_debug(*args):
    if KnowWho.settings.DEBUG:
        print(*args)


class Result:
    def __init__(self):
        self.status = False
        self.message = ''

    def is_success(self):
        return self.status

    def set_success(self):
        self.status = True

    def set_message(self, content):
        self.message = content

    def get_message(self):
        return self.message
