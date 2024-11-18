import os
import tarfile
import json
import toml
import datetime
import sys
import tempfile
from pathlib import Path

class ShellEmulator:
    def __init__(self, config_path):
        """Загружаем конфигурацию из файла TOML"""
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
        """Логируем действия пользователя"""
        entry = {
            "user": self.user,
            "command": command,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.log_data.append(entry)
    
    def run_startup_script(self):
        """Запуск команд из стартового скрипта"""
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
            path = command[3:]
            self.cd(path)
        elif command == "uptime":
            self.uptime()
        elif command.startswith("rmdir"):
            _, path = command.split(maxsplit=1)
            self.rmdir(path)
        else:
            print(f"Команда не распознана: {command}")

    def ls(self):
        """Вывод содержимого директории"""
        items = []
        for item in self.fs.getmembers():
            if self.current_dir == '/' and '/' not in item.name.lstrip('/'):
                items.append(item.name)
            if item.name.startswith(self.current_dir):
                relative_path = item.name[len(self.current_dir):]
                if '/' not in relative_path.strip('/') and relative_path != '':
                    items.append(relative_path.strip('/'))
        if items:
            print('\n'.join(items))
        else:
            print("No files found.")

    def cd(self, path):
        """Переход в другую директорию"""
        if path == '' or path == '/':
            self.current_dir = '/'
        elif path == '..':
            if self.current_dir == '/':
                print("Находитесь в корневой директории, нельзя подняться выше.")
            else:
                self.current_dir = '/'.join(self.current_dir.split('/')[:-1]) or '/'
        elif path in self.fs.getnames():
            self.current_dir = path
        elif self.current_dir+'/'+path in self.fs.getnames():
            self.current_dir = self.current_dir+'/'+path
        else:
            print(f"cd: no such file or directory: {path}")

    def uptime(self):
        """Вывод времени работы сессии"""
        print("Сессия работает с:", datetime.datetime.now().isoformat())

    def rmdir(self, path):
        """Удаление директории"""
        normalized_path = os.path.join(self.current_dir, path).lstrip('/')
        
        # Проверяем, пуста ли директория и существует ли она
        members_to_keep = []
        directory_exists = False
        directory_empty = True
        
        for member in self.fs.getmembers():
            if member.name == normalized_path and member.isdir():
                directory_exists = True
            elif member.name.startswith(normalized_path + '/'):
                directory_empty = False
            else:
                members_to_keep.append(member)

        if not directory_exists:
            print(f"Директория {path} не найдена.")
            return

        if not directory_empty:
            print(f"Директория {path} не пуста, удаление невозможно.")
            return

        # Пересоздаем архив без удаленной директории
        with tempfile.NamedTemporaryFile(delete=False) as temp_tar_file:
            temp_tar_path = temp_tar_file.name
        
        with tarfile.open(temp_tar_path, "w") as new_tar:
            for member in members_to_keep:
                fileobj = self.fs.extractfile(member) if member.isfile() else None
                new_tar.addfile(member, fileobj=fileobj)
        
        self.fs.close()
        
        # Заменяем старый архив новым
        os.replace(temp_tar_path, self.fs_path)
        self.fs = tarfile.open(self.fs_path, "r")

    def exit(self):
        """Выход и запись лога"""
        with open(self.log_path, 'w') as log_file:
            json.dump(self.log_data, log_file, indent=4)
        self.fs.close()
        print("Сеанс завершен.")
        sys.exit()

    def prompt(self):
        """Отображение приглашения"""
        return f"{self.user}@{self.hostname}:{self.current_dir}$ "

    def run(self):
        """Основной цикл эмулятора"""
        self.run_startup_script()
        while True:
            command = input(self.prompt())
            self.execute_command(command)

if __name__ == "__main__":
    emulator = ShellEmulator("config/config.toml")
    emulator.run()
