AlchemyDumps
------------

.. image:: https://pypip.in/version/Flask-AlchemyDumps/badge.svg
    :target: https://pypi.python.org/pypi/Flask-AlchemyDumps/
    :alt: Latest Version
.. image:: https://pypip.in/download/Flask-AlchemyDumps/badge.svg
    :target: https://pypi.python.org/pypi//Flask-AlchemyDumps/
    :alt: Downloads
.. image:: https://pypip.in/license/Flask-AlchemyDumps/badge.svg
    :target: https://pypi.python.org/pypi/Flask-AlchemyDumps/
    :alt: License

Do you use `Flask <http://flask.pocoo.org>`_ with `SQLAlchemy <http://www.sqlalchemy.org/>`_  and `Flask-Script <http://flask-script.readthedocs.org/en/latest/>`_ ? Wow, what a coincidence!

This package let you backup and restore all your data using `SQLALchemy dumps() method <http://docs.sqlalchemy.org/en/latest/core/serializer.html>`_.

It is an easy way (one singe command, I mean it) to save **all** the data stored in your database.

Install
-------

First install the package: ``$ pip install Flask-AlchemyDumps``

Then configure it in your Flask application:

::

    from alchemydumps import AlchemyDumps, AlchemyDumpsCommand
    from flask import Flask
    from flask.ext.script import Manager
    from flask.ext.sqlalchemy import SQLAlchemy

    # init Flask
    app = Flask(__name__)

    # init SQLAlchemy and Flask-Script
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    db = SQLAlchemy(app)
    manager = Manager(app)

    # init Alchemy Dumps
    alchemydumps = AlchemyDumps(app, db)
    manager.add_command('alchemydumps', AlchemyDumpsCommand)

The **first line** import the methods from the package.

The **last two lines** instantiate and add AlchemyDumps to the *Flask-Script manager*).

You might want to add ``alchemydumps`` to your ``.gitignore``. It is the folder where **AlchemyDumps** save the backup files.

Examples
--------

Considering you have these *models* (`SQLAlchemy mapped classes <http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html>`_):

::

    class User(Model):
        id = Column(Integer, primary_key=True)
        email = Column(String(140), index=True, unique=True)
        ...
    
    class Post(Model):
        id = Column(Integer, primary_key=True)
        title = Column(String(140))
        content = Column(UnicodeText)
        ...


You can backup all your data
----------------------------

::

    $ python manage.py alchemydumps create

Output:

::

    ==> 3 rows from User post saved as /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
    ==> 42 rows from Post saved as /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz

You can list the backups you have already created
-------------------------------------------------
::

    $ python manage.py alchemydumps history

Output:
	
::

    ==> ID: 20141114203949 (from Nov 15, 2014 at 17:21:07)
        /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
        /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz

    ==> ID: 20141115140629 (from Nov 15, 2014 at 14:06:29)
        /vagrant/alchemydumps/db-bkp-20141115140629-User.gz
        /vagrant/alchemydumps/db-bkp-20141115140629-Post.gz

You can restore a backup
------------------------

::

    $ python manage.py alchemydumps restore -d 20141115172107

Output:

::

    ==> /vagrant/alchemydumps/db-bkp-20141115172107-User.gz totally restored.
    ==> /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz totally restored.


You can delete an existing backup
---------------------------------

::

    $ python manage.py alchemydumps remove -d 20141115172107

Output:

::

    ==> Do you want to delete the following files?
        /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
        /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz
    ==> Press "Y" to confirm, or anything else to abort.
        /vagrant/alchemydumps/db-bkp-20141115172107-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz deleted.


And you can use the auto-clean command
--------------------------------------

The ``autoclean`` command follows these rules to delete backups:

* It keeps **all** the backups from the last 7 days.
* It keeps **the most recent** backup **from each week of the last month**.
* It keeps **the most recent** backup **from each month of the last year**.
* It keeps **the most recent** backup **from each year** of the remaining years.

::

    $ python manage.py alchemydumps autoclean

Output:

::

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

    ==> Press "Y" to confirm, or anything else to abort.
        /vagrant/alchemydumps/db-bkp-20120123032442-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20120123032442-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20101029100412-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20101029100412-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20100526185156-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20100526185156-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20100423085529-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20100423085529-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20081006074458-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20081006074458-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20080429210254-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20080429210254-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20080424043716-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20080424043716-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20080405110244-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20080405110244-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20060629054914-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20060629054914-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20060329020048-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20060329020048-Post.gz deleted.
        /vagrant/alchemydumps/db-bkp-20050324012859-User.gz deleted.
        /vagrant/alchemydumps/db-bkp-20050324012859-Post.gz deleted.

Requirements
------------

As **AlchemyDumps** was designed to work together with `Flask <http://flask.pocoo.org>`_ applications that uses `SQLAlchemy <http://www.sqlalchemy.org/>`_. And it runs within the `Flask-Script <http://flask-script.readthedocs.org/en/latest/>`_ manager. Thus, be sure to have these packages installed and in use.

**AlchemyDumps** also uses `Unipath <https://github.com/mikeorr/Unipath>`_ package.

In sum, if your ``requirements.txt`` looks something like this, probably you will be fine:

::

    Flask>=0.10.1
    Flask-Script>=2.0.5
    Flask-SQLAlchemy>=0.16
    SQLAlchemy>=0.7.9
    Unipath>=1.0

**AlchemyDumps** is `not` ready for Python 3 yet – but pull requests are more than welcomed.

Tests
-----

If you wanna run the tests:

::

    $ git clone git@github.com:cuducos/alchemydumps.git
    $ cd /alchemydumps
    $ pip install nose unipath
    $ nosetests

Contributing
------------

You can `report issues <https://github.com/cuducos/alchemydumps/issues>`_ or:

* Fork this repo
* Create a new branch: ``git checkout -b my-new-feature``
* Commit your changes: ``git add -A . && commit -m 'Add some feature'``
* Push to the branch: ``git push origin my-new-feature``
* And create new `pull request`

Changelog
---------

**Version 0.0.3**
    * New command: auto-clean backup folder.
**Version 0.0.2**
    * New command: delete a single backup.
    * Proper message when ID is not found in restore and delete commands.
    * Avoid breaking the code when get_id() fails.
    * Minor code improvements.

License
-------

Copyright (c) 2014 Eduardo Cuducos.

Licensed under the `MIT License <http://opensource.org/licenses/MIT>`_.
