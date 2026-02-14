from io import BytesIO

from pypdf import PdfReader


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def parse_markdown(raw: bytes) -> str:
    return raw.decode("utf-8", errors="ignore")


def parse_pdf(raw: bytes) -> str:
    reader = PdfReader(BytesIO(raw))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)
