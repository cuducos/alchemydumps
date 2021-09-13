import os
from functools import partial

import click
from flask.cli import with_appcontext
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from flask_alchemydumps.autoclean import BackupAutoClean
from flask_alchemydumps.backup import Backup
from flask_alchemydumps.confirm import Confirm
from flask_alchemydumps.database import AlchemyDumpsDatabase


success = partial(click.secho, fg="green")
error = partial(click.secho, fg="red")


@click.group()
def alchemydumps():
    """Flask-AlchemyDumps CLI"""
    pass


@alchemydumps.command()
@with_appcontext
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
            success(f"==> {rows} rows from {class_name} saved as {full_path}")
        else:
            error(f"==> Error creating {name} at {backup.target.path}")
    backup.close_ftp()


@alchemydumps.command()
@with_appcontext
def history():
    """List existing backups"""

    backup = Backup()
    backup.files = tuple(backup.target.get_files())

    # if no files
    if not backup.files:
        click.echo(f"==> No backups found at {backup.target.path}.")
        return None

    # create output
    timestamps = backup.get_timestamps()
    groups = [{"id": i, "files": backup.by_timestamp(i)} for i in timestamps]
    for output in groups:
        if output["files"]:
            date_formated = backup.target.parse_timestamp(output["id"])
            click.echo(f"\n==> ID: {output['id']} (from {date_formated})")
            for file_name in output["files"]:
                click.echo(f"    {backup.target.path}{file_name}")
    click.echo("")
    backup.close_ftp()


@alchemydumps.command()
@click.option(
    "-d",
    "--date",
    "date_id",
    help="The date part of a file from the AlchemyDumps folder",
)
@with_appcontext
def restore(date_id):
    """Restore a backup based on the date part of the backup files"""

    alchemy = AlchemyDumpsDatabase()
    backup = Backup()

    # loop through mapped classes
    for mapped_class in alchemy.get_mapped_classes():
        class_name = mapped_class.__name__
        name = backup.get_name(class_name, date_id)
        path = backup.target.path / name

        if path.exists():

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
            status = "partially" if len(fails) else "totally"
            success(f"==> {name} {status} restored.")
            for f in fails:
                error(f"    Restore of {f} failed.")
        else:
            os.system("ls alchemydumps-backups")
            msg = (
                f"==> No file found for {class_name} "
                f"({backup.target.path}{name} does not exist)."
            )
            error(msg)


@alchemydumps.command()
@click.option(
    "-d",
    "--date",
    "date_id",
    help="The date part of a file from the AlchemyDumps folder",
)
@click.option(
    "-y",
    "--assume-yes",
    "assume_yes",
    is_flag=True,
    help="Assume `yes` for all prompts",
)
@with_appcontext
def remove(date_id, assume_yes=False):
    """Remove a series of backup files based on the date part of the files"""

    # check if date/id is valid
    backup = Backup()
    if backup.valid(date_id):

        # List files to be deleted
        delete_list = tuple(backup.by_timestamp(date_id))
        click.echo("==> Do you want to delete the following files?")
        for name in delete_list:
            click.echo(f"    {backup.target.path}{name}")

        # delete
        confirm = Confirm(assume_yes)
        if confirm.ask():
            for name in delete_list:
                backup.target.delete_file(name)
                click.echo(f"    {name} deleted.")
    backup.close_ftp()


@alchemydumps.command()
@click.option(
    "-y",
    "--assume-yes",
    "assume_yes",
    is_flag=True,
    help="Assume `yes` for all prompts",
)
@with_appcontext
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
        click.echo("==> No backups found.")
        return None

    # get black and white list
    cleaning = BackupAutoClean(backup.get_timestamps())
    white_list = cleaning.white_list
    black_list = cleaning.black_list
    if not black_list:
        click.echo("==> No backup to be deleted.")
        return None

    # print the list of files to be kept
    click.echo(f"\n==> {len(white_list)} backups will be kept:")
    for date_id in white_list:
        date_formated = backup.target.parse_timestamp(date_id)
        click.echo(f"\n    ID: {date_id} (from {date_formated})")
        for f in backup.by_timestamp(date_id):
            click.echo(f"    {backup.target.path}{f}")

    # print the list of files to be deleted
    delete_list = list()
    click.echo(f"\n==> {len(black_list)} backups will be deleted:")
    for date_id in black_list:
        date_formated = backup.target.parse_timestamp(date_id)
        click.echo(f"\n    ID: {date_id} (from {date_formated})")
        for f in backup.by_timestamp(date_id):
            click.echo(f"    {backup.target.path}{f}")
            delete_list.append(f)

    # delete
    confirm = Confirm(assume_yes)
    if confirm.ask():
        for name in delete_list:
            backup.target.delete_file(name)
            click.echo(f"    {name} deleted.")
    backup.close_ftp()
