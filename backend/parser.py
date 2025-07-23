# backend/parser.py

import re
from pathlib import Path
from datetime import datetime
from typing import Optional

import pytesseract
# ← point pytesseract at your installed EXE
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import pdf2image
from PIL import Image

from .models import Receipt

# ---- regexps for dates and amounts ----
DATE_PATTERNS = [
    (re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"), ["%d/%m/%Y", "%d-%m-%Y"]),
    (re.compile(r"([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})"), ["%b %d, %Y", "%B %d, %Y"]),
]
AMOUNT_RE = re.compile(r"₹?\s*([0-9]+(?:\.[0-9]{1,2})?)")

def extract_text_from_file(fpath: Path) -> str:
    suffix = fpath.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg"}:
        img = Image.open(fpath)
        return pytesseract.image_to_string(img)
    if suffix == ".pdf":
        pages = pdf2image.convert_from_path(str(fpath), dpi=300)
        return pytesseract.image_to_string(pages[0])
    if suffix == ".txt":
        return fpath.read_text(encoding="utf-8")
    raise ValueError(f"Unsupported file type: {suffix}")

def parse_date(text: str) -> datetime.date:
    for regex, fmts in DATE_PATTERNS:
        m = regex.search(text)
        if not m:
            continue
        for fmt in fmts:
            try:
                return datetime.strptime(m.group(1), fmt).date()
            except ValueError:
                pass
    return datetime.today().date()

def parse_amount(text: str) -> float:
    vals = [float(x) for x in AMOUNT_RE.findall(text)]
    return max(vals) if vals else 0.0

def parse_vendor(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()[:64]
    return "Unknown"

def categorize_vendor(vendor: str) -> str:
    """Very simple keyword-based category assignment."""
    v = vendor.lower()
    if any(kw in v for kw in ("mart", "grocery", "store")):
        return "Groceries"
    if "toll" in v or "road" in v:
        return "Transport"
    if "book" in v or "stationer" in v:
        return "Books"
    # fallback
    return "Uncategorized"

def parse_receipt(fpath: Path) -> Receipt:
    raw    = extract_text_from_file(fpath)
    vendor = parse_vendor(raw)
    date   = parse_date(raw)
    amount = parse_amount(raw)
    category = categorize_vendor(vendor)
    return Receipt(
        vendor=vendor,
        date=date,
        amount=amount,
        category=category
    )
