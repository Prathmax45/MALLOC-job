"""PDF text extraction helpers."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from io import BytesIO
from typing import Callable


@dataclass
class PdfExtractionResult:
    text: str
    engine: str
    quality: str
    score: int
    page_count: int
    warnings: list[str]
    candidates: list[dict[str, int | str]]

    def to_dict(self) -> dict:
        return asdict(self)


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Backward-compatible text-only PDF extraction."""

    return extract_pdf(pdf_bytes).text


def extract_pdf(pdf_bytes: bytes) -> PdfExtractionResult:
    """Extract resume text using multiple engines and choose the best result.

    Resume PDFs often use columns, tables, icon fonts, and visual section
    layouts. No single parser wins for every file, so this function compares
    PyMuPDF, pdfplumber, and pypdf when available.
    """

    extractors: list[tuple[str, Callable[[bytes], tuple[str, int]]]] = [
        ("pymupdf-blocks", _extract_with_pymupdf_blocks),
        ("pymupdf-text", _extract_with_pymupdf_text),
        ("pdfplumber-layout", _extract_with_pdfplumber),
        ("pypdf", _extract_with_pypdf),
    ]

    candidates = []
    warnings = []
    page_count = 0

    for engine, extractor in extractors:
        try:
            raw_text, pages = extractor(pdf_bytes)
            page_count = max(page_count, pages)
            cleaned = clean_resume_text(raw_text)
            score = _quality_score(cleaned)
            candidates.append(
                {
                    "engine": engine,
                    "text": cleaned,
                    "score": score,
                    "characters": len(cleaned),
                    "words": len(cleaned.split()),
                }
            )
        except ImportError as exc:
            warnings.append(f"{engine} unavailable: {exc}")
        except Exception as exc:
            warnings.append(f"{engine} failed: {exc}")

    usable = [candidate for candidate in candidates if candidate["text"]]
    
    # If no text was found, or the highest score is suspiciously low (likely a scanned image), attempt OCR.
    best_score = max([c["score"] for c in usable], default=0)
    if not usable or best_score < 15:
        try:
            from pdf2image import convert_from_bytes
            import pytesseract
            images = convert_from_bytes(pdf_bytes)
            ocr_text = "\n".join([pytesseract.image_to_string(img) for img in images])
            
            cleaned_ocr = clean_resume_text(ocr_text)
            ocr_score = _quality_score(cleaned_ocr)
            if ocr_score > best_score:
                candidates.append({
                    "engine": "ocr-fallback",
                    "text": cleaned_ocr,
                    "score": ocr_score,
                    "characters": len(cleaned_ocr),
                    "words": len(cleaned_ocr.split()),
                })
                page_count = max(page_count, len(images))
                usable = [candidate for candidate in candidates if candidate["text"]]
        except ImportError as exc:
            warnings.append(f"OCR dependencies missing (pdf2image/pytesseract): {exc}")
        except Exception as exc:
            warnings.append(f"OCR extraction failed (requires Tesseract/Poppler on system): {exc}")

    if not usable:
        raise ValueError(
            "Could not extract readable text from this PDF. It may be scanned/image-based, locked, or exported with broken text encoding."
        )

    best = max(usable, key=lambda item: (int(item["score"]), int(item["words"]), int(item["characters"])))
    quality = _quality_label(int(best["score"]), int(best["words"]))
    result_warnings = _result_warnings(str(best["text"]), quality)
    result_warnings.extend(warnings[:3])

    return PdfExtractionResult(
        text=str(best["text"]),
        engine=str(best["engine"]),
        quality=quality,
        score=int(best["score"]),
        page_count=page_count,
        warnings=result_warnings,
        candidates=[
            {
                "engine": str(candidate["engine"]),
                "score": int(candidate["score"]),
                "characters": int(candidate["characters"]),
                "words": int(candidate["words"]),
            }
            for candidate in sorted(usable, key=lambda item: int(item["score"]), reverse=True)
        ],
    )


def clean_resume_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = text.replace("\uf0b7", "-")
    text = text.replace("\u2022", "-")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = _join_broken_words(text)
    text = _restore_section_breaks(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_with_pymupdf_blocks(pdf_bytes: bytes) -> tuple[str, int]:
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        blocks = page.get_text("blocks", sort=True)
        lines = []
        for block in blocks:
            if len(block) >= 5:
                value = str(block[4]).strip()
                if value:
                    lines.append(value)
        pages.append("\n".join(lines))
    return "\n\n".join(pages), doc.page_count


def _extract_with_pymupdf_text(pdf_bytes: bytes) -> tuple[str, int]:
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n\n".join(page.get_text("text", sort=True) for page in doc), doc.page_count


def _extract_with_pdfplumber(pdf_bytes: bytes) -> tuple[str, int]:
    import pdfplumber

    pages = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text(layout=True, x_tolerance=1, y_tolerance=3) or ""
            pages.append(text)
        return "\n\n".join(pages), len(pdf.pages)


def _extract_with_pypdf(pdf_bytes: bytes) -> tuple[str, int]:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages), len(reader.pages)


def _quality_score(text: str) -> int:
    if not text:
        return 0

    words = re.findall(r"[A-Za-z][A-Za-z+#.\-]{1,}", text)
    word_count = len(words)
    unique_words = len(set(word.lower() for word in words))
    section_hits = sum(
        1
        for section in [
            "education",
            "skills",
            "experience",
            "projects",
            "internship",
            "achievements",
            "certifications",
        ]
        if re.search(rf"\b{section}\b", text, flags=re.IGNORECASE)
    )
    technical_hits = sum(
        1
        for term in [
            "c++",
            "python",
            "linux",
            "cuda",
            "gpu",
            "pytorch",
            "project",
            "github",
            "intern",
            "engineer",
            "algorithm",
            "operating systems",
        ]
        if term in text.lower()
    )
    bad_chars = len(re.findall(r"[�□■●◆◇]", text))
    single_char_lines = sum(1 for line in text.splitlines() if len(line.strip()) == 1)

    score = 0
    score += min(35, word_count // 8)
    score += min(15, unique_words // 12)
    score += section_hits * 5
    score += technical_hits * 3
    score -= min(20, bad_chars * 2)
    score -= min(15, single_char_lines)
    return max(0, min(100, score))


def _quality_label(score: int, words: int) -> str:
    if words < 80:
        return "poor"
    if score >= 75:
        return "high"
    if score >= 55:
        return "medium"
    return "low"


def _result_warnings(text: str, quality: str) -> list[str]:
    warnings = []
    words = len(text.split())
    if quality in {"low", "poor"}:
        warnings.append("Extraction quality is low; check the extracted text before trusting the analysis.")
    if words < 120:
        warnings.append("Extracted text is short for a resume; the PDF may be scanned, image-based, or heavily designed.")
    if re.search(r"[�□■●◆◇]", text):
        warnings.append("Some symbols did not decode cleanly; replace icon-heavy resume templates with plain text labels.")
    return warnings


def _join_broken_words(text: str) -> str:
    # Fix common PDF extraction artifact: "P y t h o n" -> "Python".
    def replace(match: re.Match[str]) -> str:
        return match.group(0).replace(" ", "")

    return re.sub(r"\b(?:[A-Za-z]\s){2,}[A-Za-z]\b", replace, text)


def _restore_section_breaks(text: str) -> str:
    sections = [
        "Education",
        "Skills",
        "Technical Skills",
        "Experience",
        "Work Experience",
        "Internship",
        "Projects",
        "Achievements",
        "Certifications",
        "Publications",
    ]
    for section in sections:
        text = re.sub(rf"(?<!\n)\b{re.escape(section)}\b\s*:?", f"\n{section}\n", text, flags=re.IGNORECASE)
    return text
