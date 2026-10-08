"""Preserve PyMuPDF text exactly; clauses are slices of original page text."""
import re
from uuid import uuid4

import pymupdf

from app.config import settings
from app.services.analysis_observability import timed
from app.models.contracts import Clause, Contract, PageText


class PDFError(ValueError):
    pass


class ContractLimitError(PDFError):
    pass


def split_clauses(page: PageText) -> list[Clause]:
    # Numbered headings or blank paragraphs provide lightweight MVP boundaries.
    boundaries = [0]
    for match in re.finditer(r"\n[ \t]*\n|(?<=\n)(?=\d{1,3}[.)][ \t]+)", page.text):
        boundaries.append(match.end() if match.group() else match.start())
    boundaries.append(len(page.text))
    clauses = []
    for start, end in zip(boundaries, boundaries[1:]):
        while start < end:
            stop = min(start + 2000, end)
            if stop < end:
                space = page.text.rfind(" ", start + 1000, stop)
                newline = page.text.rfind("\n", start + 1000, stop)
                split = max(space, newline)
                if split > start:
                    stop = split
            raw = page.text[start:stop]
            first = start + len(raw) - len(raw.lstrip())
            last = stop - len(raw) + len(raw.rstrip())
            if first < last:
                clauses.append(Clause(
                    clause_id=f"P{page.page_number:03d}-C{len(clauses) + 1:03d}",
                    page_number=page.page_number, text=page.text[first:last],
                    start_offset=first, end_offset=last,
                ))
            start = stop
    return clauses


@timed("pdf_extraction")
def extract_contract(pdf_bytes: bytes, filename: str) -> Contract:
    if len(pdf_bytes) > settings.max_upload_bytes:
        raise ContractLimitError("PDF exceeds the configured upload size limit.")
    if not pdf_bytes.lstrip().startswith(b"%PDF-"):
        raise PDFError("Upload must be a valid PDF.")
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            if pdf.needs_pass:
                raise PDFError("Password-protected PDFs are not supported.")
            if len(pdf) > settings.max_contract_pages:
                raise ContractLimitError("PDF exceeds the configured page limit.")
            pages = []
            chars = 0
            for index, page in enumerate(pdf):
                text = page.get_text("text", sort=True)
                chars += len(text)
                if chars > settings.max_contract_chars:
                    raise ContractLimitError("Extracted text exceeds the configured analysis limit.")
                pages.append(PageText(page_number=index + 1, text=text))
    except PDFError:
        raise
    except (pymupdf.FileDataError, pymupdf.EmptyFileError, RuntimeError, ValueError) as exc:
        raise PDFError("PDF could not be parsed.") from exc
    if not any(page.text.strip() for page in pages):
        raise PDFError("PDF contains no extractable text. Scanned PDFs require OCR, which is not supported.")
    clauses = [clause for page in pages for clause in split_clauses(page)]
    if len(clauses) > settings.max_contract_clauses:
        raise ContractLimitError("PDF exceeds the configured clause limit.")
    warnings = [f"Page {p.page_number} has no extractable text; its contents were not analyzed." for p in pages if not p.text.strip()]
    return Contract(contract_id=str(uuid4()), filename=filename, pages=pages, clauses=clauses, warnings=warnings)
