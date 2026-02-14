# Local RAG Starter (React + FastAPI + pgvector)

Готовый шаблон приложения для вашего собственного RAG:
- **Frontend:** React (Vite)
- **Backend:** Python + FastAPI
- **Хранилище векторов:** PostgreSQL + pgvector (локально в Docker)
- **Поддерживаемые входные данные:**
  - текст из формы
  - файлы `.md`
  - файлы `.pdf`

## 1) Поднимите pgvector (если еще не поднят)

```bash
docker compose -f docker-compose.pgvector.yml up -d
```

## 2) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен на `http://localhost:8000`.

### Основные эндпоинты
- `POST /ingest/text` — сохранить текст
- `POST /ingest/file` — загрузить `.md` / `.pdf`
- `POST /search` — semantic search по сохраненным данным
- `GET /health` — проверка здоровья

## 3) Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Откройте `http://localhost:5173`.

Если backend работает на другом URL, задайте:

```bash
VITE_API_BASE=http://localhost:8000 npm run dev
```

## Как это работает

1. Пользователь отправляет текст или файл через React UI.
2. Backend:
   - парсит контент (`.md` как текст, `.pdf` через `pypdf`),
   - разбивает текст на чанки,
   - строит эмбеддинги (`sentence-transformers`),
   - сохраняет в таблицу `documents` с типом `vector`.
3. `POST /search` строит эмбеддинг запроса и возвращает ближайшие чанки из pgvector.

## Дальше для полноценного RAG

- добавить retrieval+generation endpoint (например, с OpenAI, Ollama, vLLM);
- добавить метаданные документов (tenant/user/source uri);
- добавить re-ranking;
- добавить auth и очереди для крупных PDF.
