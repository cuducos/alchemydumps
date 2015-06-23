# coding: utf-8

# python 2 and 3 compatibility
try:
    input = raw_input
except NameError:
    pass


def confirm(assume_yes=False):
    if assume_yes:
        return True
    message = '\n==> Press "Y" to confirm, or anything else to abort: '
    confirmation = input(message)
    if confirmation.lower() == 'y':
        return True
    return False
