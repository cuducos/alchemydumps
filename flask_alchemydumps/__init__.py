# coding: utf-8

# import native modules
import gzip
from datetime import datetime
from time import gmtime, strftime

# import installed modules
from flask import current_app
from flask.ext.script import Manager
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from unipath import Path

# import alchemydumps helpers
from helpers.autoclean import bw_lists
from helpers.database import AlchemyDumpsDatabase


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
    date_id = str(strftime("%Y%m%d%H%M%S", gmtime()))
    bkp_dir = get_bkp_dir()
    for k in data.keys():
        file_name = 'db-bkp-{}-{}.gz'.format(date_id, k)
        file_path = bkp_dir.child(file_name)
        file_handler = gzip.open(file_path, 'wb')
        file_handler.write(data[k])
        file_handler.close()
        num_rows = len(loads(data[k], db.metadata, db.session))
        print '==> {} rows from {} saved as {}'.format(num_rows,
                                                       k,
                                                       file_path.absolute())
    alchemy = AlchemyDumpsDatabase()
    data = alchemy.get_data()


@AlchemyDumpsCommand.command
def history():
    """List existing backups"""

    # check the dir
    files = get_list()
    bkp_dir = get_bkp_dir()

    # if no files
    if not len(files):
        return '==> No backup files found at {}.'.format(bkp_dir.absolute())

    # create output
    file_ids = get_ids(files)
    output = [{'id': i, 'files': get_list(i, files)} for i in file_ids]
    for o in output:
        if len(o['files']):
            date_parsed = datetime.strptime(o['id'], '%Y%m%d%H%M%S')
            date_format = date_parsed.strftime('%b %d, %Y at %H:%M:%S')
            print '\n==> ID: {} (from {})'.format(o['id'], date_format)
            for f in o['files']:
                print '    {}'.format(f)
    print ''


@AlchemyDumpsCommand.option('-d',
                            '--date',
                            dest='date_id',
                            default=False,
                            help='The date part of a file from the AlchemyDumps\
                                 folder')
def restore(date_id):
    """Restore a backup based on the date part of the backup files"""

    # check if date/id is valid
    files = get_list()
    if not date_id or date_id not in get_ids(files):
        print '==> Invalid id. Use "history" to list existing downloads'
        return None
    alchemy = AlchemyDumpsDatabase()
        for mapped_class in alchemy.get_mapped_classes():

        class_name = m.__name__
        bkp_dir = get_bkp_dir()
        file_path = bkp_dir.child('db-bkp-{}-{}.gz'.format(date_id, class_name))
        if file_path.exists():
            with gzip.open(file_path, 'rb') as file_handler:
                file_content = file_handler.read()
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
                print '==> {} {} restored.'.format(file_path, status)
                for f in fails:
                    print '    {} failed to merge and was skipped.'.format(f)
        else:
            msg = '==> No file found for {} ({} does not exist).'
            print msg.format(class_name, file_path.absolute())


@AlchemyDumpsCommand.option('-d',
                            '--date',
                            dest='date_id',
                            default=False,
                            help='The date part of a file from the AlchemyDumps\
                                 folder')
@AlchemyDumpsCommand.option('-y',
                            '--yes-for-all',
                            dest='yes_for_all',
                            default=False,
                            help='Assume `yes` for all prompts')
def remove(date_id, yes_for_all=False):
    """Remove a series of backup files based on the date part of the files"""

    # check if date/id is valid
    files = get_list(date_id)
    if not date_id or date_id not in get_ids(files):
        print '==> Invalid id. Use "history" to list existing downloads'
        return None

    # List files to be deleted
    delete_list = get_list(date_id, files)
    print '==> Do you want to delete the following files?'
    for d in delete_list:
        print '    {}'.format(d.absolute())

    # confirm
    confirmed = False
    if yes_for_all:
        confirmed = True
    else:
        msg = '==> Press "Y" to confirm, or anything else to abort.'
        confirmation = raw_input(msg)
        if confirmation.lower() == 'y':
            confirmed = True

    # delete
    if confirmed:
        for d in delete_list:
            print '    {} deleted.'.format(d.absolute())
            d.remove()


@AlchemyDumpsCommand.option('-y',
                            '--yes-for-all',
                            dest='yes_for_all',
                            default=False,
                            help='Assume `yes` for all prompts')
def autoclean(yes_for_all=False):
    """
    Remove a series of backup files based on the following rules:
    * Keeps all the backups from the last 7 days
    * Keeps the most recent backup from each week of the last month
    * Keeps the most recent backup from each month of the last year
    * Keeps the most recent backup from each year of the remaining years
    """

    # check if there are backups
    files = get_list()
    date_ids = get_ids(files)
    if not len(files):
        print '==> No backups found.'
        return

    # get black and white list
    lists = bw_lists(date_ids)
    if not len(lists['black_list']):
        print '==> No backup to be deleted.'
        return

    # print the list of files to be kept/deleted
    black_list = list()
    for l in ['white_list', 'black_list']:
        msg = 'kept' if l == 'white_list' else 'deleted'
        print '\n==> {} backups will be {}:'.format(len(lists[l]), msg)
        for date_id in lists[l]:
            date_parsed = datetime.strptime(date_id, '%Y%m%d%H%M%S')
            date_format = date_parsed.strftime('%b %d, %Y at %H:%M:%S')
            print '\n    ID: {} (from {})'.format(date_id, date_format)
            for f in get_list(date_id, files):
                print '    {}'.format(f)
                if l == 'black_list':
                    black_list.append(f)

    # confirm
    confirmed = False
    if yes_for_all:
        confirmed = True
    else:
        msg = '\n==> Press "Y" to confirm, or anything else to abort.'
        confirmation = raw_input(msg)
        if confirmation.lower() == 'y':
            confirmed = True

    # delete
    if confirmed:
        for file_path in black_list:
            print '    {} deleted.'.format(file_path.absolute())
            file_path.remove()