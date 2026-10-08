"""Generate the synthetic text-only PDF reproducibly with PyMuPDF."""
import json
from pathlib import Path

import pymupdf

FIXTURE = Path(__file__).parent / "fixtures" / "sample_contract.json"


def sample_pdf() -> bytes:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with pymupdf.open() as doc:
        for paragraphs in fixture["pages"]:
            page = doc.new_page(width=595, height=842)
            y = 45
            for paragraph in paragraphs:
                box = pymupdf.Rect(45, y, 550, y + 140)
                remaining = page.insert_textbox(box, paragraph, fontsize=11)
                if remaining < 0:
                    raise RuntimeError("Synthetic PDF paragraph did not fit.")
                y += 140 - remaining + 20
            if y > 810:
                raise RuntimeError("Synthetic PDF exceeded page bounds.")
        return doc.tobytes()


if __name__ == "__main__":
    path = Path(__file__).parent / "fixtures" / "synthetic_supplier_contract.pdf"
    path.write_bytes(sample_pdf())
    print(f"Generated {path.name}")
