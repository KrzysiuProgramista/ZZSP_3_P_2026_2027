"""Inspect a PDF locally. Outputs may contain private information."""
import argparse
import csv
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", type=Path)
    args = parser.parse_args()
    path = args.pdf_path.expanduser()
    if not path.is_file() or path.suffix.lower() != ".pdf":
        parser.error("Provide an existing PDF file.")
    output = ROOT / "private_work"
    output.mkdir(exist_ok=True)
    print("Local processing only. Do not share extracted text or tables.")
    count = 0
    try:
        with pdfplumber.open(path) as pdf:
            for number, page in enumerate(pdf.pages, 1):
                print(f"Page {number} text preview:")
                print((page.extract_text() or "No selectable text.")[:3000])
                for index, table in enumerate(page.extract_tables() or [], 1):
                    rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in table if row and any(cell for cell in row)]
                    if not rows:
                        continue
                    target = output / f"page_{number:03d}_table_{index:02d}.csv"
                    with target.open("w", newline="", encoding="utf-8-sig") as handle:
                        csv.writer(handle).writerows(rows)
                    count += 1
                    print("Saved:", target.name)
    except Exception as exc:
        print("PDF inspection failed:", exc)
        return 1
    print(f"Tables saved: {count}. Check alignment manually.")
    print("Create grades.csv locally: date,subject,grade,description")
    print("For scanned/unsupported PDFs, manually enter selected records locally.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
