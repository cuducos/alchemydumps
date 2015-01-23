# coding: utf-8


def confirm(assume_yes=False):
    confirmed = False
    if assume_yes:
        return True
    else:
        message = '\n==> Press "Y" to confirm, or anything else to abort: '
        confirmation = raw_input(message)
        if confirmation.lower() == 'y':
            confirmed = True
    return confirmed
