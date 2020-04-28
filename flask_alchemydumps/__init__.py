# coding: utf-8

from __future__ import absolute_import, print_function

from unipath import Path

from flask_alchemydumps.cli import alchemydumps


class _AlchemyDumpsConfig(object):

    def __init__(self, db=None, basedir=''):
        self.db = db
        self.basedir = Path(basedir).absolute()


class AlchemyDumps(object):

    def __init__(self, app=None, db=None, basedir=''):
        if app is not None and db is not None:
            self.init_app(app, db, basedir)
        if app is not None:
            app.cli.add_command(alchemydumps)

    @staticmethod
    def init_app(app, db, basedir=''):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['alchemydumps'] = _AlchemyDumpsConfig(db, basedir)
