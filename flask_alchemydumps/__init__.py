# coding: utf-8

# import third party modules
from flask.ext.script import Manager
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from unipath import Path

# import alchemydumps helpers
from helpers.autoclean import bw_lists
from helpers.backup import Backup
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
    alchemy = AlchemyDumpsDatabase()
    data = alchemy.get_data()
    backup = Backup()
    date_id = backup.create_id()
    for class_name in data.keys():
        name = backup.get_name(date_id, class_name)
        full_path = backup.create_file(name, data[class_name])
        rows = len(alchemy.parse_data(data[class_name]))
        if full_path:
            print '==> {} rows from {} saved as {}'.format(rows,
                                                           class_name,
                                                           full_path)
        else:
            print '==> Error creating {} at {}'.format(name, backup.path)
    backup.close_connection()


@AlchemyDumpsCommand.command
def history():
    """List existing backups"""

    # if no files
    backup = Backup()
    if not backup.files:
        print '==> No backups found at {}.'.format(backup.path)
        return None

    # create output
    file_ids = backup.get_ids()
    groups = [{'id': i, 'files': backup.filter_files(i)} for i in file_ids]
    for output in groups:
        if output['files']:
            date_formated = backup.parsed_id(output['id'])
            print '\n==> ID: {} (from {})'.format(output['id'], date_formated)
            for file_name in output['files']:
                print '    {}{}'.format(backup.path, file_name)
    print ''
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
                print '==> {} {} restored.'.format(name, status)
                for f in fails:
                    print '    Restore of {} failed.'.format(f)
            else:
                name = backup.get_name(date_id, class_name)
                msg = '==> No file found for {} ({}{} does not exist).'
                print msg.format(class_name, backup.path, name)


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
    backup = Backup()
    if backup.valid(date_id):

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
        # List files to be deleted
        delete_list = backup.filter_files(date_id)
        print '==> Do you want to delete the following files?'
        for name in delete_list:
            print '    {}{}'.format(backup.path, name)

    backup.close_connection()

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
    backup = Backup()
    if not backup.files:
        print '==> No backups found.'
        return None

    # get black and white list
    lists = bw_lists(backup.get_ids())
    if not lists['black_list']:
        print '==> No backup to be deleted.'
        return None

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