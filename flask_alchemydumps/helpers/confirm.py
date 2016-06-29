# coding: utf-8


class Confirm(object):

    def __init__(self, assume_yes=False):
        self.assume_yes = assume_yes

    @staticmethod
    def input(message):
        try:
            return raw_input(message)
        except NameError:
            return input(message)

    def ask(self):
        if self.assume_yes:
            return True

        message = '\n==> Press "Y" to confirm, or anything else to abort: '
        confirmation = self.input(message)
        return True if str(confirmation).lower() == 'y' else False
