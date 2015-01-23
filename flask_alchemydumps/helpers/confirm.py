# coding: utf-8


def confirm(yes_to_all=False):
    message = '==> Press "Y" to confirm, or anything else to abort:'
    confirmed = False
    if yes_to_all:
        return True
    else:
        msg = '\n==> {} '.format(message)
        confirmation = raw_input(msg)
        if confirmation.lower() == 'y':
            confirmed = True
    return confirmed
