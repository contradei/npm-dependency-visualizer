# Граф зависимостей npm

Практическая работа 2, вариант 9. Python 3.12+, Windows/PyCharm.
Этап 3: рекурсивный DFS строит граф транзитивных зависимостей.
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

На этапе 3 параметры визуализации только проверяются; на экран выводятся рёбра.
Фильтр, совпадающий с корнем, отвергается. Выход не может затереть тестовый вход.
Ошибки параметров печатаются в stderr, код завершения 2.
Примеры ошибок: `--max-depth -1`, `--output a.png`, `--ascii false`,
`--repository ftp://host`, отсутствующий файл с `--test-mode`.

## Функции

`config.parse_args` разбирает семь опций, `depth_value` проверяет глубину,
`validate_repository` проверяет источник, `validate_settings` — остальные поля.
`main.main` выводит рёбра графа; `NpmRepository.dependencies` получает
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

## Тестовые графы и обход

JSON — объект вида `{"A": ["B"], "B": []}`. Все вершины должны быть объявлены,
имена содержат только A-Z. Неверный JSON и неизвестные ссылки дают ошибку.

```console
run.bat --package A --test-mode --repository examples/chain.json --max-depth 2
run.bat --package A --test-mode --repository examples/diamond.json --max-depth 3
run.bat --package A --test-mode --repository examples/cycle.json
run.bat --package A --test-mode --repository examples/chain.json --exclude B
run.bat --package A --test-mode --repository examples/empty.json
```

Ожидается: цепочка до C; ромб с достижимым F; цикл с ребром C -> A;
после исключения B — только A; для пустого графа зависимостей — только A.
`TestRepository` читает JSON, `validate_nodes` проверяет весь документ.
`build_graph` использует именно рекурсивный DFS; `graph_lines` выводит рёбра.
Граничные вершины включаются без запроса их зависимостей.
Повторное посещение на меньшей глубине расширяет оставшийся бюджет обхода.
Это важно для ромба: результат не зависит от первого, более длинного пути.
Циклические рёбра сохраняются, повторный обход не зацикливается.
Фильтр удаляет совпадающие вершины и пути через них; сравнение регистрозависимое.
