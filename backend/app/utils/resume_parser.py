from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith('.pdf'):
        return _extract_pdf(content)
    if lower.endswith('.docx'):
        return _extract_docx(content)
    raise ValueError('Unsupported file type. Only PDF/DOCX are allowed.')


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    return '\n'.join((page.extract_text() or '') for page in reader.pages).strip()


def _extract_docx(content: bytes) -> str:
    doc = Document(BytesIO(content))
    return '\n'.join(p.text for p in doc.paragraphs).strip()
