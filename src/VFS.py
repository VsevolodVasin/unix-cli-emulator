import base64
import json


class VFSError(Exception):
    """Ошибка операций над VFS."""


class VFS:
    """Виртуальная файловая система в памяти (источник — JSON)."""

    def __init__(self, path=None):
        """
        Загрузить VFS из JSON или создать пустую.
        Данные держатся только в памяти.
        """
        self.name = "Emulator"
        self.cwd = "/"
        self.root = {"type": "dir", "children": {}}
        if path:
            self.load(path)

    @property
    def active_directory(self):
        """Текущий каталог для промпта."""
        return self.cwd if self.cwd != "/" else "/"

    @active_directory.setter
    def active_directory(self, value):
        self.cwd = value if value else "/"

    def load(self, path):
        """Прочитать JSON с диска и разобрать в дерево в памяти."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.name = data.get("name", "Emulator")
        root = data.get("root")
        if root is None:
            raise VFSError("invalid VFS: missing root")
        self.root = self._normalize_node(root)
        self.cwd = "/"

    def _normalize_node(self, node):
        """Привести узел JSON к внутреннему представлению."""
        if not isinstance(node, dict) or "type" not in node:
            raise VFSError("invalid VFS node")
        ntype = node["type"]
        if ntype == "dir":
            children = {}
            for name, child in node.get("children", {}).items():
                children[name] = self._normalize_node(child)
            return {"type": "dir", "children": children}
        if ntype == "file":
            encoding = node.get("encoding", "text")
            content = node.get("content", "")
            if encoding == "base64":
                raw = base64.b64decode(content)
            else:
                raw = content.encode("utf-8") if isinstance(
                    content, str
                ) else content
            return {"type": "file", "content": raw}
        raise VFSError(f"unknown node type: {ntype}")

    def _split(self, path):
        """Разбить путь на части без пустых сегментов."""
        return [p for p in path.split("/") if p and p != "."]

    def resolve(self, path):
        """Абсолютный путь относительно cwd. Поддержка ~ и .."""
        if path is None or path == "":
            path = self.cwd
        if path.startswith("~"):
            path = "/" + path[1:].lstrip("/")
        if not path.startswith("/"):
            base = self.cwd if self.cwd != "/" else ""
            path = f"{base}/{path}"
        parts = []
        for part in self._split(path):
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return "/" + "/".join(parts) if parts else "/"

    def _walk(self, path):
        """Вернуть узел по абсолютному пути или None."""
        abs_path = self.resolve(path)
        if abs_path == "/":
            return self.root
        node = self.root
        for part in self._split(abs_path):
            if node.get("type") != "dir":
                return None
            node = node.get("children", {}).get(part)
            if node is None:
                return None
        return node

    def exists(self, path):
        """Проверка существования пути."""
        return self._walk(path) is not None

    def is_dir(self, path):
        """Является ли путь каталогом."""
        node = self._walk(path)
        return node is not None and node.get("type") == "dir"

    def is_file(self, path):
        """Является ли путь файлом."""
        node = self._walk(path)
        return node is not None and node.get("type") == "file"

    def list_dir(self, path):
        """Список имён в каталоге."""
        node = self._walk(path)
        if node is None:
            raise VFSError(f"no such file or directory: {path}")
        if node.get("type") != "dir":
            raise VFSError(f"not a directory: {path}")
        return sorted(node.get("children", {}).keys())

    def read_file(self, path):
        """Прочитать содержимое файла (bytes)."""
        node = self._walk(path)
        if node is None:
            raise VFSError(f"no such file or directory: {path}")
        if node.get("type") != "file":
            raise VFSError(f"is a directory: {path}")
        return node["content"]

    def read_text(self, path):
        """Прочитать файл как текст."""
        return self.read_file(path).decode("utf-8", errors="replace")

    def write_file(self, path, content=b""):
        """Создать/перезаписать файл в памяти."""
        abs_path = self.resolve(path)
        if abs_path == "/":
            raise VFSError("cannot write to root")
        parts = self._split(abs_path)
        name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
        parent = self._walk(parent_path)
        if parent is None or parent.get("type") != "dir":
            raise VFSError(
                f"no such file or directory: {parent_path}"
            )
        if isinstance(content, str):
            content = content.encode("utf-8")
        existing = parent["children"].get(name)
        if existing and existing.get("type") == "dir":
            raise VFSError(f"is a directory: {path}")
        parent["children"][name] = {"type": "file", "content": content}

    def chdir(self, path):
        """Сменить текущий каталог."""
        if path is None or path == "":
            path = "/"
        abs_path = self.resolve(path)
        if not self.is_dir(abs_path):
            if not self.exists(abs_path):
                raise VFSError(f"no such file or directory: {path}")
            raise VFSError(f"not a directory: {path}")
        self.cwd = abs_path

    def size_of(self, path):
        """Размер файла или суммарный размер каталога (байты)."""
        node = self._walk(path)
        if node is None:
            raise VFSError(f"no such file or directory: {path}")
        return self._size_node(node)

    def _size_node(self, node):
        if node.get("type") == "file":
            return len(node.get("content", b""))
        total = 0
        for child in node.get("children", {}).values():
            total += self._size_node(child)
        return total
