# coding: utf-8

from flask.ext.alchemydumps.helpers.confirm import confirm
from mock import patch
from unittest import TestCase


class TestConfirmHelper(TestCase):

    @patch('__builtin__.raw_input')
    def test_no_auto_confirm_upper(self, mocked_input):
        mocked_input.return_value = 'Y'
        self.assertTrue(confirm())

    @patch('__builtin__.raw_input')
    def test_no_auto_confirm_lower(self, mocked_input):
        mocked_input.return_value = 'y'
        self.assertTrue(confirm())

    @patch('__builtin__.raw_input')
    def test_no_auto_do_not_confirm(self, mocked_input):
        mocked_input.return_value = 'x'
        self.assertFalse(confirm())

    @patch('__builtin__.raw_input')
    def test_no_auto_do_blank(self, mocked_input):
        mocked_input.return_value = ''
        self.assertFalse(confirm())

    def test_auto_confirm(self):
        self.assertTrue(confirm(True))
        self.assertTrue(confirm('Y'))
        self.assertTrue(confirm(1))
