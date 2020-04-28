import click


class Confirm:
    def __init__(self, assume_yes=False):
        self.assume_yes = assume_yes

    def ask(self):
        if self.assume_yes:
            return True

        click.echo('\n==> Press "Y" to confirm, or anything else to abort: ')
        return click.getchar().lower() == "y"
