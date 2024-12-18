# Домашнее задание №1 по дисциплине "Конфигурационное управление"

## Задание 1. Вариант 3

Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу эмулятора 
как можно более похожей на сеанс shell в UNIX-подобной ОС. Эмулятор должен запускаться
из реальной командной строки, а файл с виртуальной файловой системой не нужно распаковывать 
у пользователя. Эмулятор принимает образ виртуальной файловой системы в виде файла формата 
**tar**. Эмулятор должен работать в режиме **CLI**.

Конфигурационный файл имеет формат toml и содержит:
- Имя пользователя для показа в приглашении к вводу.
- Имя компьютера для показа в приглашении к вводу.
- Путь к архиву виртуальной файловой системы.
- Путь к лог-файлу.
- Путь к стартовому скрипту.

Лог-файл имеет формат json и содержит все действия во время последнего сеанса работы с 
эмулятором. Для каждого действия указаны дата и время. Для каждого действия указан пользователь.
Стартовый скрипт служит для начального выполнения заданного списка команд из файла.
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также следующие команды:

1. uptime.
2. rmdir.

Все функции эмулятора должны быть покрыты тестами, а для каждой из поддерживаемых 
команд необходимо написать 3 теста.

--- 

# Shell Emulator

Этот проект реализует эмулятор командной строки, напоминающий UNIX-подобный shell. 
Он работает с виртуальной файловой системой в формате tar, читает конфигурацию из файла TOML 
и поддерживает базовые команды управления файлами и каталогами.

## Функционал

Эмулятор поддерживает следующие команды:
- `ls`: вывод содержимого текущей директории.
- `cd <путь>`: переход в указанный каталог.
- `cd ..`: переход в родительский каталог.
- `exit`: завершение сеанса и запись лога в JSON.
- `uptime`: отображение времени работы текущей сессии.
- `rmdir <путь>`: удаление пустого каталога.

## Устройство проекта

### Основной класс

`ShellEmulator` реализует:
1. Чтение конфигурации из TOML-файла.
2. Открытие и обработку файловой системы (tar-архива).
3. Логирование команд пользователя.
4. Основной цикл работы, отображающий приглашение и выполняющий команды.

### Конфигурация

Эмулятор загружает настройки из файла TOML с ключами:
- `user`: имя пользователя.
- `hostname`: имя компьютера.
- `filesystem_path`: путь к tar-архиву файловой системы.
- `log_path`: путь для сохранения лога.
- `startup_script`: путь к файлу с командами, которые выполняются при запуске.

Пример `config.toml`:
```toml
user = "testuser"
hostname = "localhost"
filesystem_path = "filesystem.tar"
log_path = "log.json"
startup_script = "startup.sh"
```

### Логирование

Все действия пользователя записываются в лог-файл в формате JSON, включая:
- Имя пользователя.
- Команду.
- Время выполнения.

Пример лога:
```json
[
    {
        "user": "testuser",
        "command": "ls",
        "timestamp": "2024-11-26T10:00:00"
    },
    {
        "user": "testuser",
        "command": "exit",
        "timestamp": "2024-11-26T10:05:00"
    }
]
```

## Тестирование

Для проверки корректности работы эмулятора предоставлены модульные тесты (`unittest`). 
Тесты покрывают:
- Команды `ls`, `cd`, `uptime`, `exit`.
- Обработку несуществующих каталогов.
- Удаление пустых директорий.

Пример запуска тестов:
```bash
python -m unittest test_shellemulator.py
```

### Тестовые данные

Для тестов автоматически создаётся временная файловая система с файлами:
- `file1.txt`
- `dir1/`
- `dir1/file2.txt`

## Установка и запуск

1. Склонируйте репозиторий.
2. Убедитесь, что установлен Python 3.8+.
3. Установите зависимости:
   ```bash
   pip install toml
   ```
4. Настройте файл `config.toml`.
5. Запустите эмулятор:
   ```bash
   python shellemulator.py
   ```

## Использование

Пример работы:
```bash
testuser@localhost:/home$ ls
file1.txt
dir1
testuser@localhost:/home$ cd dir1
testuser@localhost:/home/dir1$ ls
file2.txt
testuser@localhost:/home/dir1$ uptime
Сессия работает: 2024-11-26T10:05:00 Время работы: 0:05:00
testuser@localhost:/home/dir1$ exit
Сеанс завершен.
```