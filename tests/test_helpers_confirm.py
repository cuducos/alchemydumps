# coding: utf-8

from unittest import TestCase

from flask_alchemydumps.helpers.confirm import confirm


# Python 2 and 3 compatibility (mock and bultins)
try:
    from unittest.mock import patch
    input_function = 'builtins.input'
except ImportError:
    from mock import patch
    input_function = 'flask.ext.alchemydumps.helpers.confirm.input'


class TestConfirmHelper(TestCase):

    @patch(input_function)
    def test_no_auto_confirm_upper(self, mocked_input):
        mocked_input.return_value = 'Y'
        self.assertTrue(confirm())

    @patch(input_function)
    def test_no_auto_confirm_lower(self, mocked_input):
        mocked_input.return_value = 'y'
        self.assertTrue(confirm())

    @patch(input_function)
    def test_no_auto_confirm_when_something_else(self, mocked_input):
        possibilities = ('x', 0, 1, '', None, False)
        mocked_input.side_effect = possibilities
        for user_input in possibilities:
            self.assertFalse(confirm())

    @patch(input_function)
    def test_auto_confirm(self, mocked_input):
        mocked_input.return_value = ''
        ok_possibilities = (True, 'Y', 1)
        cancel_possibilities = (False, '', 0)
        for default_value in ok_possibilities:
            self.assertTrue(confirm(default_value), default_value)
        for default_value in cancel_possibilities:
            self.assertFalse(confirm(default_value), default_value)
