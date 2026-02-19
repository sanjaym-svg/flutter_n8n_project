import hashlib
import re


def dedupe_hash(title: str, company: str, location: str, apply_url: str) -> str:
    raw = f'{title}{company}{location}{apply_url}'.lower()
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def sanitize_text(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
