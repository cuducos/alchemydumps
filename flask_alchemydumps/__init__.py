# coding: utf-8

# Python 2 compatibility with Pyhton 3 import and print
from __future__ import absolute_import
from __future__ import print_function

# import third party modules
from flask.ext.script import Manager
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from unipath import Path

# import alchemydumps helpers
from .helpers.autoclean import bw_lists
from .helpers.backup import Backup
from .helpers.confirm import confirm
from .helpers.database import AlchemyDumpsDatabase


class _AlchemyDumpsConfig(object):

    def __init__(self, db=None, basedir=''):
        self.db = db
        self.basedir = Path(basedir).absolute()


class AlchemyDumps(object):

    def __init__(self, app=None, db=None, basedir=''):
        if app is not None and db is not None:
            self.init_app(app, db, basedir)

    @staticmethod
    def init_app(app, db, basedir=''):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['alchemydumps'] = _AlchemyDumpsConfig(db, basedir)


AlchemyDumpsCommand = Manager(usage='Backup and restore full SQL database')


@AlchemyDumpsCommand.command
def create():
    """Create a backup based on SQLAlchemy mapped classes"""

    # create backup files
    alchemy = AlchemyDumpsDatabase()
    data = alchemy.get_data()
    backup = Backup()
    date_id = backup.create_id()
    for class_name in data.keys():
        name = backup.get_name(date_id, class_name)
        full_path = backup.create_file(name, data[class_name])
        rows = len(alchemy.parse_data(data[class_name]))
        if full_path:
            print('==> {} rows from {} saved as {}'.format(rows,
                                                           class_name,
                                                           full_path))
        else:
            print('==> Error creating {} at {}'.format(name, backup.path))
    backup.close_connection()


@AlchemyDumpsCommand.command
def history():
    """List existing backups"""

    # if no files
    backup = Backup()
    if not backup.files:
        print('==> No backups found at {}.'.format(backup.path))
        return None

    # create output
    file_ids = backup.get_ids()
    groups = [{'id': i, 'files': backup.filter_files(i)} for i in file_ids]
    for output in groups:
        if output['files']:
            date_formated = backup.parsed_id(output['id'])
            print('\n==> ID: {} (from {})'.format(output['id'], date_formated))
            for file_name in output['files']:
                print('    {}{}'.format(backup.path, file_name))
    print('')
    backup.close_connection()


@AlchemyDumpsCommand.option('-d',
                            '--date',
                            dest='date_id',
                            default=False,
                            help='The date part of a file from the AlchemyDumps\
                                 folder')
def restore(date_id):
    """Restore a backup based on the date part of the backup files"""

    # check if date/id is valid
    alchemy = AlchemyDumpsDatabase()
    backup = Backup()
    if backup.valid(date_id):

        # loop through backup files
        for mapped_class in alchemy.get_mapped_classes():
            class_name = mapped_class.__name__
            name = backup.get_name(date_id, class_name)
            if name in backup.files:

                # read file contents
                contents = backup.read_file(name)
                fails = list()

                # restore to the db
                db = alchemy.db()
                for row in alchemy.parse_data(contents):
                    try:
                        db.session.merge(row)
                        db.session.commit()
                    except (IntegrityError, InvalidRequestError):
                        db.session.rollback()
                        fails.append(row)

                # print summary
                status = 'partially' if len(fails) else 'totally'
                print('==> {} {} restored.'.format(name, status))
                for f in fails:
                    print('    Restore of {} failed.'.format(f))
            else:
                name = backup.get_name(date_id, class_name)
                msg = '==> No file found for {} ({}{} does not exist).'
                print(msg.format(class_name, backup.path, name))


@AlchemyDumpsCommand.option('-d',
                            '--date',
                            dest='date_id',
                            default=False,
                            help='The date part of a file from the AlchemyDumps\
                                 folder')
@AlchemyDumpsCommand.option('-y',
                            '--assume-yes',
                            dest='assume_yes',
                            action='store_true',
                            default=False,
                            help='Assume `yes` for all prompts')
def remove(date_id, assume_yes=False):
    """Remove a series of backup files based on the date part of the files"""

    # check if date/id is valid
    backup = Backup()
    if backup.valid(date_id):

        # List files to be deleted
        delete_list = backup.filter_files(date_id)
        print('==> Do you want to delete the following files?')
        for name in delete_list:
            print('    {}{}'.format(backup.path, name))

        # delete
        if confirm(assume_yes):
            for name in delete_list:
                backup.delete_file(name)
                print('    {} deleted.'.format(name))
    backup.close_connection()


@AlchemyDumpsCommand.option('-y',
                            '--assume-yes',
                            dest='assume_yes',
                            action='store_true',
                            default=False,
                            help='Assume `yes` for all prompts')
def autoclean(assume_yes=False):
    """
    Remove a series of backup files based on the following rules:
    * Keeps all the backups from the last 7 days
    * Keeps the most recent backup from each week of the last month
    * Keeps the most recent backup from each month of the last year
    * Keeps the most recent backup from each year of the remaining years
    """

    # check if there are backups
    backup = Backup()
    if not backup.files:
        print('==> No backups found.')
        return None

    # get black and white list
    lists = bw_lists(backup.get_ids())
    if not lists['black_list']:
        print('==> No backup to be deleted.')
        return None

    # print the list of files to be kept/deleted
    black_list = list()
    for l in ['white_list', 'black_list']:
        msg = 'kept' if l == 'white_list' else 'deleted'
        print('\n==> {} backups will be {}:'.format(len(lists[l]), msg))
        for date_id in lists[l]:
            date_formated = backup.parsed_id(date_id)
            print('\n    ID: {} (from {})'.format(date_id, date_formated))
            for f in backup.filter_files(date_id):
                print('    {}{}'.format(backup.path, f))
                if l == 'black_list':
                    black_list.append(f)

    # delete
    if confirm(assume_yes):
        for name in black_list:
            backup.delete_file(name)
            print('    {} deleted.'.format(name))
    backup.close_connection()
