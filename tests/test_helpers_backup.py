# coding: utf-8

from .app import app
from flask.ext.alchemydumps.helpers.backup import Backup
from unittest import TestCase


class TestIdentificationHelper(TestCase):

    def tearDown(self):

        # clean up files and directories
        basedir = app.extensions['alchemydumps'].basedir
        directory = basedir.child('alchemydumps')
        directory.rmtree()

    def test_filter_files(self):
        with app.app_context():
            backup = Backup()
            date_ids = ['20141115172107', '20141112113214']
            class_names = ['User', 'Post']
            template = 'db-bkp-{}-{}.gz'
            files = list()
            for date_id in date_ids:
                for class_name in class_names:
                    files.append(template.format(date_id, class_name))
            expected = [template.format(date_ids[0], c) for c in class_names]
            backup.files = files
            self.assertEqual(backup.filter_files(date_ids[0]), expected)
