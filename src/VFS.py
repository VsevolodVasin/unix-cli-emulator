class VFS:
    """Виртуальная файловая система эмулятора."""

    def __init__(self):
        """Инициализация VFS с именем и домашним каталогом."""
        self.name = "Emulator"
        self.active_directory = "~"
