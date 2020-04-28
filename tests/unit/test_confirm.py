from unittest import TestCase
from unittest.mock import patch

from flask_alchemydumps.confirm import Confirm


class TestConfirmHelper(TestCase):

    @patch('flask_alchemydumps.confirm.click.getchar')
    def test_no_auto_confirm_upper(self, mock_getchar):
        mock_getchar.return_value = 'Y'
        confirm = Confirm()
        self.assertTrue(confirm.ask())

    @patch('flask_alchemydumps.confirm.click.getchar')
    def test_no_auto_confirm_lower(self, mock_getchar):
        mock_getchar.return_value = 'y'
        confirm = Confirm()
        self.assertTrue(confirm.ask())

    @patch('flask_alchemydumps.confirm.click.getchar')
    def test_no_auto_confirm_when_something_else(self, mock_getchar):
        possibilities = ('x', '0', '1', '')
        mock_getchar.side_effect = possibilities
        confirm = Confirm()
        for user_input in possibilities:
            with self.subTest():
                self.assertFalse(confirm.ask(), user_input)

    def test_auto_confirm_with_assume_yes(self):
        ok_possibilities = (True, 'Y', 1)
        for value in ok_possibilities:
            confirm = Confirm(value)
            self.assertTrue(confirm.ask(), value)

    @patch('flask_alchemydumps.confirm.click.getchar')
    def test_auto_confirm_without_assume_yes(self, _mock_getchar):
        cancel_possibilities = (False, '', 0)
        for value in cancel_possibilities:
            confirm = Confirm(value)
            self.assertFalse(confirm.ask(), value)
