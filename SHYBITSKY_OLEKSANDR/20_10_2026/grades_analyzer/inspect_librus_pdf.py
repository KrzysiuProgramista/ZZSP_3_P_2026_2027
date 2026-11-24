"""Inspect a Librus grade-export PDF locally and export candidate tables.

Expected format: Przedmiot,Oceny bieżące
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import pandas as pd

REQUIRED_COLUMNS = ["Przedmiot", "Oceny bieżące"]


def extract_librus_grades_from_pdf(pdf_path: str | Path) -> pd.DataFrame:
    """Extract grades from Librus PDF and return a DataFrame with 'Przedmiot' and 'Oceny bieżące'.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file is not a PDF or if the PDF does not contain the required columns.
    """
    path = Path(pdf_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"The input file must have a .pdf extension: {path}")

    try:
        import pdfplumber
    except ImportError as err:
        raise ImportError("Missing pdfplumber dependency. Install it via: pip install pdfplumber") from err

    records = []
    found_required_columns = False

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Check if this table contains the required columns in the header (first 3 rows)
                header_cells = [
                    (cell or "").replace("\n", " ").strip().lower()
                    for row in table[:3]
                    for cell in row
                    if cell
                ]
                has_przedmiot = any("przedmiot" in cell for cell in header_cells)
                has_oceny = any("oceny bieżące" in cell or "oceny biezace" in cell for cell in header_cells)

                if not (has_przedmiot and has_oceny):
                    continue

                found_required_columns = True

                # Determine column index for 'Przedmiot'
                subject_col = 0
                for r in table[:3]:
                    for c_idx, cell in enumerate(r):
                        if cell and "przedmiot" in cell.lower():
                            subject_col = c_idx
                            break

                # Determine starting column index for 'Oceny bieżące'
                grades_start_col = 1
                for r in table[:3]:
                    for c_idx, cell in enumerate(r):
                        if cell and ("oceny bieżące" in cell.lower() or "oceny biezace" in cell.lower()):
                            grades_start_col = c_idx
                            break

                # Determine ending column index (before 'Śr.I' or 'Okres 2')
                grades_end_col = None
                for r in table[:3]:
                    for c_idx, cell in enumerate(r):
                        if cell and ("śr.i" in cell.lower() or "sr.i" in cell.lower() or "okres 2" in cell.lower()):
                            if grades_end_col is None or c_idx < grades_end_col:
                                grades_end_col = c_idx

                if grades_end_col is None:
                    grades_end_col = len(table[0])

                # Data rows start after header rows
                data_start_row = 0
                for idx, r in enumerate(table):
                    cell_val = (r[subject_col] or "").strip().lower()
                    if cell_val and cell_val != "przedmiot":
                        data_start_row = idx
                        break

                current_subject = None
                current_grades = []

                for r in table[data_start_row:]:
                    subj = (r[subject_col] or "").replace("\n", " ").strip()
                    grade_cells = [
                        c.replace("\n", " ").strip()
                        for c in r[grades_start_col:grades_end_col]
                        if c and c.strip()
                    ]

                    if subj:
                        if current_subject:
                            grades_str = " ".join(current_grades) if current_grades else "Brak ocen"
                            records.append({"Przedmiot": current_subject, "Oceny bieżące": grades_str})
                        current_subject = subj
                        current_grades = list(grade_cells)
                    else:
                        # Continuation row (overflow)
                        if grade_cells and current_subject:
                            current_grades.extend(grade_cells)

                if current_subject:
                    grades_str = " ".join(current_grades) if current_grades else "Brak ocen"
                    records.append({"Przedmiot": current_subject, "Oceny bieżące": grades_str})

                if records:
                    break
            if records:
                break

    if not found_required_columns or not records:
        raise ValueError("PDF does not contain required columns: 'Przedmiot', 'Oceny bieżące'")

    return pd.DataFrame(records, columns=REQUIRED_COLUMNS)


def convert_pdf_to_csv(pdf_path: str | Path, output_csv_path: str | Path = "grades.csv") -> Path:
    """Extract grades from Librus PDF and save as CSV with columns: Przedmiot,Oceny bieżące.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file is not a PDF or if the PDF does not contain the required columns.
    """
    df = extract_librus_grades_from_pdf(pdf_path)
    output_path = Path(output_csv_path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a Librus PDF locally and export grades table to CSV (Przedmiot, Oceny bieżące)."
    )
    parser.add_argument("pdf_path", help="Path to the PDF exported from Librus")
    parser.add_argument(
        "-o", "--output",
        default="grades.csv",
        help="Path to output CSV file (default: grades.csv)"
    )
    args = parser.parse_args()

    output_path = convert_pdf_to_csv(args.pdf_path, args.output)
    print(f"Successfully processed PDF to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
