#!/usr/bin/env python3
"""Прототип эмулятора командной оболочки (CLI).

Возможности этапа 1:
    * приглашение к вводу строится из реальных данных ОС;
    * парсер учитывает кавычки (одинарные и двойные);
    * сообщения об ошибках (неизвестная команда, неверные аргументы);
    * команды-заглушки ls и cd, команда exit.
"""

import getpass
import os
import shlex
import socket
import sys


class ShellError(Exception):
    """Ошибка выполнения команды, сообщение которой видит пользователь."""


def get_prompt():
    """Сформировать приглашение вида username@hostname:~$."""
    try:
        username = getpass.getuser()
    except (KeyError, OSError):
        username = "user"
    hostname = socket.gethostname()

    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd == home:
        cwd = "~"
    elif cwd.startswith(home + os.sep):
        cwd = "~" + cwd[len(home):]

    return f"{username}@{hostname}:{cwd}$ "


def parse_line(line):
    """Разобрать строку на токены с учётом кавычек.

    Вызывает ShellError, если кавычка или экранирование не закрыты.
    """
    try:
        return shlex.split(line, posix=True)
    except ValueError as error:
        raise ShellError(f"ошибка разбора: {error}") from error


def cmd_ls(args):
    """Заглушка ls: выводит своё имя и аргументы."""
    print_stub("ls", args)


def cmd_cd(args):
    """Заглушка cd: выводит своё имя и аргументы."""
    print_stub("cd", args)


def cmd_exit(args):
    """Завершить работу эмулятора с необязательным кодом возврата."""
    if len(args) > 1:
        raise ShellError("exit: слишком много аргументов")
    code = 0
    if args:
        try:
            code = int(args[0])
        except ValueError:
            raise ShellError(
                f"exit: неверный аргумент: '{args[0]}' "
                "(требуется целое число)"
            ) from None
    sys.exit(code)


def print_stub(name, args):
    """Вывести имя команды и список аргументов."""
    print(f"{name}: аргументы = {args}")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute(tokens):
    """Выполнить команду, заданную списком токенов."""
    if not tokens:
        return
    name, args = tokens[0], tokens[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        raise ShellError(f"{name}: команда не найдена")
    handler(args)


def main():
    """Главный цикл чтения и выполнения команд."""
    while True:
        try:
            line = input(get_prompt())
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue

        try:
            execute(parse_line(line))
        except ShellError as error:
            print(error, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())


