from pathlib import Path

from flask_alchemydumps.cli import alchemydumps


class AlchemyDumpsConfig:
    def __init__(self, db=None, basedir=""):
        self.db = db
        self.basedir = Path(basedir).absolute()


class AlchemyDumps:
    def __init__(self, app=None, db=None, basedir=""):
        if app is not None and db is not None:
            self.init_app(app, db, basedir)

    @staticmethod
    def init_app(app, db, basedir=""):
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["alchemydumps"] = AlchemyDumpsConfig(db, basedir)

        if app is not None:
            app.cli.add_command(alchemydumps)
