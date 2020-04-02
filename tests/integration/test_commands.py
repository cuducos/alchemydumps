# coding: utf-8

import os
from shutil import rmtree
from unittest import TestCase
from tempfile import mkdtemp

from flask_alchemydumps import create, history, restore, remove, autoclean
from flask_alchemydumps.helper.backup import Backup, LocalTools

from .app import Comments, Post, SomeControl, User, app, db


# Python 2 and 3 compatibility (mock)
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestCommands(TestCase):

    def setUp(self):

        # create database
        self.db = db
        self.db.create_all()

        # feed user table
        db.session.add(User(email=u'me@example.etc'))
        db.session.commit()

        # feed post table
        db.session.add(Post(title=u'Post 1',
                            content=u'Lorem ipsum...',
                            author_id=1))
        db.session.add(Post(title=u'Post 2',
                            content=u'Ipsum lorem...',
                            author_id=1))

        # feed some control table
        db.session.add(SomeControl(uuid='1'))

        # commit
        db.session.commit()

        # temp directory
        self.dir = mkdtemp()

    def tearDown(self):

        # clean up database and backup directory
        self.db.drop_all()

        # delete temp directory
        rmtree(self.dir)

    @patch.object(LocalTools, 'normalize_path')
    def test_create_restore_remove(self, mock_path):
        mock_path.return_value = self.dir + os.sep

        with app.app_context():

            # assert data was inserted
            posts = Post.query.count()
            authors = User.query.count()
            controls = SomeControl.query.count()
            comments = Comments.query.count()
            self.assertEqual(posts, 2)
            self.assertEqual(authors, 1)
            self.assertEqual(controls, 1)
            self.assertEqual(comments, 0)

            # create and assert backup files
            # self.subprocess_run('create')
            create()
            backup = Backup()
            backup.files = backup.target.get_files()
            self.assertEqual(len(list(backup.files)), 4)

            # clean up database
            self.db.drop_all()
            self.db.create_all()

            # assert database is empty
            posts = Post.query.count()
            authors = User.query.count()
            controls = SomeControl.query.count()
            comments = Comments.query.count()
            self.assertEqual(posts, 0)
            self.assertEqual(authors, 0)
            self.assertEqual(controls, 0)
            self.assertEqual(comments, 0)

            # restore backup
            backup.files = backup.target.get_files()
            date_id = backup.get_timestamps()
            restore(date_id[0])

            # assert data was restored
            posts = Post.query.count()
            authors = User.query.count()
            controls = SomeControl.query.count()
            comments = Comments.query.count()
            self.assertEqual(posts, 2)
            self.assertEqual(authors, 1)
            self.assertEqual(controls, 1)
            self.assertEqual(comments, 0)

            # assert data is accurate
            posts = Post.query.all()
            for num in range(1):
                self.assertEqual(posts[num].author.email, 'me@example.etc')
                self.assertEqual(posts[num].title, u'Post {}'.format(num + 1))
                self.assertEqual(posts[num].content, u'Lorem ipsum...')

            # remove backup
            remove(date_id[0], True)

            # assert there is no backup left
            backup = Backup()
            backup.files = backup.target.get_files()
            self.assertEqual(len(tuple(backup.files)), 0)

    @patch.object(LocalTools, 'normalize_path')
    def test_autoclean(self, mock_path):
        mock_path.return_value = self.dir + os.sep

        with app.app_context():

            # create fake backup dir
            backup = Backup()
            date_ids = [
                '20110824045557',
                '20100106120931',
                '20090728192328',
                '20070611074712',
                '20130729044443',
                '20070611090332',
                '20090927181422',
                '20060505063150',
                '20090608052756',
                '20050413201344',
                '20111015194547',
                '20090711221957',
                '20140425202739',
                '20130808133229',
                '20120111210958',
                '20120419224811',
                '20060519170013',
                '20090111042034',
                '20100112115416'
            ]
            class_names = ['Post', 'User', 'SomeControl', 'Comments']
            for date_id in date_ids:
                for class_name in class_names:
                    name = backup.get_name(class_name, date_id)
                    backup.target.create_file(name, ''.encode())

            # assert files were created
            history()
            backup = Backup()
            backup.files = backup.target.get_files()
            expected_count = len(class_names) * len(date_ids)
            self.assertEqual(len(list(backup.files)), expected_count)

            # run auto clean
            autoclean(True)

            # assert some files were deleted
            backup = Backup()
            backup.files = backup.target.get_files()
            white_list = [
                '20140425202739',
                '20130808133229',
                '20120419224811',
                '20111015194547',
                '20100112115416',
                '20090927181422',
                '20070611090332',
                '20060519170013',
                '20050413201344'
            ]
            expected_count = len(class_names) * len(white_list)
            self.assertEqual(len(list(backup.files)), expected_count)

            # assert only white listed files exists,
            # and only black listed were deleted
            backup = Backup()
            backup.files = tuple(backup.target.get_files())
            self.assertEqual(sorted(white_list), sorted(backup.get_timestamps()))

            # clean up to avoid messing up other tests
            backup = Backup()
            backup.files = backup.target.get_files()
            for name in backup.files:
                backup.target.delete_file(name)
            backup = Backup()
            backup.files = backup.target.get_files()
            self.assertEqual(len(list(backup.files)), 0)
