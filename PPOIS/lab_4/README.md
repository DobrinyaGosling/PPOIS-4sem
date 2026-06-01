# Виртуальная кафедра (FastAPI, Python, MVC)

HTTP API для организации обучения в виртуальной среде: студенты/преподаватели, материалы, задания и сдачи, тестирование, форум, онлайн-лекции.

Состояние сохраняется между запусками в JSON-файл.

## Архитектура

- `src/model/` — доменные сущности и логика + ошибки + хранилище состояния
- `src/view/use_cases/` — use-cases (операции над моделью)
- `src/controller/` — HTTP слой (FastAPI)
  - `src/controller/app.py` — создание FastAPI приложения
  - `src/controller/api/routes.py` — роуты (`/api/v1/...`)

## Настройки (settings.py / .env)

Настройки читаются из переменных окружения и файла `.env` (см. `src/settings.py`).

Путь к файлу состояния:

- `DATA_DIR` (по умолчанию `data`)
- `STATE_FILE` (по умолчанию `state.json`, если относительный — считается относительно `DATA_DIR`)

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск API

```bash
source .venv/bin/activate
uvicorn src.controller.app:app --reload
```

По умолчанию API доступен по адресу `http://127.0.0.1:8000`, Swagger UI: `http://127.0.0.1:8000/docs`.

## Примеры запросов

Базовый префикс: `/api/v1`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/students \
  -H 'Content-Type: application/json' \
  -d '{"login":"ivan","name":"Ivan"}'

curl http://127.0.0.1:8000/api/v1/materials

curl -X POST http://127.0.0.1:8000/api/v1/tests \
  -H 'Content-Type: application/json' \
  -d '{"title":"Quiz","questions":[{"prompt":"2+2?","options":["3","4"],"correct_index":1}]}'
```

## Тесты и покрытие

```bash
source .venv/bin/activate
pytest
```

Требование: `--cov-fail-under=95` задано в `pytest.ini`.
