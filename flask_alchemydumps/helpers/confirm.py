# coding: utf-8


def confirm(yes_to_all=False):
    confirmed = False
    if yes_to_all:
        return True
    else:
        message = '\n==> Press "Y" to confirm, or anything else to abort: '
        confirmation = raw_input(message)
        if confirmation.lower() == 'y':
            confirmed = True
    return confirmed
