import json
import shlex
import sys
from datetime import datetime

from VFS import VFS, VFSError

_KIB = 1024
_SIZE_UNITS = ("K", "M", "G", "T")
_LS_FLAGS = frozenset("lha")


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
        """Список файлов/каталогов. ls [-lha] [path...]"""
        parsed = self._parse_ls_args(args)
        if parsed is None:
            return False
        long_fmt, human, show_all, paths = parsed
        ok = True
        multi = len(paths) > 1
        for i, path in enumerate(paths):
            if not self._ls_one(path, long_fmt, human, show_all, multi):
                ok = False
            if multi and i != len(paths) - 1:
                print()
        return ok

    def _parse_ls_args(self, args):
        """Флаги и пути ls. None при неизвестном флаге."""
        flags = {name: False for name in _LS_FLAGS}
        paths = []
        for arg in args:
            if arg.startswith("-") and arg != "-":
                if not self._apply_ls_flags(arg[1:], flags):
                    return None
            else:
                paths.append(arg)
        if not paths:
            paths = ["."]
        return flags["l"], flags["h"], flags["a"], paths

    @staticmethod
    def _apply_ls_flags(chars, flags):
        """Включить флаги ls. False, если символ неизвестен."""
        for ch in chars:
            if ch not in _LS_FLAGS:
                print(f"ls: invalid option -- '{ch}'")
                return False
            flags[ch] = True
        return True

    def _ls_one(self, path, long_fmt, human, show_all, multi):
        """Обработать один аргумент ls."""
        if self.vfs.is_file(path):
            self._ls_print_entry(path, path, long_fmt, human)
            return True
        if self.vfs.is_dir(path):
            return self._ls_dir(path, long_fmt, human, show_all, multi)
        print(f"ls: cannot access '{path}': "
              f"No such file or directory")
        return False

    def _ls_dir(self, path, long_fmt, human, show_all, multi):
        """Вывести содержимое каталога."""
        try:
            entries = self.vfs.list_dir(path)
        except VFSError as e:
            print(f"ls: {e}")
            return False
        names = self._ls_names(entries, show_all)
        if multi:
            print(f"{path}:")
        for name in names:
            child = self._ls_child_path(path, name)
            self._ls_print_entry(name, child, long_fmt, human)
        return True

    @staticmethod
    def _ls_names(entries, show_all):
        """Имена для вывода ls с учётом -a."""
        if not show_all:
            return [n for n in entries if not n.startswith(".")]
        return [".", ".."] + entries

    def _ls_child_path(self, path, name):
        """Путь дочерней записи каталога."""
        if name == ".":
            return path
        if name == "..":
            return self.vfs.resolve(f"{path}/..")
        if path == "/":
            return f"/{name}"
        return f"{path.rstrip('/')}/{name}"

    @staticmethod
    def _human_size(size):
        """Размер в человекочитаемом виде (-h)."""
        if size < _KIB:
            return f"{size}B"
        value = float(size) / _KIB
        last = _SIZE_UNITS[-1]
        for unit in _SIZE_UNITS:
            if value < _KIB or unit == last:
                text = f"{value:.1f}".rstrip("0").rstrip(".")
                return f"{text}{unit}"
            value /= _KIB
        return str(size)

    @staticmethod
    def _format_mtime(ts):
        """Формат даты как в ls -l: Mon DD HH:MM."""
        dt = datetime.fromtimestamp(ts)
        return f"{dt.strftime('%b')} {dt.day:2d} {dt.strftime('%H:%M')}"

    def _ls_print_entry(self, display, path, long_fmt, human):
        """Печать одной записи ls. -l: права, владелец, размер, имя."""
        if not long_fmt:
            print(display)
            return
        is_dir = self.vfs.is_dir(path)
        mode = "drwxr-xr-x" if is_dir else "-rw-r--r--"
        try:
            size = self.vfs.size_of(path)
            mtime = self.vfs.mtime_of(path)
        except VFSError:
            size = 0
            mtime = 0
        size_s = self._human_size(size) if human else str(size)
        date_s = self._format_mtime(mtime)
        print(
            f"{mode}  1 {self.user:<5} {self.user:<5} "
            f"{size_s:>6} {date_s} {display}"
        )

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

    def cmd_cat(self, args):
        """Вывести содержимое файла(ов). cat FILE..."""
        if not args:
            print("cat: missing file operand")
            return False
        ok = True
        for path in args:
            if not self._cat_one(path):
                ok = False
        return ok

    def _cat_one(self, path):
        """Печать одного файла без лишнего перевода строки в конце."""
        try:
            text = self.vfs.read_text(path)
        except VFSError as e:
            print(f"cat: {e}")
            return False
        print(text, end="" if text.endswith("\n") else "\n")
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
        """Уникальные подряд идущие строки файла. uniq [-c] FILE"""
        parsed = self._uniq_parse_args(args)
        if parsed is None:
            return False
        count, filename = parsed
        try:
            text = self.vfs.read_text(filename)
        except VFSError as e:
            print(f"uniq: {e}")
            return False
        self._uniq_print(text.splitlines(), count)
        return True

    @staticmethod
    def _uniq_parse_args(args):
        """Разобрать uniq. None при ошибке аргументов."""
        count = False
        files = []
        for arg in args:
            if arg == "-c":
                count = True
            elif arg.startswith("-"):
                print(f"uniq: invalid option -- '{arg}'")
                return None
            else:
                files.append(arg)
        if len(files) != 1:
            print("uniq: expected exactly one file")
            return None
        return count, files[0]

    def _uniq_print(self, lines, count):
        """Схлопнуть подряд идущие одинаковые строки и напечатать."""
        prev = None
        n = 0
        for line in lines:
            if prev is None:
                prev, n = line, 1
            elif line == prev:
                n += 1
            else:
                self._uniq_emit(prev, n, count)
                prev, n = line, 1
        if prev is not None:
            self._uniq_emit(prev, n, count)

    @staticmethod
    def _uniq_emit(line, n, count):
        """Печать строки uniq, с счётчиком при -c."""
        if count:
            print(f"{n:4d} {line}")
        else:
            print(line)

    def cmd_touch(self, args):
        """Создать пустой файл или обновить существующий. touch FILE..."""
        if not args:
            print("touch: missing file operand")
            return False
        ok = True
        for path in args:
            if not self._touch_one(path):
                ok = False
        return ok

    def _touch_one(self, path):
        """Создать файл или обновить mtime существующего."""
        try:
            self.vfs.touch(path)
        except VFSError as e:
            print(f"touch: {e}")
            return False
        return True

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
            "cat": self.cmd_cat,
            "du": self.cmd_du,
            "uniq": self.cmd_uniq,
            "touch": self.cmd_touch,
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
