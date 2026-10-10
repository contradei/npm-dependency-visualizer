# Граф зависимостей npm

Практическая работа 2, вариант 9. Python 3.12+, Windows/PyCharm.
Этап 2: CLI выводит прямые зависимости последнего релиза npm-пакета.
Внешних Python-зависимостей нет; сборка не требуется.

## Запуск и тесты

```console
python -m venv .venv
run.bat --package is-odd
.venv\Scripts\python -m unittest discover -s tests -v
```

В PyCharm откройте папку проекта и выберите `.venv\Scripts\python.exe`.
Модуль для запуска: `src.npm_graph.main`, параметры: `--package is-odd`.
Рабочая папка — корень проекта.

## Настройки

| Опция | Значение |
| --- | --- |
| `--package` | Обязательное имя npm; в тестовом режиме — большие латинские буквы |
| `--repository` | URL реестра; по умолчанию `https://registry.npmjs.org` |
| `--test-mode` | Читать локальный файл вместо URL; флаг без значения |
| `--output` | Имя SVG, по умолчанию `graph.svg`; родительская папка должна существовать |
| `--ascii` | Показать ASCII-дерево; флаг без значения |
| `--max-depth` | Глубина 0..200, по умолчанию 5; корень имеет глубину 0 |
| `--exclude` | Регистрозависимая подстрока исключения, по умолчанию пустая |

На этапе 2 визуализация и параметры обхода только проверяются.
Тестовый режим будет реализован на этапе 3; сейчас он сообщает об этом ошибкой.
Фильтр, совпадающий с корнем, отвергается. Выход не может затереть тестовый вход.
Ошибки параметров печатаются в stderr, код завершения 2.
Примеры ошибок: `--max-depth -1`, `--output a.png`, `--ascii false`,
`--repository ftp://host`, отсутствующий файл с `--test-mode`.

## Функции

`config.parse_args` разбирает семь опций, `depth_value` проверяет глубину,
`validate_repository` проверяет источник, `validate_settings` — остальные поля.
`main.main` выводит прямые зависимости; `NpmRepository.dependencies` получает
`GET /<package>/latest` стандартными `urllib` и `json`, кодируя scoped-имена.
`extract_dependencies` проверяет структуру метаданных. Повторные запросы кешируются.
Ошибки HTTP, тайм-ауты и неверный JSON дают сообщение в stderr и код 1.
Показывается поле `dependencies`, без `devDependencies` и `peerDependencies`.
Это граф имён последних релизов: диапазоны версий сохраняются как декларации,
но приложение не выполняет npm-разрешение версий и установку пакетов.

```console
run.bat --package is-odd
run.bat --package is-even
run.bat --package ansi-styles
```

Формат данных: https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md
