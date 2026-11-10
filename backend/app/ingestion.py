import io
import re
from pathlib import Path
from docx import Document as DocxDocument
from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_pages(content: bytes, extension: str) -> list[tuple[int | None, str]]:
    if extension == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        return [(index + 1, page.extract_text() or "") for index, page in enumerate(reader.pages)]
    if extension == ".docx":
        document = DocxDocument(io.BytesIO(content))
        return [(None, "\n".join(paragraph.text for paragraph in document.paragraphs))]
    return [(None, content.decode("utf-8", errors="replace"))]


def normalize(text: str) -> str:
    return re.sub(r"[ \t]+", " ", re.sub(r"\r\n?", "\n", text)).strip()


def chunk_pages(pages: list[tuple[int | None, str]], size: int = 1200, overlap: int = 150) -> list[dict]:
    chunks: list[dict] = []
    boundary = re.compile(r"(?=^(?:REQ[-_ ][A-Z0-9-]+|\d+(?:\.\d+)+)[:.\s])", re.MULTILINE)
    for page_number, raw in pages:
        text = normalize(raw)
        sections = [part.strip() for part in boundary.split(text) if part.strip()] or [text]
        for section in sections:
            start = 0
            while start < len(section):
                end = min(start + size, len(section))
                if end < len(section):
                    break_at = section.rfind("\n", start, end)
                    if break_at > start + size // 2: end = break_at
                value = section[start:end].strip()
                if value: chunks.append({"text": value, "page_number": page_number})
                if end >= len(section): break
                start = max(end - overlap, start + 1)
    return chunks


def safe_upload_path(upload_dir: str, stored_name: str) -> Path:
    root = Path(upload_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = (root / stored_name).resolve()
    if root not in target.parents: raise ValueError("Unsafe upload path")
    return target

