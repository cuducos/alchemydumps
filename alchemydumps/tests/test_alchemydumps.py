# coding: utf-8
import alchemydumps
from unipath import Path
from unittest import TestCase


class TestAlchemyDumps(TestCase):

    def test_get_id(self):
        filepath = Path('/vagrant/alchemydumps/db-bkp-20141115172107-User.gz')
        assert alchemydumps.get_id(filepath) == '20141115172107'

    def test_get_list(self):
        date_ids = ['20141115172107', '20141112113214']
        models = ['User', 'Post']
        prefix ='/vagrant/alchemydumps/'
        files = list()
        for i in date_ids:
            for m in models:
                files.append(Path('{}db-bkp-{}-{}.gz'.format(prefix, i, m)))
        expected = [Path('{}db-bkp-{}-{}.gz'.format(prefix, date_ids[0], m)) for m in models]
        assert alchemydumps.get_list(date_ids[0], files) == expected

    def test_get_ids(self):
        date_ids = ['20141115172107', '20141112113214']
        models = ['User', 'Post']
        prefix ='/vagrant/alchemydumps/'
        files = list()
        for i in date_ids:
            for m in models:
                files.append(Path('{}db-bkp-{}-{}.gz'.format(prefix, i, m)))
        assert alchemydumps.get_ids(files) == date_ids