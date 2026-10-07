import json
import shlex
import sys

from VFS import VFS, VFSError


class CLI:
    """Интерактивная оболочка эмулятора."""

    def __init__(self, vfs_path=None, script_path=None):
        """Создаёт VFS (из JSON при наличии пути) и сохраняет параметры."""
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.user = "root"
        try:
            self.vfs = VFS(path=vfs_path) if vfs_path else VFS()
        except (OSError, ValueError, json.JSONDecodeError, VFSError) as e:
            print(f"vfs error: {e}")
            self.vfs = VFS()

    def prompt(self):
        """Строка приглашения оболочки."""
        return (
            f"{self.user}@{self.vfs.name}:"
            f"{self.vfs.active_directory}$ "
        )

    def cmd_ls(self, args):
        """Список файлов/каталогов. ls [path...]"""
        paths = [a for a in args if not a.startswith("-")]
        if not paths:
            paths = ["."]
        ok = True
        multi = len(paths) > 1
        for i, path in enumerate(paths):
            if self.vfs.is_file(path):
                print(path)
            elif self.vfs.is_dir(path):
                try:
                    entries = self.vfs.list_dir(path)
                except VFSError as e:
                    print(f"ls: {e}")
                    ok = False
                    continue
                if multi:
                    print(f"{path}:")
                for name in entries:
                    print(name)
            else:
                print(f"ls: cannot access '{path}': "
                      f"No such file or directory")
                ok = False
            if multi and i != len(paths) - 1:
                print()
        return ok

    def cmd_cd(self, args):
        """Смена каталога. cd [path]"""
        if len(args) > 1:
            print("cd: too many arguments")
            return False
        path = args[0] if args else "/"
        try:
            self.vfs.chdir(path)
        except VFSError as e:
            print(f"cd: {e}")
            return False
        return True

    def cmd_echo(self, args):
        """Печать аргументов. echo [args...]"""
        print(" ".join(args))
        return True

    def cmd_du(self, args):
        """Размер файла/каталога в байтах. du [path...]"""
        paths = args if args else ["."]
        ok = True
        for path in paths:
            try:
                size = self.vfs.size_of(path)
                shown = self.vfs.resolve(path)
                print(f"{size}\t{shown}")
            except VFSError as e:
                print(f"du: {e}")
                ok = False
        return ok

    def cmd_uniq(self, args):
        """
        Уникальные подряд идущие строки файла.
        uniq [-c] FILE
        """
        count = False
        files = []
        for arg in args:
            if arg == "-c":
                count = True
            elif arg.startswith("-"):
                print(f"uniq: invalid option -- '{arg}'")
                return False
            else:
                files.append(arg)

        if len(files) != 1:
            print("uniq: expected exactly one file")
            return False

        try:
            text = self.vfs.read_text(files[0])
        except VFSError as e:
            print(f"uniq: {e}")
            return False

        lines = text.splitlines()
        prev = None
        n = 0
        for line in lines:
            if prev is None:
                prev = line
                n = 1
            elif line == prev:
                n += 1
            else:
                self._uniq_emit(prev, n, count)
                prev = line
                n = 1
        if prev is not None:
            self._uniq_emit(prev, n, count)
        return True

    @staticmethod
    def _uniq_emit(line, n, count):
        if count:
            print(f"{n:4d} {line}")
        else:
            print(line)

    def execute(self, command, args):
        """
        Выполнить одну команду.
        Возвращает True / False / 'exit'.
        """
        handlers = {
            "exit": lambda _a: "exit",
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "echo": self.cmd_echo,
            "du": self.cmd_du,
            "uniq": self.cmd_uniq,
        }
        handler = handlers.get(command)
        if handler is None:
            print("command not found: " + command)
            return False
        return handler(args)

    def handle_line(self, line):
        """Разобрать и выполнить строку ввода."""
        line = line.strip()
        if not line or line.startswith("#"):
            return True
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"parse error: {e}")
            return False
        if not parts:
            return True
        return self.execute(parts[0], parts[1:])

    def run_script(self, path):
        """
        Выполнить стартовый скрипт построчно.
        Ошибочные строки пропускаются. Ввод и вывод как в диалоге.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as e:
            print(f"script error: {e}")
            return

        for raw in lines:
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue

            print(f"{self.prompt()}{stripped}")
            result = self.handle_line(stripped)
            if result == "exit":
                return

    def run_repl(self):
        """Интерактивный цикл чтения команд."""
        while True:
            try:
                print(self.prompt(), end="", flush=True)
                raw = sys.stdin.buffer.readline()
                if raw == b"":
                    print()
                    break
                line = raw.decode("utf-8", errors="replace").rstrip("\n\r")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            result = self.handle_line(line)
            if result == "exit":
                break

    def run(self):
        """Запуск: сначала скрипт (если задан), иначе REPL."""
        if self.script_path:
            self.run_script(self.script_path)
            return
        self.run_repl()
