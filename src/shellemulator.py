import os
import tarfile
import json
import toml
import datetime
import sys
from pathlib import Path

class ShellEmulator:
    def __init__(self, config_path):
        # Загружаем конфигурацию из файла TOML
        self.config = toml.load(config_path)
        self.user = self.config["user"]
        self.hostname = self.config["hostname"]
        self.fs_path = self.config["filesystem_path"]
        self.log_path = self.config["log_path"]
        self.startup_script_path = self.config["startup_script"]
        self.current_dir = '/'
        self.log_data = []

        # Открываем виртуальную файловую систему
        self.fs = tarfile.open(self.fs_path, "r")

    def log_action(self, command):
        # Логируем действия пользователя
        entry = {
            "user": self.user,
            "command": command,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.log_data.append(entry)
    
    def run_startup_script(self):
        # Запуск команд из стартового скрипта
        if os.path.exists(self.startup_script_path):
            with open(self.startup_script_path) as script:
                for command in script:
                    self.execute_command(command.strip())
    
    def execute_command(self, command):
        # Выполнение команд
        self.log_action(command)
        if command == "exit":
            self.exit()
        elif command == "ls":
            self.ls()
        elif command.startswith("cd"):
            _, path = command.split(maxsplit=1)
            self.cd(path)
        elif command == "uptime":
            self.uptime()
        elif command.startswith("rmdir"):
            _, path = command.split(maxsplit=1)
            self.rmdir(path)
        else:
            print(f"Команда не распознана: {command}")

    def ls(self):
        # Вывод содержимого директории
        members = [member for member in self.fs.getmembers() if member.name.startswith(self.current_dir)]
        for member in members:
            print(member.name)

    def cd(self, path):
        # Переход в другую директорию
        new_path = os.path.join(self.current_dir, path)
        if any(member.name == new_path for member in self.fs.getmembers()):
            self.current_dir = new_path
        else:
            print(f"Нет такой директории: {path}")

    def uptime(self):
        # Вывод времени работы сессии
        print("Сессия работает с:", datetime.datetime.now().isoformat())

    def rmdir(self, path):
        # Удаление директории
        target_path = os.path.join(self.current_dir, path)
        if any(member.name == target_path for member in self.fs.getmembers()):
            print(f"Удалена директория: {target_path}")
        else:
            print(f"Директория не найдена: {path}")

    def exit(self):
        # Выход и запись лога
        with open(self.log_path, 'w') as log_file:
            json.dump(self.log_data, log_file, indent=4)
        print("Сеанс завершен.")
        sys.exit()

    def prompt(self):
        # Отображение приглашения
        return f"{self.user}@{self.hostname}:{self.current_dir}$ "

    def run(self):
        # Основной цикл эмулятора
        self.run_startup_script()
        while True:
            command = input(self.prompt())
            self.execute_command(command)

if __name__ == "__main__":
    emulator = ShellEmulator("config/config.toml")
    emulator.run()
