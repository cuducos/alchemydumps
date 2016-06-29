# coding: utf-8

from unittest import TestCase

from flask_alchemydumps.helpers.confirm import Confirm


try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestConfirmHelper(TestCase):

    def test_no_auto_confirm_upper(self):
        confirm = Confirm()
        confirm.input = MagicMock(return_value='Y')
        self.assertTrue(confirm.ask())

    def test_no_auto_confirm_lower(self):
        confirm = Confirm()
        confirm.input = MagicMock(return_value='y')
        self.assertTrue(confirm.ask())

    def test_no_auto_confirm_when_something_else(self):
        possibilities = ('x', 0, 1, '', None, False)
        confirm = Confirm()
        confirm.input = MagicMock(side_effect=possibilities)
        for user_input in possibilities:
            self.assertFalse(confirm.ask(), user_input)

    def test_auto_confirm_with_assume_yes(self):
        ok_possibilities = (True, 'Y', 1)
        for value in ok_possibilities:
            confirm = Confirm(value)
            self.assertTrue(confirm.ask(), value)

    def test_auto_confirm_without_assume_yes(self):
        cancel_possibilities = (False, '', 0)
        for value in cancel_possibilities:
            confirm = Confirm(value)
            confirm.input = MagicMock()
            self.assertFalse(confirm.ask(), value)
