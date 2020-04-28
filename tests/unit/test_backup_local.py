from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from flask_alchemydumps.backup import LocalTools


class TestLocalTools(TestCase):
    def setUp(self):
        self.backup_dir = ".test-local-tools/"
        self.backup_path = Path(self.backup_dir).absolute()

    @patch.object(Path, "mkdir")
    @patch.object(Path, "is_file")
    @patch.object(Path, "glob")
    def test_get_files(self, mock_glob, mock_is_file, _mock_mkdir):
        mock_glob.return_value = (
            self.backup_path / "BRA-19940704123000-USA.gz",
            self.backup_path / "BRA-19940709163000-NED.gz",
            self.backup_path / "BRA-19940713123XXX-SWE.gz",
            self.backup_path / "BRA-19940717123000-ITA.gz",
        )
        mock_is_file.side_effect = (True, True, True, False)
        expected = (
            self.backup_path / "BRA-19940704123000-USA.gz",
            self.backup_path / "BRA-19940709163000-NED.gz",
        )
        backup = LocalTools(self.backup_dir)
        self.assertEqual(expected, tuple(backup.get_files()))
        mock_glob.assert_called_once_with("*")

    @patch.object(Path, "mkdir")
    @patch.object(Path, "exists")
    @patch("flask_alchemydumps.backup.gzip.open")
    def test_create_file(self, mock_open, mock_exists, _mock_mkdir):
        mock_exists.return_value = False
        path = self.backup_path / "foobar.gz"
        backup = LocalTools(self.backup_dir)
        created = backup.create_file("foobar.gz", b"42")
        mock_open.assert_called_once_with(path, "wb")
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(
            b"42"
        )
        self.assertEqual(path, created)

    @patch.object(Path, "mkdir")
    @patch.object(Path, "exists")
    @patch("flask_alchemydumps.backup.gzip.open")
    def test_read_file(self, mock_open, mock_exists, _mock_mkdir):
        mock_exists.return_value = False
        path = self.backup_path / "foobar.gz"
        backup = LocalTools(self.backup_dir)
        backup.read_file("foobar.gz")
        mock_open.assert_called_once_with(path, "rb")
        mock_open.return_value.__enter__.return_value.read.assert_called_once_with()

    @patch.object(Path, "mkdir")
    @patch.object(Path, "exists")
    @patch.object(Path, "unlink")
    def test_delete_file(self, mock_unlink, mock_exists, _mock_mkdir):
        mock_exists.return_value = False
        backup = LocalTools(self.backup_dir)
        backup.delete_file("foobar.gz")
        mock_unlink.assert_called_once_with()
