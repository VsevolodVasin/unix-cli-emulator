# unix-cli-emulator

Вариант 5

Эмулятор unix-оболочки на Python со своей VFS в памяти и интерактивным CLI.
Источник VFS — JSON (бинарные данные в base64). Реальная FS хоста не меняется,
кроме чтения JSON и стартовых скриптов.

## Запуск

```bash
./setup.sh          # один раз: создать .venv
./run.sh            # интерактивный режим
./run.sh --vfs vfs/deep.json --script startups/stage5_touch.txt
```

### Параметры командной строки

| Параметр | Описание |
|----------|----------|
| `--vfs PATH` | Путь к JSON-файлу VFS |
| `--script PATH` | Стартовый скрипт команд эмулятора |

При старте печатается отладочный блок со всеми параметрами и кратким
состоянием загруженной VFS.

Стартовый скрипт выполняется построчно: на экране виден ввод и вывод как в
диалоге; ошибочные строки пропускаются; строки `#` и пустые игнорируются.

## Команды

| Команда | Описание |
|---------|----------|
| `ls [path...]` | Список каталога |
| `cd [path]` | Смена текущего каталога |
| `echo [args...]` | Печать аргументов |
| `du [path...]` | Размер файла/каталога в байтах |
| `uniq [-c] FILE` | Уникальные подряд идущие строки файла |
| `touch FILE...` | Создать пустой файл или «обновить» существующий (в памяти) |
| `exit` | Выход |
| другое | `command not found: ...` |

## Модули

### `main.py`

- `parse_args()` — `--vfs`, `--script`
- `print_debug_config()` — отладочный вывод параметров
- `run()` — точка входа

### `CLI` (`CLI.py`)

Поля: `vfs`, `user` (`root`), `vfs_path`, `script_path`.

Методы: `prompt`, `execute`, `handle_line`, `run_script`, `run_repl`, `run`,
а также `cmd_ls` / `cmd_cd` / `cmd_echo` / `cmd_du` / `cmd_uniq` / `cmd_touch`.

### `VFS` (`VFS.py`)

Дерево в памяти. Поля: `name`, `cwd` / `active_directory`, `root`.

Основные методы: `load`, `resolve`, `list_dir`, `chdir`, `read_file`,
`read_text`, `write_file`, `size_of`, `exists`, `is_dir`, `is_file`.

### Формат VFS (JSON)

```json
{
  "name": "Deep",
  "root": {
    "type": "dir",
    "children": {
      "file.txt": {
        "type": "file",
        "encoding": "text",
        "content": "hello\n"
      },
      "data.bin": {
        "type": "file",
        "encoding": "base64",
        "content": "AQIDBA=="
      }
    }
  }
}
```

Готовые образы: `vfs/minimal.json`, `vfs/multi.json`, `vfs/deep.json` (≥3 уровня).

## Тестовые скрипты ОС

```bash
./scripts/stage2_no_args.sh
./scripts/stage2_vfs.sh
./scripts/stage2_script.sh
./scripts/stage2_all.sh
./scripts/stage3_vfs_minimal.sh
./scripts/stage3_vfs_multi.sh
./scripts/stage3_vfs_deep.sh
./scripts/stage3_startup_all.sh
./scripts/stage4_commands.sh
./scripts/stage4_uniq.sh
./scripts/stage5_touch.sh
```

Стартовые сценарии эмулятора лежат в `startups/`.

## Структура

```
unix-cli-emulator/
├── src/           # main.py, CLI.py, VFS.py
├── vfs/           # JSON-образы VFS
├── startups/      # скрипты команд эмулятора
├── scripts/       # bash-обёртки для прогона тестов
├── setup.sh
├── run.sh
└── README.md
```
