# coding: utf-8

from flask import current_app
from sqlalchemy.ext.serializer import dumps, loads


class AlchemyDumpsDatabase(object):

    def __init__(self):
        self.do_not_backup = list()

    @staticmethod
    def db():
        return current_app.extensions['alchemydumps'].db

    def get_mapped_classes(self):
        """Gets a list of SQLALchemy mapped classes"""
        db = self.db()
        models = list()
        for model_name in db.Model.__subclasses__():
            if model_name not in self.do_not_backup:
                models.append(model_name)
        return models

    def get_data(self):
        """Go through every mapped class and dumps the data"""
        db = self.db()
        data = dict()
        for model in self.get_mapped_classes():
            query = db.session.query(model)
            data[model.__name__] = dumps(query.all())
        return data

    def parse_data(self, contents):
        """Loads a dump and convert it into a ? """
        db = self.db()
        return loads(contents, db.metadata, db.session)
