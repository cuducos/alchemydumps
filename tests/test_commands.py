# coding: utf-8

import os
from .app import app, db, Post, User
from flask.ext.alchemydumps.helpers.identification import get_id
from unittest import TestCase


class TestCommands(TestCase):

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
        db.session.commit()

        # directory of backups
        self.dir = app.extensions['alchemydumps'].basedir.child('alchemydumps')

    def tearDown(self):
        self.dir.rmtree()
        self.db.drop_all()
        db_file = app.extensions['alchemydumps'].basedir.child('test.db')
        db_file.remove()

    def test_create_restore_remove(self):

        # assert data was inserted
        posts = Post.query.count()
        authors = User.query.count()
        self.assertEqual(posts, 2)
        self.assertEqual(authors, 1)

        # create and assert backup files
        os.system('python tests/app.py alchemydumps create')

        # clean up and recreate database
        self.db.drop_all()
        self.db.create_all()

        # assert database is empty
        posts = Post.query.count()
        authors = User.query.count()
        self.assertEqual(posts, 0)
        self.assertEqual(authors, 0)

        # restore backup
        dump = None
        for file_path in self.dir.listdir():
            dump = get_id(file_path)
        command = 'python tests/app.py alchemydumps restore -d {}'
        os.system(command.format(dump))

        # assert data was restored
        posts = Post.query.count()
        authors = User.query.count()
        self.assertEqual(posts, 2)
        self.assertEqual(authors, 1)

        # assert data is accurate
        post = Post.query.first()
        self.assertEqual(post.author.email, 'me@example.etc')

        # remove backup
        command = 'python tests/app.py alchemydumps remove -d {} -y True'
        os.system(command.format(dump))

        # assert there is no backup left
        self.assertEqual(len(self.dir.listdir()), 0)

        # clean up to avoid messing up other tests
        self.dir.rmtree()

    def test_autoclean(self):

        # create fake backup dir
        self.dir.mkdir()
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
        tables = ['Post', 'User']
        for dump in date_ids:
            for table in tables:
                path = self.dir.child('test-bkp-{}-{}.gz'.format(dump, table))
                open(path, 'a').close()

        # assert files were created
        self.assertEqual(len(self.dir.listdir()), len(tables) * len(date_ids))

        # run auto clean
        os.system('python tests/app.py alchemydumps autoclean -y True')

        # assert some files were deleted
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
        self.assertEqual(len(self.dir.listdir()), len(tables) * len(white_list))

        # assert only white listed files exists,
        # and only black listed were deleted
        file_ids = list()
        for file_path in self.dir.listdir():
            dump = get_id(file_path)
            if dump not in file_ids:
                file_ids.append(dump)
        self.assertEqual(sorted(white_list), sorted(file_ids))

        # clean up to avoid messing up other tests
        self.dir.rmtree()