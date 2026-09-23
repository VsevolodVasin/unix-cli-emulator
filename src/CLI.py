from VFS import VFS


class CLI:
    """Интерактивная оболочка эмулятора."""

    vfs: VFS = None

    def __init__(self):
        """Создаёт VFS и выставляет пользователя root."""
        self.vfs = VFS()
        self.vfs.activate_directory = "~"
        self.user = "root"

    def run(self):
        """Цикл чтения и разбора команд (exit, ls, cd)."""
        while True:
            prompt = (
                f"{self.user}@{self.vfs.name}:"
                f"{self.vfs.active_directory}$ "
            )
            parsed_name = input(prompt).split(" ")
            command = parsed_name[0]
            args = list(filter(lambda x: x != "", parsed_name[1:]))

            if command == "exit":
                break
            elif command == "ls":
                print(command)
                for arg in args:
                    print(arg)
            elif command == "cd":
                print(command)
                for arg in args:
                    print(arg)
            else:
                print("command not found: " + command)