# AlchemyDumps [![Latest release](https://img.shields.io/pypi/v/Flask-AlchemyDumps.svg?style=flat)](https://pypi.python.org/pypi/Flask-AlchemyDumps)

[![Development Status: Alpha](https://img.shields.io/pypi/status/Flask-AlchemyDumps.svg?style=flat)](https://pypi.python.org/pypi/Flask-AlchemyDumps)
[![Python Version](https://img.shields.io/pypi/pyversions/Flask-AlchemyDumps.svg)](https://pypi.python.org/pypi/Flask-AlchemyDumps)
[![GitHub Actions](https://github.com/cuducos/alchemydumps/actions/workflows/tests.yaml/badge.svg)](https://github.com/cuducos/alchemydumps/actions/workflows/tests.yaml)
[![Coverage Status](https://coveralls.io/repos/github/cuducos/alchemydumps/badge.svg?branch=master)](https://coveralls.io/github/cuducos/alchemydumps?branch=master)


Do you use [Flask](http://flask.pocoo.org>) with [SQLAlchemy](http://www.sqlalchemy.org/)? Wow, what a coincidence!

This package lets you backup and restore all your data using [SQLAlchemy dumps() method](http://docs.sqlalchemy.org/en/latest/core/serializer.html).

It is an easy way (one single command, I mean it) to save **all** the data stored in your database.

You can save it locally or in a remote server via FTP.

> **WARNING** [**@baumatron**](https://github.com/baumatron)'ve [found an important bug](https://github.com/cuducos/alchemydumps/issues/13): at this time this package won't backup [non-standard mappings](http://docs.sqlalchemy.org/en/latest/orm/nonstandard_mappings.html), such as [many-to-many association tables](http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#many-to-many). This is still an open issue and I have no expectation to fix is in the following weeks — **_pull requests_ are more tham welcomed**.

## Install

First install the package: `pip install Flask-AlchemyDumps`

Then pass your Flask application and SQLALchemy database to it.

For example:

* The ***second line*** imports the object from the package.
* The ***last line*** instantiates `AlchemyDumps` for your app and database.

```python
from flask import Flask
from flask_alchemydumps import AlchemyDumps
from flask_sqlalchemy import SQLAlchemy

# init Flask
app = Flask(__name__)

# init SQLAlchemy and Flask-Script
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

# init Alchemy Dumps
alchemydumps = AlchemyDumps(app, db)
```

### Remote backup (via FTP)

If you want to save your backup in a remote server via FTP, just make sure to set these environment variables replacing the placeholder information with the proper credentials:

```console
export ALCHEMYDUMPS_FTP_SERVER=ftp.server.com
export ALCHEMYDUMPS_FTP_USER=johndoe
export ALCHEMYDUMPS_FTP_PASSWORD=secret
export ALCHEMYDUMPS_FTP_PATH=/absolute/path/
```

If you want, there is a `.env.sample` inside the `/tests` folder. Just copy it to your application root folder, rename it to `.env`, and insert your credentials.

### Using application factory

It is possible to use this package with application factories:

```python
alchemydumps = AlchemyDumps()

def create_app(settings):
    …
    alchemydumps.init_app(app, db)
    …
```

### .gitignore

You might want to add `alchemydumps/` to your `.gitignore`. It is the folder where **AlchemyDumps** save the backup files.

## Examples

Considering you have these *models* — that is to say, these [SQLAlchemy mapped classes](http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html):

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(140), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.UnicodeText)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

Just in case: this is a simple example, but you can use *abstract* mapped classes as well.

### You can backup all your data

```console
python manage.py alchemydumps create
```

Output:

```
==> 3 rows from User saved as /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
==> 42 rows from Post saved as /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz
```

### You can list the backups you have already created

```console
python manage.py alchemydumps history
```

Output:
	
```
==> ID: 20141114203949 (from Nov 15, 2014 at 17:21:07)
    /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
    /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz

==> ID: 20141115140629 (from Nov 15, 2014 at 14:06:29)
    /vagrant/alchemydumps/db-bkp-20141115140629-User.gz
    /vagrant/alchemydumps/db-bkp-20141115140629-Post.gz
```

### You can restore a backup

```console
python manage.py alchemydumps restore -d 20141115172107
```

Output:

```
==> db-bkp-20141115172107-User.gz totally restored.
==> db-bkp-20141115172107-Post.gz totally restored.
```

### You can delete an existing backup

```console
python manage.py alchemydumps remove -d 20141115172107
```

Output:

```
==> Do you want to delete the following files?
    /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
    /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz
==> Press "Y" to confirm, or anything else to abort: y
    db-bkp-20141115172107-User.gz deleted.
    db-bkp-20141115172107-Post.gz deleted.
```

### And you can use the auto-clean command

The `autoclean` command follows these rules to delete backups:

* It keeps **all** the backups from the last 7 days.
* It keeps **the most recent** backup **from each week of the last month**.
* It keeps **the most recent** backup **from each month of the last year**.
* It keeps **the most recent** backup **from each remaining year**.

```console
python manage.py alchemydumps autoclean
```

Output:

```
==> 8 backups will be kept:

    ID: 20130703225903 (from Jul 03, 2013 at 22:59:03)
    /vagrant/alchemydumps/db-bkp-20130703225903-User.gz
    /vagrant/alchemydumps/db-bkp-20130703225903-Post.gz

    ID: 20120405013054 (from Apr 05, 2012 at 01:30:54)
    /vagrant/alchemydumps/db-bkp-20120405013054-User.gz
    /vagrant/alchemydumps/db-bkp-20120405013054-Post.gz

    ID: 20101123054342 (from Nov 23, 2010 at 05:43:42)
    /vagrant/alchemydumps/db-bkp-20101123054342-User.gz
    /vagrant/alchemydumps/db-bkp-20101123054342-Post.gz

    ID: 20090708100815 (from Jul 08, 2009 at 10:08:15)
    /vagrant/alchemydumps/db-bkp-20090708100815-User.gz
    /vagrant/alchemydumps/db-bkp-20090708100815-Post.gz

    ID: 20081208191908 (from Dec 08, 2008 at 19:19:08)
    /vagrant/alchemydumps/db-bkp-20081208191908-User.gz
    /vagrant/alchemydumps/db-bkp-20081208191908-Post.gz

    ID: 20070114122922 (from Jan 14, 2007 at 12:29:22)
    /vagrant/alchemydumps/db-bkp-20070114122922-User.gz
    /vagrant/alchemydumps/db-bkp-20070114122922-Post.gz

    ID: 20060911035318 (from Sep 11, 2006 at 03:53:18)
    /vagrant/alchemydumps/db-bkp-20060911035318-User.gz
    /vagrant/alchemydumps/db-bkp-20060911035318-Post.gz

    ID: 20051108082503 (from Nov 08, 2005 at 08:25:03)
    /vagrant/alchemydumps/db-bkp-20051108082503-User.gz
    /vagrant/alchemydumps/db-bkp-20051108082503-Post.gz

==> 11 backups will be deleted:

    ID: 20120123032442 (from Jan 23, 2012 at 03:24:42)
    /vagrant/alchemydumps/db-bkp-20120123032442-User.gz
    /vagrant/alchemydumps/db-bkp-20120123032442-Post.gz

    ID: 20101029100412 (from Oct 29, 2010 at 10:04:12)
    /vagrant/alchemydumps/db-bkp-20101029100412-User.gz
    /vagrant/alchemydumps/db-bkp-20101029100412-Post.gz

    ID: 20100526185156 (from May 26, 2010 at 18:51:56)
    /vagrant/alchemydumps/db-bkp-20100526185156-User.gz
    /vagrant/alchemydumps/db-bkp-20100526185156-Post.gz

    ID: 20100423085529 (from Apr 23, 2010 at 08:55:29)
    /vagrant/alchemydumps/db-bkp-20100423085529-User.gz
    /vagrant/alchemydumps/db-bkp-20100423085529-Post.gz

    ID: 20081006074458 (from Oct 06, 2008 at 07:44:58)
    /vagrant/alchemydumps/db-bkp-20081006074458-User.gz
    /vagrant/alchemydumps/db-bkp-20081006074458-Post.gz

    ID: 20080429210254 (from Apr 29, 2008 at 21:02:54)
    /vagrant/alchemydumps/db-bkp-20080429210254-User.gz
    /vagrant/alchemydumps/db-bkp-20080429210254-Post.gz

    ID: 20080424043716 (from Apr 24, 2008 at 04:37:16)
    /vagrant/alchemydumps/db-bkp-20080424043716-User.gz
    /vagrant/alchemydumps/db-bkp-20080424043716-Post.gz

    ID: 20080405110244 (from Apr 05, 2008 at 11:02:44)
    /vagrant/alchemydumps/db-bkp-20080405110244-User.gz
    /vagrant/alchemydumps/db-bkp-20080405110244-Post.gz

    ID: 20060629054914 (from Jun 29, 2006 at 05:49:14)
    /vagrant/alchemydumps/db-bkp-20060629054914-User.gz
    /vagrant/alchemydumps/db-bkp-20060629054914-Post.gz

    ID: 20060329020048 (from Mar 29, 2006 at 02:00:48)
    /vagrant/alchemydumps/db-bkp-20060329020048-User.gz
    /vagrant/alchemydumps/db-bkp-20060329020048-Post.gz

    ID: 20050324012859 (from Mar 24, 2005 at 01:28:59)
    /vagrant/alchemydumps/db-bkp-20050324012859-User.gz
    /vagrant/alchemydumps/db-bkp-20050324012859-Post.gz

==> Press "Y" to confirm, or anything else to abort. y
    db-bkp-20120123032442-User.gz deleted.
    db-bkp-20120123032442-Post.gz deleted.
    db-bkp-20101029100412-User.gz deleted.
    db-bkp-20101029100412-Post.gz deleted.
    db-bkp-20100526185156-User.gz deleted.
    db-bkp-20100526185156-Post.gz deleted.
    db-bkp-20100423085529-User.gz deleted.
    db-bkp-20100423085529-Post.gz deleted.
    db-bkp-20081006074458-User.gz deleted.
    db-bkp-20081006074458-Post.gz deleted.
    db-bkp-20080429210254-User.gz deleted.
    db-bkp-20080429210254-Post.gz deleted.
    db-bkp-20080424043716-User.gz deleted.
    db-bkp-20080424043716-Post.gz deleted.
    db-bkp-20080405110244-User.gz deleted.
    db-bkp-20080405110244-Post.gz deleted.
    db-bkp-20060629054914-User.gz deleted.
    db-bkp-20060629054914-Post.gz deleted.
    db-bkp-20060329020048-User.gz deleted.
    db-bkp-20060329020048-Post.gz deleted.
    db-bkp-20050324012859-User.gz deleted.
    db-bkp-20050324012859-Post.gz deleted.
```

## Requirements & Dependencies

**AlchemyDumps** is tested and should work with Python 3.6+.

## Tests

If you wanna run the tests for the current Python version:

```console
poetry install
poetry run nosetests
```

We also use some style and quality checkers:

```console
poetry run black . --check
poetry run flake8 flask_alchemydumps/ tests/
```

If you wanna cover all supported Python version, you need them installed and available via [`pyenv`](https://github.com/pyenv/pyenv). Then just `poetry run tox`.
