import argparse
import re
from pathlib import Path

import pandas as pd
import pdfplumber


SUMMARY_COLUMNS = (
    "Śr.I", "(I)", "I", "Oceny bieżące", "Śr.II", "II", "Śr.R", "R"
)

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

GRADE = re.compile(r"[1-6][+-]?")
AVERAGE = re.compile(r"[1-6](?:[.,]\d+)?")
GRADE_GROUP = re.compile(r"\[([^\]]*)\](?:[1-6](?!\d))?")


def clean_text(text):
    return " ".join((text or "").split())


def grade_tokens(text):
    tokens = re.split(r"[\s,]+", text.strip())
    return [token for token in tokens if GRADE.fullmatch(token)]


def clean_grades(text):
    def last_grade(match):
        grades = grade_tokens(match.group(1))
        return f" {grades[-1]} " if grades else " "

    # Consume the digit attached to a closing bracket, e.g. ]1.
    # A separate grade after a space is kept.
    text = GRADE_GROUP.sub(last_grade, text)
    return " ".join(grade_tokens(text))


def save_csv(path, rows, columns, *, clean_numeric=False):
    df = pd.DataFrame(rows, columns=columns)

    if clean_numeric:
        for column in df.columns:
            if column == "Przedmiot":
                continue

            if column.startswith("Śr."):
                valid = df[column].str.fullmatch(AVERAGE, na=False)
                df[column] = df[column].where(valid, "")
            else:
                df[column] = df[column].map(clean_grades)

    df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
    print(f"Saved {len(df)} rows to {path}")


def convert(pdf_path):
    grades = []
    formative_grades = []
    formative_columns = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.find_tables():
                rows = [
                    [clean_text(cell) for cell in row]
                    for row in table.extract()
                ]

                if not rows or rows[0][0] != "Przedmiot":
                    continue

                if "Ocena kształtująca" in rows[0]:
                    formative_columns = rows[0]
                    formative_grades.extend(row for row in rows[1:] if row[0])
                    continue

                if len(rows) < 2 or "Śr.I" not in rows[1]:
                    continue

                # The PDF can use different column positions on each page.
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

                    # Read all first-period grades, including wrapped lines.
                    layout_row = table.rows[row_index]
                    subject_cell = layout_row.cells[0]
                    if subject_cell is None:
                        continue

                    _, top, _, bottom = layout_row.bbox
                    grade_area = (subject_cell[2], top, grades_right, bottom)
                    current_grades = clean_text(
                        page.crop(grade_area).extract_text()
                    )

                    grades.append([subject, current_grades, *summary])

    if not grades:
        raise SystemExit(
            "No Librus grade table found. Use a PDF exported from the "
            "Librus grade overview, not a scan or screenshot."
        )

    save_csv(
        pdf_path.parent / "oceny.csv",
        grades,
        CSV_COLUMNS,
        clean_numeric=True,
    )

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