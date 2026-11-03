"""Inspect a Librus grade-export PDF locally and export candidate tables.

This script does not upload or send data anywhere. Extracted CSVs may include
personal information, so keep the private_work folder on your own computer.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a Librus PDF locally and save any tables found as CSV."
    )
    parser.add_argument("pdf_path", help="Path to the PDF exported from Librus")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path).expanduser()
    if not pdf_path.is_file():
        print(f"ERROR: File not found: {pdf_path}", file=sys.stderr)
        return 2
    if pdf_path.suffix.lower() != ".pdf":
        print("ERROR: The input file must have a .pdf extension.", file=sys.stderr)
        return 2

    try:
        import pdfplumber
    except ImportError:
        print("Missing dependency. Run: python -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    output_dir = Path("private_work")
    output_dir.mkdir(exist_ok=True)
    found_tables = 0
    all_text_found = False

    print("Librus PDF Inspector — local processing only")
    print("Do not share the PDF or files created in private_work.\n")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Pages found: {len(pdf.pages)}")
            for page_number, page in enumerate(pdf.pages, start=1):
                print(f"\n{'=' * 20} PAGE {page_number} {'=' * 20}")
                page_text = page.extract_text() or ""
                if page_text.strip():
                    all_text_found = True
                    print("Extracted text preview:")
                    print(page_text[:3000])
                    if len(page_text) > 3000:
                        print("[Preview shortened. The full text was not saved.] ")
                else:
                    print("No selectable text was detected on this page.")

                try:
                    tables = page.extract_tables() or []
                except Exception as exc:
                    print(f"Table extraction failed on this page: {exc}")
                    tables = []

                if not tables:
                    print("No table was detected on this page.")
                    continue

                for table_number, table in enumerate(tables, start=1):
                    cleaned_rows = [
                        [(cell or "").replace("\n", " ").strip() for cell in row]
                        for row in table if row and any((cell or "").strip() for cell in row)
                    ]
                    if not cleaned_rows:
                        continue
                    output_path = output_dir / f"pdf_table_page_{page_number:03d}_table_{table_number:02d}.csv"
                    with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerows(cleaned_rows)
                    found_tables += 1
                    print(f"Saved candidate table ({len(cleaned_rows)} rows): {output_path}")
    except Exception as exc:
        print(f"ERROR: Could not read this PDF: {exc}", file=sys.stderr)
        return 1

    print("\nInspection complete.")
    if not all_text_found and found_tables == 0:
        print("No text or tables were detected. The PDF may be scanned or use an unsupported layout.")
        print("For this classroom task, manually enter selected grade records into grades.csv.")
    elif found_tables == 0:
        print("Text was extracted, but no tables were detected. Inspect the preview and create grades.csv manually.")
    else:
        print("Check every saved table before using it. Column alignment is not guaranteed.")
        print("Create a clean grades.csv with columns: date,subject,grade,description")
    print("The script does not create a cleaned grades.csv automatically because each PDF layout may differ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
