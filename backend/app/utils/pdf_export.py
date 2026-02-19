from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def text_to_pdf_bytes(text: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 760
    for line in text.split('\n'):
        if y < 50:
            c.showPage()
            y = 760
        c.drawString(40, y, line[:110])
        y -= 16
    c.save()
    return buffer.getvalue()
