import unittest
from unittest.mock import patch, MagicMock
import os
import tarfile
import json
import io
import toml
from shellemulator import ShellEmulator
import datetime


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Создает временный tar-архив с тестовыми файлами и инициализирует эмулятор."""
        self.config_path = "test_config.txt"
        self.config = toml.load(self.config_path)
        self.tar_path = self.config["filesystem_path"]
        with tarfile.open(self.tar_path, "w") as tar:
            tarinfo = tarfile.TarInfo(name="file1.txt")
            tarinfo.size = len("Hello, World!\n")
            tar.addfile(tarinfo, io.BytesIO(b"Hello, World!\n"))
            tarinfo = tarfile.TarInfo(name="dir1/")
            tarinfo.type = tarfile.DIRTYPE
            tar.addfile(tarinfo)
            tarinfo = tarfile.TarInfo(name="dir1/file2.txt")
            tarinfo.size = len("Content of file2.txt\n")
            tar.addfile(tarinfo, io.BytesIO(b"Content of file2.txt\n"))

        self.log_path = self.config["log_path"]
        self.startup_script = self.config["startup_script"]
        self.emulator = ShellEmulator(self.config_path)

    def tearDown(self):
        """Удаляет временные файлы после завершения тестов."""
        self.emulator.close()
        os.remove(self.tar_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        if os.path.exists(self.startup_script):
            os.remove(self.startup_script)

    @patch("builtins.print")
    def test_ls_root(self, mock_print):
        """Тестирует команду 'ls' в корневом каталоге."""
        self.emulator.ls()
        mock_print.assert_called_once_with("file1.txt\ndir1")

    @patch("builtins.print")
    def test_ls_dir1(self, mock_print):
        """Тестирует команду 'ls' в подкаталоге 'dir1'."""
        self.emulator.cd("dir1")
        self.emulator.ls()
        mock_print.assert_called_once_with("file2.txt")

    @patch("builtins.print")
    def test_cd_root(self, mock_print):
        """Тестирует переход в корневой каталог из подкаталога."""
        self.emulator.cd("dir1")
        self.emulator.cd("/")
        self.assertEqual(self.emulator.current_dir, "/")

    @patch("builtins.print")
    def test_cd_dir1(self, mock_print):
        """Тестирует переход в подкаталог 'dir1' и проверяет текущий каталог."""
        self.emulator.cd("dir1")
        self.emulator.ls()
        self.assertEqual(self.emulator.current_dir, "dir1")

    @patch("builtins.print")
    def test_cd_parent(self, mock_print):
        """Тестирует переход на уровень вверх из подкаталога."""
        self.emulator.cd("dir1")
        self.emulator.cd("..")
        self.assertEqual(self.emulator.current_dir, "/")

    @patch("builtins.print")
    def test_cd_nonexistent(self, mock_print):
        """Тестирует обработку попытки перехода в несуществующий каталог."""
        self.emulator.cd("nonexistent")
        mock_print.assert_called_once_with("cd: no such file or directory: nonexistent")

    # @patch("builtins.print")
    # def test_uptime(self, mock_print):
    #     """Тестирует вывод времени работы сессии"""
    #     self.emulator.uptime()
    #     self.assertEqual()

    @patch("builtins.print")  # Мокаем встроенную функцию print
    @patch("datetime.datetime")
    def test_uptime(self, mock_datetime, mock_print):
        """Тестирует функцию uptime, проверяя правильность формата строки."""

        # Создаем фиктивное время старта
        start_time = datetime.datetime(2024, 11, 18, 10, 0, 0)
        mock_datetime.now.return_value = datetime.datetime(2024, 11, 18, 10, 5, 0)
        mock_datetime.now().isoformat.return_value = "2024-11-18T10:05:00"

        # Эмулятор с этим временем старта
        emulator = ShellEmulator("config/config.toml")
        emulator.start_time = start_time  # Присваиваем фиксированное время начала

        emulator.uptime()

        # Ожидаем, что время работы сессии будет 5 минут
        # expected_output = "Сессия работает: 2024-11-18T10:05:00 Время работы: 0:05:00"

        formatted_uptime = str(mock_datetime.now() - start_time).split(".")[0]

        # Ожидаем, что время работы сессии будет 4 года
        expected_output = (
            f"Сессия работает: {mock_datetime.now().isoformat()} "
            f"Время работы: {formatted_uptime}"
        )

        # Проверяем, что функция print была вызвана с правильной строкой
        mock_print.assert_called_once_with(expected_output)

    @patch("builtins.print")  # Мокаем встроенную функцию print
    @patch("datetime.datetime")
    def test_uptime_zero_duration(self, mock_datetime, mock_print):
        """Тестирует функцию uptime сразу после старта эмулятора, когда время работы равно нулю."""

        # Эмулятор с фиктивным временем старта
        start_time = datetime.datetime(2024, 11, 18, 10, 0, 0)
        mock_datetime.now.return_value = start_time
        mock_datetime.now().isoformat.return_value = start_time.isoformat()

        emulator = ShellEmulator("config/config.toml")
        emulator.start_time = start_time  # Присваиваем время старта

        emulator.uptime()

        # Ожидаем, что время работы сессии будет 0
        # expected_output = (
        #     f"Сессия работает: {start_time.isoformat()} Время работы: 0:00:00"
        # )

        formatted_uptime = str(mock_datetime.now() - start_time).split(".")[0]

        # Ожидаем, что время работы сессии будет 4 года
        expected_output = (
            f"Сессия работает: {mock_datetime.now().isoformat()} "
            f"Время работы: {formatted_uptime}"
        )

        # Проверяем, что функция print была вызвана с правильной строкой
        mock_print.assert_called_once_with(expected_output)

    @patch("builtins.print")  # Мокаем встроенную функцию print
    @patch("datetime.datetime")
    def test_uptime_large_duration(self, mock_datetime, mock_print):
        """Тестирует функцию uptime для длительного времени работы сессии."""

        # Эмулятор с временем старта
        start_time = datetime.datetime(2020, 11, 18, 10, 0, 0)
        mock_datetime.now.return_value = datetime.datetime(2024, 11, 18, 10, 0, 0)
        mock_datetime.now().isoformat.return_value = "2024-11-18T10:00:00"

        emulator = ShellEmulator("config/config.toml")
        emulator.start_time = start_time  # Присваиваем время старта

        emulator.uptime()

        formatted_uptime = str(mock_datetime.now() - start_time).split(".")[0]

        # Ожидаем, что время работы сессии будет 4 года
        expected_output = (
            f"Сессия работает: {mock_datetime.now().isoformat()} "
            f"Время работы: {formatted_uptime}"
        )

        # Проверяем, что функция print была вызвана с правильной строкой
        mock_print.assert_called_once_with(expected_output)

    @patch("builtins.print")
    @patch("sys.exit")
    def test_exit(self, mock_exit, mock_print):
        """Тестирует корректное завершение работы эмулятора."""
        self.emulator.exit()
        mock_print.assert_called_once_with("Сеанс завершен.")
        mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
