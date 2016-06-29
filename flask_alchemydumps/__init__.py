# coding: utf-8

# Python 2 compatibility with Pyhton 3 import and print
from __future__ import absolute_import, print_function

import os

from flask_script import Manager
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from unipath import Path

from flask_alchemydumps.helpers.autoclean import BackupAutoClean
from flask_alchemydumps.helpers.backup import Backup
from flask_alchemydumps.helpers.confirm import Confirm
from flask_alchemydumps.helpers.database import AlchemyDumpsDatabase


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
    for class_name in data.keys():
        name = backup.get_name(class_name)
        full_path = backup.target.create_file(name, data[class_name])
        rows = len(alchemy.parse_data(data[class_name]))
        if full_path:
            print('==> {} rows from {} saved as {}'.format(rows,
                                                           class_name,
                                                           full_path))
        else:
            print('==> Error creating {} at {}'.format(name, backup.target.path))
    backup.close_ftp()


@AlchemyDumpsCommand.command
def history():
    """List existing backups"""

    backup = Backup()
    backup.files = tuple(backup.target.get_files())

    # if no files
    if not backup.files:
        print('==> No backups found at {}.'.format(backup.target.path))
        return None

    # create output
    timestamps = backup.get_timestamps()
    groups = [{'id': i, 'files': backup.filter_files(i)} for i in timestamps]
    for output in groups:
        if output['files']:
            date_formated = backup.parse_timestamp(output['id'])
            print('\n==> ID: {} (from {})'.format(output['id'], date_formated))
            for file_name in output['files']:
                print('    {}{}'.format(backup.target.path, file_name))
    print('')
    backup.close_ftp()


@AlchemyDumpsCommand.option('-d',
                            '--date',
                            dest='date_id',
                            default=False,
                            help='The date part of a file from the AlchemyDumps\
                                 folder')
def restore(date_id):
    """Restore a backup based on the date part of the backup files"""

    alchemy = AlchemyDumpsDatabase()
    backup = Backup()

    # loop through mapped classes
    for mapped_class in alchemy.get_mapped_classes():
        class_name = mapped_class.__name__
        name = backup.get_name(class_name, date_id)
        if os.path.exists(os.path.join(backup.target.path, name)):

            # read file contents
            contents = backup.target.read_file(name)
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
            os.system('ls alchemydumps-backups')
            msg = '==> No file found for {} ({}{} does not exist).'
            print(msg.format(class_name, backup.target.path, name))


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
        delete_list = tuple(backup.by_timestamp(date_id))
        print('==> Do you want to delete the following files?')
        for name in delete_list:
            print('    {}{}'.format(backup.target.path, name))

        # delete
        confirm = Confirm(assume_yes)
        if confirm.ask():
            for name in delete_list:
                backup.target.delete_file(name)
                print('    {} deleted.'.format(name))
    backup.close_ftp()


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
    backup.files = tuple(backup.target.get_files())
    if not backup.files:
        print('==> No backups found.')
        return None

    # get black and white list
    cleaning = BackupAutoClean(backup.get_timestamps())
    white_list = cleaning.white_list
    black_list = cleaning.black_list
    if not black_list:
        print('==> No backup to be deleted.')
        return None

    # print the list of files to be kept
    print('\n==> {} backups will be kept:'.format(len(white_list)))
    for date_id in white_list:
        date_formated = backup.target.parse_timestamp(date_id)
        print('\n    ID: {} (from {})'.format(date_id, date_formated))
        for f in backup.by_timestamp(date_id):
            print('    {}{}'.format(backup.target.path, f))

    # print the list of files to be deleted
    delete_list = list()
    print('\n==> {} backups will be deleted:'.format(len(black_list)))
    for date_id in black_list:
        date_formated = backup.target.parse_timestamp(date_id)
        print('\n    ID: {} (from {})'.format(date_id, date_formated))
        for f in backup.by_timestamp(date_id):
            print('    {}{}'.format(backup.target.path, f))
            delete_list.append(f)

    # delete
    confirm = Confirm(assume_yes)
    if confirm.ask():
        for name in delete_list:
            backup.target.delete_file(name)
            print('    {} deleted.'.format(name))
    backup.close_ftp()
