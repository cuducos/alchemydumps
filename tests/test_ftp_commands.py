# coding: utf-8

import os
from .app_ftp import app, db, Post, User, SomeControl, Comments
from flask.ext.alchemydumps.helpers.backup import Backup
from unittest import TestCase


class TestFTPCommands(TestCase):

    def setUp(self):

        # create database
        self.db = db
        self.db.drop_all()
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

        db.session.commit()

    def tearDown(self):

        # clean up database
        self.db.drop_all()

        # clean up files and directories
        basedir = app.extensions['alchemydumps'].basedir
        directory = basedir.child('alchemydumps')
        sqlite = basedir.child('test.db')
        directory.rmtree()
        sqlite.remove()

    def test_create_restore_remove(self):

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
            os.system('python tests/app_ftp.py alchemydumps create')
            backup = Backup()
            self.assertEqual(len(backup.files), 4)

            # clean up and recreate database
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
            date_id = backup.get_ids()
            command = 'python tests/app_ftp.py alchemydumps restore -d {}'
            os.system(command.format(date_id[0]))

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
            posts= Post.query.all()
            for num in range(1):
                self.assertEqual(posts[num].author.email, 'me@example.etc')
                self.assertEqual(posts[num].title, u'Post {}'.format(num + 1))
                self.assertEqual(posts[num].content, u'Lorem ipsum...')

            # remove backup
            command = 'python tests/app_ftp.py alchemydumps remove -d {} -y'
            os.system(command.format(date_id[0]))

            # assert there is no backup left
            backup = Backup()
            self.assertEqual(len(backup.files), 0)

    def test_autoclean(self):

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
                    name = backup.get_name(date_id, class_name)
                    backup.create_file(name, '')

            # assert files were created
            backup = Backup()
            expected_count = len(class_names) * len(date_ids)
            self.assertEqual(len(backup.files), expected_count)

            # run auto clean
            os.system('python tests/app_ftp.py alchemydumps autoclean -y')

            # assert some files were deleted
            backup = Backup()
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
            self.assertEqual(len(backup.files), expected_count)

            # assert only white listed files exists,
            # and only black listed were deleted
            self.assertEqual(sorted(white_list), sorted(backup.get_ids()))

            # clean up to avoid messing up other tests
            for name in backup.files:
                backup.delete_file(name)
            backup = Backup()
            self.assertEqual(len(backup.files), 0)
