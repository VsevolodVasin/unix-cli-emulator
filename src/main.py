import argparse
import os
import sys

from CLI import CLI


def parse_args(argv=None):
    """Разбор параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор unix-оболочки (вариант 5)",
    )
    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        default=None,
        help="Путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script",
        dest="script_path",
        default=None,
        help="Путь к стартовому скрипту эмулятора",
    )
    return parser.parse_args(argv)


def print_debug_config(args, cli=None):
    """Отладочный вывод всех заданных параметров."""
    print("=== debug: параметры запуска ===")
    print(f"vfs_path    = {args.vfs_path!r}")
    print(f"script_path = {args.script_path!r}")
    print(f"cwd         = {os.getcwd()!r}")
    print(f"argv        = {sys.argv!r}")
    if cli is not None:
        print(f"vfs.name    = {cli.vfs.name!r}")
        print(f"vfs.cwd     = {cli.vfs.active_directory!r}")
        try:
            root_entries = cli.vfs.list_dir("/")
        except Exception:
            root_entries = []
        print(f"vfs.root    = {root_entries!r}")
    print("================================")


def run(argv=None):
    """Точка входа: разбор аргументов и запуск CLI."""
    args = parse_args(argv)
    cli = CLI(vfs_path=args.vfs_path, script_path=args.script_path)
    print_debug_config(args, cli)
    cli.run()


if __name__ == "__main__":
    run()
