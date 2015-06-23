# coding: utf-8

from flask.ext.alchemydumps.helpers.confirm import confirm
from unittest import TestCase

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
    def test_no_auto_do_not_confirm(self, mocked_input):
        mocked_input.return_value = 'x'
        self.assertFalse(confirm())

    @patch(input_function)
    def test_no_auto_do_blank(self, mocked_input):
        mocked_input.return_value = ''
        self.assertFalse(confirm())

    @patch(input_function)
    def test_auto_confirm(self, mocked_input):
        mocked_input.return_value = ''
        self.assertTrue(confirm(True))
        self.assertTrue(confirm('Y'))
        self.assertTrue(confirm(1))
        self.assertFalse(confirm(False))
        self.assertFalse(confirm(0))
        self.assertFalse(confirm(''))
