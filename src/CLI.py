from VFS import VFS


class CLI:
    """Интерактивная оболочка эмулятора."""

    def __init__(self, vfs_path=None, script_path=None):
        """Создаёт VFS и сохраняет параметры запуска."""
        self.vfs = VFS()
        self.vfs.active_directory = "~"
        self.user = "root"
        self.vfs_path = vfs_path
        self.script_path = script_path

    def prompt(self):
        """Строка приглашения оболочки."""
        return (
            f"{self.user}@{self.vfs.name}:"
            f"{self.vfs.active_directory}$ "
        )

    def execute(self, command, args):
        """
        Выполнить одну команду.
        Возвращает True при успехе, False при ошибке.
        """
        if command == "exit":
            return "exit"
        if command == "ls":
            print(command)
            for arg in args:
                print(arg)
            return True
        if command == "cd":
            print(command)
            for arg in args:
                print(arg)
            return True
        print("command not found: " + command)
        return False

    def handle_line(self, line):
        """Разобрать и выполнить строку ввода."""
        line = line.strip()
        if not line or line.startswith("#"):
            return True

        parts = line.split(" ")
        command = parts[0]
        args = [x for x in parts[1:] if x != ""]
        return self.execute(command, args)

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
            line = raw.rstrip("\n")
            stripped = line.strip()
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
                line = input(self.prompt())
            except EOFError:
                print()
                break
            result = self.handle_line(line)
            if result == "exit":
                break

    def run(self):
        """Запуск: сначала скрипт (если задан), затем REPL."""
        if self.script_path:
            self.run_script(self.script_path)
            return
        self.run_repl()
