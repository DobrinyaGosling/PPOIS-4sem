# Модель виртуальной кафедры (CLI, Python, MVC)

CLI-система для организации обучения в виртуальной среде: учебные материалы, задания, тестирование, форум, онлайн-лекции.

## Архитектура (MVC)

- `src/model/` — доменные сущности + сервис + хранение состояния
- `src/view/` — CLI View (только вывод)
- `src/controller/` — контроллер CLI (команды как endpoints: парсинг аргументов + вызов model + вывод через view)

Состояние сохраняется между запусками в JSON-файл.

## Настройки (settings.py / .env)

Настройки читаются из переменных окружения и файла `.env` (см. `settings.py`).

Сохранение состояния:

- `DATA_DIR` (по умолчанию `data`)
- `STATE_FILE` (по умолчанию `state.json`, если относительный — считается относительно `DATA_DIR`)

Шаблон полей для окружения (не обязательно использовать в этой лабораторной):

- `MODE` (`DEV|TEST|PROD`)
- `DB_NAME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` (свойство `database_url`)

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

Все команды запускаются через `python -m src.main ...`

Если запустить без аргументов (`python -m src.main`), включится интерактивный режим (бесконечный цикл).

Чтобы вместо REPL показать справку (например, для CI), установи `VDEPT_NO_REPL=1`.

```bash
python -m src.main create-student --login ivan --name "Ivan Ivanov"
python -m src.main create-teacher --login petrov --name "Dr. Petrov"
python -m src.main add-material --title "Intro" --content "..."
python -m src.main list-materials
```

### Задания

```bash
python -m src.main add-assignment --title "Lab 1" --description "OOP + MVC"
python -m src.main submit-assignment --assignment-id <asg_id> --student-id <stu_id> --answer "my solution"
python -m src.main grade-submission --submission-id <sub_id> --grade 95
```

### Тесты

```bash
python -m src.main create-test --title "Quiz" --questions-json '[{"prompt":"2+2?","options":["3","4"],"correct_index":1}]'
python -m src.main take-test --test-id <tst_id> --student-id <stu_id> --answers-json '[1]'
```

### Форум

```bash
python -m src.main create-thread --title "Q&A"
python -m src.main post --thread-id <thr_id> --author-id <teacher_id> --content "Hello!"
```

### Онлайн-лекции

```bash
python -m src.main schedule-lecture --topic "SOLID"
python -m src.main start-lecture --lecture-id <lec_id>
python -m src.main end-lecture --lecture-id <lec_id>
```

## Диаграммы UML 2.x

PlantUML-исходники:

- `docs/diagrams/class_diagram.puml`
- `docs/diagrams/state_diagram.puml`

## Тесты и покрытие

```bash
pytest
```

Требование: `--cov-fail-under=95` задано в `pytest.ini`.
