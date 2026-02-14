# Upload smoke tests (separate from app code)

Этот каталог содержит отдельный тестовый скрипт для проверки отправки файлов разных форматов в бэкенд.

## Что проверяется
- Отправка `multipart/form-data` для нескольких форматов (`txt`, `json`, `csv`, `png`, `pdf`).
- Возврат успешного HTTP-кода (`2xx`) на каждый файл.

> Важно: скрипт проверяет, что запрос дошёл до API-эндпоинта и получил успешный ответ. Подтверждение сохранения файла в БД/хранилище требует дополнительных проверок логов/БД конкретного бэка.

## Запуск
Из корня репозитория:

```bash
python3 -m pip install requests
python3 tests/upload/test_file_upload.py \
  --base-url http://localhost:8000 \
  --endpoint /upload \
  --field-name file
```

## Настройка под ваш бэкенд
- `--base-url` — базовый URL API.
- `--endpoint` — путь upload-эндпоинта.
- `--field-name` — имя поля файла в multipart (например `file`, `upload`, `document`).
- `--formats` — список форматов через запятую.

Пример:

```bash
python3 tests/upload/test_file_upload.py \
  --base-url http://localhost:8080 \
  --endpoint /api/v1/files/upload \
  --field-name upload \
  --formats txt,json,csv,png,pdf
```
