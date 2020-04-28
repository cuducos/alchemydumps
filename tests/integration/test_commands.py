from os import environ
from tempfile import TemporaryDirectory
from unittest import TestCase

from click.testing import CliRunner
from flask.cli import ScriptInfo

from flask_alchemydumps.cli import create, restore, remove, autoclean
from flask_alchemydumps.backup import Backup

from .app import Comments, Post, SomeControl, User, db


class TestCommands(TestCase):
    def setUp(self):

        # create database
        self.db = db
        self.db.create_all()

        # feed user table
        db.session.add(User(email="me@example.etc"))
        db.session.commit()

        # feed post table
        db.session.add(Post(title="Post 1", content="Lorem ipsum...", author_id=1))
        db.session.add(Post(title="Post 2", content="Ipsum lorem...", author_id=1))

        # feed some control table
        db.session.add(SomeControl(uuid="1"))

        # commit
        db.session.commit()

        # temp directory & envvar
        self.tmp = TemporaryDirectory()
        self.backup_alchemydumps_dir = environ.get("ALCHEMYDUMPS_DIR")
        environ["ALCHEMYDUMPS_DIR"] = self.tmp.name

        # main object
        self.backup = Backup()

    def tearDown(self):
        self.db.drop_all()
        self.tmp.cleanup()
        del environ["ALCHEMYDUMPS_DIR"]
        if self.backup_alchemydumps_dir:
            environ["ALCHEMYDUMPS_DIR"] = self.backup_alchemydumps_dir

    @staticmethod
    def runner(command, args=""):
        obj = ScriptInfo(app_import_path="tests/integration/app.py")
        return CliRunner().invoke(command, args=args, obj=obj)

    def test_create_restore_remove(self):

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
        self.runner(create)
        self.backup.files = tuple(self.backup.target.get_files())
        self.assertEqual(len(self.backup.files), 4)

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
        self.backup.files = tuple(self.backup.target.get_files())
        date_id, *_ = self.backup.get_timestamps()
        self.runner(restore, f"-d {date_id}")

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
        post, *_ = Post.query.all()
        self.assertEqual(post.author.email, "me@example.etc")
        self.assertEqual(post.title, "Post 1")
        self.assertEqual(post.content, "Lorem ipsum...")

        # remove backup
        self.runner(remove, f"-d {date_id} -y")

        # assert there is no backup left
        self.backup.files = tuple(self.backup.target.get_files())
        self.assertEqual(len(self.backup.files), 0)

    def test_autoclean(self):

        # create fake backup dir
        date_ids = (
            "20110824045557",
            "20100106120931",
            "20090728192328",
            "20070611074712",
            "20130729044443",
            "20070611090332",
            "20090927181422",
            "20060505063150",
            "20090608052756",
            "20050413201344",
            "20111015194547",
            "20090711221957",
            "20140425202739",
            "20130808133229",
            "20120111210958",
            "20120419224811",
            "20060519170013",
            "20090111042034",
            "20100112115416",
        )
        classes = ("Post", "User", "SomeControl", "Comments")
        for date_id in date_ids:
            for class_name in classes:
                name = self.backup.get_name(class_name, date_id)
                self.backup.target.create_file(name, b"")

        # assert files were created
        self.backup.files = tuple(self.backup.target.get_files())
        self.assertEqual(len(self.backup.files), len(classes) * len(date_ids))

        # run auto clean
        self.runner(autoclean, "-y")

        # assert some files were deleted
        self.backup.files = tuple(self.backup.target.get_files())
        white_list = (
            "20140425202739",
            "20130808133229",
            "20120419224811",
            "20111015194547",
            "20100112115416",
            "20090927181422",
            "20070611090332",
            "20060519170013",
            "20050413201344",
        )
        self.assertEqual(len(self.backup.files), len(classes) * len(white_list))
        self.assertEqual(sorted(white_list), sorted(self.backup.get_timestamps()))
