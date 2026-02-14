from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from .config import settings
from .db import get_conn, init_db
from .embedding import get_embedding_service
from .parser import chunk_text, parse_markdown, parse_pdf

app = FastAPI(title=settings.app_name)


class TextIngestRequest(BaseModel):
    source_name: str = "manual_input"
    text: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest/text")
def ingest_text(payload: TextIngestRequest) -> dict[str, int | str]:
    chunks = chunk_text(payload.text, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=400, detail="Пустой текст после очистки")

    vectors = get_embedding_service().encode(chunks)
    with get_conn() as conn:
        with conn.cursor() as cur:
            for chunk, vector in zip(chunks, vectors, strict=True):
                cur.execute(
                    """
                    INSERT INTO documents (source_name, source_type, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (payload.source_name, "text", chunk, vector),
                )
    return {"status": "stored", "chunks": len(chunks)}


@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)) -> dict[str, int | str]:
    raw = await file.read()
    filename = file.filename or "unknown"
    lower = filename.lower()

    if lower.endswith(".md"):
        parsed = parse_markdown(raw)
        source_type = "markdown"
    elif lower.endswith(".pdf"):
        parsed = parse_pdf(raw)
        source_type = "pdf"
    else:
        raise HTTPException(status_code=400, detail="Поддерживаются только .md и .pdf")

    chunks = chunk_text(parsed, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=400, detail="Не удалось извлечь текст")

    vectors = get_embedding_service().encode(chunks)
    with get_conn() as conn:
        with conn.cursor() as cur:
            for chunk, vector in zip(chunks, vectors, strict=True):
                cur.execute(
                    """
                    INSERT INTO documents (source_name, source_type, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (filename, source_type, chunk, vector),
                )
    return {"status": "stored", "chunks": len(chunks)}


@app.post("/search")
def search(payload: SearchRequest) -> dict[str, list[dict[str, str | float]]]:
    vector = get_embedding_service().encode([payload.query])[0]
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT source_name, source_type, content, 1 - (embedding <=> %s::vector) AS score
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vector, vector, payload.limit),
            )
            rows = cur.fetchall()

    return {
        "results": [
            {
                "source_name": row[0],
                "source_type": row[1],
                "content": row[2],
                "score": float(row[3]),
            }
            for row in rows
        ]
    }
