# coding: utf-8

from .app import app, db, Post, User
from flask.ext.alchemydumps.helpers.sqlalchemy import get_sa_mapped_classes
from unittest import TestCase


class TestSQLAlchemyHelper(TestCase):

    def setUp(self):
        self.db = db
        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()
        db_file = app.extensions['alchemydumps'].basedir.child('test.db')
        db_file.remove()

    def test_mapped_classes(self):
        classes = get_sa_mapped_classes(self.db)
        self.assertIn(User, classes)
        self.assertIn(Post, classes)
        self.assertEqual(len(classes), 2)