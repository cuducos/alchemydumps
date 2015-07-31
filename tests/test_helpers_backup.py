# coding: utf-8

from .app import app
from flask.ext.alchemydumps.helpers.backup import Backup
from time import gmtime, strftime
from unipath import Path
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

    def test_date_id_helpers(self):
        with app.app_context():
            backup = Backup()
            reference = gmtime()
            date_id = backup.create_id(reference)
            self.assertEqual(backup.parsed_id(date_id),
                             strftime('%b %d, %Y at %H:%M:%S', reference))

    def test_get_ids(self):
        with app.app_context():

            # create some files
            backup = Backup()
            date_ids = [
                '20110824045557',
                '20100106120931',
                '20090728192328',
                '20100112115416'
            ]
            class_names = ['Post', 'User']
            for date_id in date_ids:
                for class_name in class_names:
                    name = backup.get_name(date_id, class_name)
                    backup.create_file(name, '')

            # restart Backup() and assert
            backup = Backup()
            self.assertEqual(sorted(date_ids), sorted(backup.get_ids()))

            # clean up to avoid messing up other tests
            for name in backup.files:
                backup.delete_file(name)
            backup = Backup()
            self.assertEqual(len(backup.files), 0)

    def test_valid(self):
        with app.app_context():

            # create some files
            backup = Backup()
            date_ids = [
                '20110824045557',
                '20100106120931',
                '20090728192328',
                '20100112115416'
            ]
            class_names = ['Post', 'User']
            for date_id in date_ids:
                for class_name in class_names:
                    name = backup.get_name(date_id, class_name)
                    backup.create_file(name, '')

            # restart Backup() and assert
            backup = Backup()
            self.assertTrue(backup.valid('20110824045557'))
            self.assertFalse(backup.valid('20110824045--'))

            # clean up to avoid messing up other tests
            for name in backup.files:
                backup.delete_file(name)
            backup = Backup()
            self.assertEqual(len(backup.files), 0)


class TestPath(TestCase):

    def test_get_path_with_local_storage(self):
        with app.app_context():
            backup = Backup()
            path = Path(backup.path)
            self.assertTrue(path.exists())
            self.assertTrue(path.isdir())
