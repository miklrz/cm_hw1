@patch('builtins.print')
    # @patch('os.getlogin', return_value='testuser')
    # def test_whoami(self, mock_getlogin, mock_print):
    #     """Тестирует команду 'whoami', которая возвращает имя пользователя."""
    #     self.emulator.whoami()
    #     mock_print.assert_called_once_with('testuser')

    # @patch('builtins.print')
    # def test_tac_file(self, mock_print):
    #     """Тестирует команду 'tac' для существующего файла."""
    #     self.emulator.tac(['file1.txt'])
    #     mock_print.assert_has_calls([
    #         unittest.mock.call("\n--- file1.txt ---\n"),
    #         unittest.mock.call("Hello, World!")
    #     ])

    # @patch('builtins.print')
    # def test_tac_directory(self, mock_print):
    #     """Тестирует обработку попытки использовать 'tac' для директории."""
    #     self.emulator.tac(['dir1'])
    #     mock_print.assert_called_once_with("Нельзя так делать: нельзя использовать tac для директории.")

    # @patch('builtins.print')
    # def test_tac_nonexistent(self, mock_print):
    #     """Тестирует обработку попытки использовать 'tac' для несуществующего файла."""
    #     self.emulator.tac(['nonexistent.txt'])
    #     mock_print.assert_called_once_with("tac: nonexistent.txt: No such file")