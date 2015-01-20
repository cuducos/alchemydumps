# coding: utf-8

# import native modules
import gzip
from datetime import datetime
from time import gmtime, strftime

# import installed modules
from flask import current_app
from flask.ext.script import Manager
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.serializer import dumps, loads
from unipath import Path

# import alchemydumps helpers
from helpers.autoclean import bw_lists
from helpers.identification import get_bkp_dir, get_ids, get_list
from helpers.sqlalchemy import get_sa_mapped_classes


class _AlchemyDumpsConfig(object):

    def __init__(self, db=None, basedir=''):
        self.db = db
        self.basedir = Path(basedir).absolute()


class AlchemyDumps(object):

    def __init__(self, app=None, db=None, basedir=''):
        if app is not None and db is not None:
            self.init_app(app, db, basedir)

    def init_app(self, app, db, basedir=''):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['alchemydumps'] = _AlchemyDumpsConfig(db, basedir)


AlchemyDumpsCommand = Manager(usage='Backup and restore full SQL database')


@AlchemyDumpsCommand.command
def create():
    """Create a backup based on SQLAlchemy mapped classes"""

    # query for data
    db = current_app.extensions['alchemydumps'].db
    data = dict()
    for m in get_sa_mapped_classes(db):
        query = db.session.query(m)
        data[m.__name__] = dumps(query.all())

    # create backup files
    date_id = str(strftime("%Y%m%d%H%M%S", gmtime()))
    bkp_dir = get_bkp_dir()
    for k in data.keys():
        filename = 'db-bkp-{}-{}.gz'.format(date_id, k)
        filepath = bkp_dir.child(filename)
        filehandler = gzip.open(filepath, 'wb')
        filehandler.write(data[k])
        filehandler.close()
        num_rows = len(loads(data[k], db.metadata, db.session))
        print '==> {} rows from {} saved as {}'.format(num_rows,
                                                       k,
                                                       filepath.absolute())


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
            date_transf = datetime.strptime(o['id'], '%Y%m%d%H%M%S')
            date_format = date_transf.strftime('%b %d, %Y at %H:%M:%S')
            print '\n==> ID: {} (from {})'.format(o['id'], date_format)
            for f in o['files']:
                print '    {}'.format(f)
    print ''


@AlchemyDumpsCommand.option('-d',
                            '--date',
                            dest='date_id',
                            default=False, help='The date part of a file from the AlchemyDumps folder')
def restore(date_id):
    """Restore a backup based on the date part of the backup files"""

    # check if date/id is valid
    files = get_list()
    if not date_id or date_id not in get_ids(files):
        print '==> Not a valid date id. Use the "history" command to list existing downloads'
        return

    # loop through backup files
    db = current_app.extensions['alchemydumps'].db
    for m in get_sa_mapped_classes(db):
        class_name = m.__name__
        bkp_dir = get_bkp_dir()
        filepath = bkp_dir.child('db-bkp-{}-{}.gz'.format(date_id, class_name))
        if filepath.exists():
            with gzip.open(filepath, 'rb') as file_handler:
                file_content = file_handler.read()
                fails = list()
                for row in loads(file_content, db.metadata, db.session):
                    try:
                        db.session.merge(row)
                        db.session.commit()
                    except (IntegrityError, InvalidRequestError):
                        db.session.rollback()
                        fails.append(row)

                # print summary
                status = 'partially' if len(fails) else 'totally'
                print '==> {} {} restored.'.format(filepath, status)
                for f in fails:
                    print '    {} failed to merge and was skipped.'.format(f)
        else:
            print '==> No file found for {} ({} does not exist).'.format(class_name,
                                                                         filepath.absolute())


@AlchemyDumpsCommand.option('-d',
                            '--date',
                            dest='date_id',
                            default=False, help='The date part of a file from the AlchemyDumps folder')
def remove(date_id):
    """Remove a series of backup files based on the date part of the files"""

    # check if date/id is valid
    files = get_list(date_id)
    if not date_id or date_id not in get_ids(files):
        print '==> Not a valid date id. Use the "history" command to list existing downloads'
        return

    # List files to be deleted
    delete_list = get_list(date_id, files)
    print '==> Do you want to delete the following files?'
    for d in delete_list:
        print '    {}'.format(d.absolute())

    # confirm
    confirmation = raw_input('==> Press "Y" to confirm, or anything else to abort.')
    if confirmation.lower() == 'y':

        # delete
        for d in delete_list:
            print '    {} deleted.'.format(d.absolute())
            d.remove()


@AlchemyDumpsCommand.command
def autoclean():
    """
    Remove a series of backup files based on the following rules:
    * It keeps all the backups from the last 7 days
    * It keeps one (the most recent one) backup from each week of the last month
    * It keeps one (the most recent one) backup from each month of the last year
    * It keeps one (the most recent one) backup from each year of the remaining years
    """

    # check if there are backups
    files = get_list()
    date_ids = get_ids(files)
    if not len(files):
        print '==> No backups found.'
        return

    # get black and white list
    lists = bw_lists(date_ids)
    if not len(lists['blacklist']):
        print '==> No backup to be deleted.'
        return

    # print the list of files to be kept/deleted
    blacklist = list()
    for l in ['whitelist', 'blacklist']:
        msg = 'kept' if l == 'whitelist' else 'deleted'
        print '\n==> {} backups will be {}:'.format(len(lists[l]), msg)
        for date_id in lists[l]:
            date_transf = datetime.strptime(date_id, '%Y%m%d%H%M%S')
            date_format = date_transf.strftime('%b %d, %Y at %H:%M:%S')
            print '\n    ID: {} (from {})'.format(date_id, date_format)
            for f in get_list(date_id, files):
                print '    {}'.format(f)
                if l == 'blacklist':
                    blacklist.append(f)

    # confirm
    confirmation = raw_input('\n==> Press "Y" to confirm, or anything else to abort.')
    if confirmation.lower() == 'y':

        # delete
        for filepath in blacklist:
            print '    {} deleted.'.format(filepath.absolute())
            filepath.remove()
