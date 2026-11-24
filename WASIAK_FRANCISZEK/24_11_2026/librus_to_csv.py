import argparse
from pathlib import Path

import pandas as pd
import pdfplumber


SUMMARY_COLUMNS = ("Śr.I", "(I)", "I", "Oceny bieżące", "Śr.II", "II", "Śr.R", "R")

CSV_COLUMNS = (
    "Przedmiot",
    "Oceny bieżące – okres 1",
    "Śr.I",
    "(I)",
    "I",
    "Oceny bieżące – okres 2",
    "Śr.II",
    "II",
    "Śr.R",
    "R",
)


def clean(text):
    return " ".join((text or "").split())


def save_csv(path, rows, columns):
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
    print(f"Saved {len(df)} rows to {path}")


def convert(pdf_path):
    grades = []
    formative_grades = []
    formative_columns = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.find_tables():
                rows = [[clean(cell) for cell in row] for row in table.extract()]

                if not rows or rows[0][0] != "Przedmiot":
                    continue

                if "Ocena kształtująca" in rows[0]:
                    formative_columns = rows[0]
                    formative_grades.extend(row for row in rows[1:] if row[0])
                    continue

                if len(rows) < 2 or "Śr.I" not in rows[1]:
                    continue

                # Column positions can change between PDF pages.
                headings = rows[1]
                avg_index = headings.index("Śr.I")
                summary_indexes = [
                    headings.index(name, avg_index) for name in SUMMARY_COLUMNS
                ]
                grades_right = table.rows[1].cells[avg_index][0]

                for row_index, row in enumerate(rows[2:], start=2):
                    subject = row[0]
                    if not subject or subject == "Zachowanie":
                        continue

                    summary = [row[i] for i in summary_indexes]
                    if not any(summary[3:]):
                        continue

                    # Read the whole grade area, including text on wrapped lines.
                    layout_row = table.rows[row_index]
                    subject_cell = layout_row.cells[0]
                    if subject_cell is None:
                        continue

                    _, top, _, bottom = layout_row.bbox
                    grade_area = (subject_cell[2], top, grades_right, bottom)
                    current_grades = clean(page.crop(grade_area).extract_text())

                    grades.append([subject, current_grades, *summary])

    if not grades:
        raise SystemExit(
            "No Librus grade table found. Use a PDF exported from the "
            "Librus grade overview, not a scan or screenshot."
        )

    save_csv(pdf_path.parent / "oceny.csv", grades, CSV_COLUMNS)

    if formative_grades:
        save_csv(
            pdf_path.parent / "oceny_ksztaltujace.csv",
            formative_grades,
            formative_columns,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a Librus grade PDF to CSV.")
    parser.add_argument("pdf", type=Path, help="Path to the Librus PDF")
    args = parser.parse_args()

    if not args.pdf.is_file():
        parser.error(f"File not found: {args.pdf}")

    convert(args.pdf)