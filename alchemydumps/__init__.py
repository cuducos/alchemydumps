# coding: utf-8

import gzip
from datetime import datetime
from flask import current_app
from flask.ext.script import Manager
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.serializer import dumps, loads
from time import gmtime, strftime
from unipath import Path


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
    files = get_list()
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


def get_sa_mapped_classes(sqlalachemy_db=False):
    """
    :param sqlalachemy_db: (optional) SQLAlchemy database (if not passed, it is loaded from AlchemyDumps() instance)
    :return: list of SQLALchemy mapped classes
    """
    if not sqlalachemy_db:
        sqlalachemy_db = current_app.extensions['alchemydumps'].db
    do_not_backup = []
    sa_models = list()
    for m in sqlalachemy_db.Model.__subclasses__():
        if m not in do_not_backup:
            sa_models.append(m)
    return sa_models


def get_bkp_dir():
    """
    :return: unipath object of the dir where backup files are saved
    """
    bkp_dir = current_app.extensions['alchemydumps'].basedir.child('alchemydumps')
    if not bkp_dir.exists():
        bkp_dir.mkdir()
    return bkp_dir


def get_id(filepath):
    """
    :param filepath: unipath object of a file generated by AlchemyDumps
    :return: the backup numeric id
    """
    filename = filepath.stem
    parts = filename.split('-')
    try:
        return parts[2]
    except IndexError:
        return False


def get_list(date_id=False, files=False):
    """
    :param date_id: (optional) Backup file numeric id (if False, list everything)
    :param files: (optional) If you have already called get_list(), pass the file list to improve performance
    :return: The list of backup files from that id
    """
    if files:
        if date_id:
            output = [f for f in files if date_id in f.stem]
        else:
            output = files
    else:
        bkp_dir = get_bkp_dir()
        pattern = '*{}*'.format(date_id) if date_id else None
        output = [f.absolute() for f in bkp_dir.listdir(pattern)]
    return output


def get_ids(files=False):
    """
    :param files: (optional) If you have already called get_list(), pass the file list to improve performance
    :return: List all valid IDs from the backup folder
    """
    if not files:
        files = get_list()
    file_ids = list()
    for f in files:
        file_id = get_id(f)
        if file_id and not file_ids.count(file_id):
            file_ids.append(file_id)
    return file_ids