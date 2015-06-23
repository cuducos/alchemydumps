# coding: utf-8

from flask import current_app
from sqlalchemy.ext.serializer import dumps, loads


class AlchemyDumpsDatabase(object):

    def __init__(self):
        self.do_not_backup = list()
        self.models = list()

    @staticmethod
    def db():
        return current_app.extensions['alchemydumps'].db

    def get_mapped_classes(self):
        """Gets a list of SQLALchemy mapped classes"""
        db = self.db()
        self.add_subclasses(db.Model)
        return self.models

    def add_subclasses(self, model):
        """Feed self.models filtering `do_not_backup` and abstract models"""
        if model.__subclasses__():
            for submodel in model.__subclasses__():
                self.add_subclasses(submodel)
        else:
            self.models.append(model)

    def get_data(self):
        """Go through every mapped class and dumps the data"""
        db = self.db()
        data = dict()
        for model in self.get_mapped_classes():
            query = db.session.query(model)
            data[model.__name__] = dumps(query.all())
        return data

    def parse_data(self, contents):
        """Loads a dump and convert it into rows """
        db = self.db()
        return loads(contents, db.metadata, db.session)
