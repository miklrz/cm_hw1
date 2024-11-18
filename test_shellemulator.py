import unittest
from unittest.mock import patch, MagicMock
import os
import tarfile
import json
import io
import toml
from shellemulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Создает временный tar-архив с тестовыми файлами и инициализирует эмулятор."""
        self.config_path = 'test_config.txt'
        self.config = toml.load(self.config_path)
        self.tar_path = self.config["filesystem_path"]
        self.log_path = self.config['log_path']
        self.startup_script = self.config['startup_script']
        with tarfile.open(self.tar_path, 'w') as tar:
            tarinfo = tarfile.TarInfo(name="file1.txt")
            tarinfo.size = len("Hello, World!\n")
            tar.addfile(tarinfo, io.BytesIO(b"Hello, World!\n"))
            tarinfo = tarfile.TarInfo(name="dir1/")
            tarinfo.type = tarfile.DIRTYPE
            tar.addfile(tarinfo)
            tarinfo = tarfile.TarInfo(name="dir1/file2.txt")
            tarinfo.size = len("Content of file2.txt\n")
            tar.addfile(tarinfo, io.BytesIO(b"Content of file2.txt\n"))

        self.emulator = ShellEmulator(self.config_path)

    def tearDown(self):
        """Удаляет временные файлы после завершения тестов."""
        os.remove(self.tar_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        if os.path.exists(self.startup_script):
            os.remove(self.startup_script)

    @patch('builtins.print')
    def test_ls_root(self, mock_print):
        """Тестирует команду 'ls' в корневом каталоге."""
        self.emulator.ls()
        mock_print.assert_called_once_with("file1.txt\ndir1")

    @patch('builtins.print')
    def test_ls_dir1(self, mock_print):
        """Тестирует команду 'ls' в подкаталоге 'dir1'."""
        self.emulator.cd('dir1')
        self.emulator.ls()
        mock_print.assert_called_once_with("file2.txt")

    @patch('builtins.print')
    def test_cd_root(self, mock_print):
        """Тестирует переход в корневой каталог из подкаталога."""
        self.emulator.cd('dir1')
        self.emulator.cd('/')
        self.assertEqual(self.emulator.current_dir, '/')

    @patch('builtins.print')
    def test_cd_dir1(self, mock_print):
        """Тестирует переход в подкаталог 'dir1' и проверяет текущий каталог."""
        self.emulator.cd('dir1')
        self.emulator.ls()
        self.assertEqual(self.emulator.current_dir, 'dir1/')

    @patch('builtins.print')
    def test_cd_parent(self, mock_print):
        """Тестирует переход на уровень вверх из подкаталога."""
        self.emulator.cd('dir1')
        self.emulator.cd('..')
        self.assertEqual(self.emulator.current_dir, '/')

    @patch('builtins.print')
    def test_cd_nonexistent(self, mock_print):
        """Тестирует обработку попытки перехода в несуществующий каталог."""
        self.emulator.cd('nonexistent')
        mock_print.assert_called_once_with("cd: no such file or directory: nonexistent")

    @patch('builtins.print')
    @patch('sys.exit')
    def test_exit(self, mock_exit, mock_print):
        """Тестирует корректное завершение работы эмулятора."""
        self.emulator.exit()
        mock_print.assert_called_once_with("Exiting...")
        mock_exit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()