#!/usr/bin/env python3
"""Convert a LIBRUS Synergia grades PDF ("Oceny ucznia") into a CSV file.

Usage:
    python pdf_to_csv.py "LIBRUS Synergia.pdf"                  # -> LIBRUS Synergia.csv
    python pdf_to_csv.py input.pdf -o oceny.csv --sep ";"         # semicolons for Polish Excel

Requires:  pip install pdfplumber pandas

How it works: pdfplumber finds the ruled grades table on every page. Each
full-width table row is one subject, and every word inside that row is put
into a column by its x position. Column borders are read from the table
header on the first page, so grades that wrap onto several lines (or a
subject name split over two lines) still end up in the right cell.

The grade columns are then cleaned so they hold only real grades (1-6,
optionally with + or -, e.g. "4+"):
  - a corrected grade "[ old new ]" keeps only the newest grade: "[ - 6 ]" -> "6"
  - everything else is dropped: np, nb, bz, T, lone "+" / "-" marks, ...
Cells with nothing in them ("Brak ocen", "-") are left empty in the CSV.
"""

import argparse
import re
from pathlib import Path

import pandas as pd

COLUMNS = [
    "Przedmiot",
    "Okres 1 - Oceny bieżące",
    "Śr.I",
    "I",
    "Okres 2 - Oceny bieżące",
    "Śr.II",
    "II",
    "Śr.R",
    "R",
]
GRADE_COLUMNS = ["Okres 1 - Oceny bieżące", "Okres 2 - Oceny bieżące"]
LINE_TOLERANCE = 3  # points; words closer than this vertically are one text line
GRADE = re.compile(r"^[1-6][+-]?$")  # 1..6, optionally "4+" / "5-"
EMPTY_MARKERS = ["Brak ocen", "-"]  # Librus placeholders for "nothing here"


def clean_grades(text):
    """Keep only real grades; from a corrected group "[ old new ]" keep the newest.

    "[ - 1 ] 5 nb +"  ->  "1 5"
    """
    if not text:
        return text
    # Put spaces around brackets so "[1" or "6]" split into separate tokens.
    tokens = text.replace("[", " [ ").replace("]", " ] ").split()
    kept, group = [], None
    for tok in tokens:
        if tok == "[":
            group = []
        elif tok == "]":
            if group:
                kept.append(group[-1])  # the last grade in the group is the correction
            group = None
        elif GRADE.match(tok):
            (group if group is not None else kept).append(tok)
        # anything else (np, nb, bz, T, +, -, ...) is skipped
    return " ".join(kept)


def full_width_rows(table):
    """Rows that start at the table's left edge, i.e. one row per subject."""
    left = table.bbox[0]
    return [r for r in table.rows if abs(r.bbox[0] - left) < 1]


class LayoutError(ValueError):
    """The PDF does not look like a Librus "Oceny ucznia" export."""


def find_column_edges(table, words):
    """Left x of each column (+ the table's right edge).

    1st choice: a table row whose ruling lines give exactly 9 cells.
    Fallback:   the header labels (Przedmiot, Śr.I, I, Śr.II, II, Śr.R, R),
                for exports where the lines are drawn differently.
    """
    for row in full_width_rows(table):
        xs = [c[0] for c in row.cells if c is not None]
        if len(xs) == len(COLUMNS):
            return xs + [row.bbox[2]]

    left, top, right, _ = table.bbox
    header = [w for w in words if top <= w["top"] < top + 70 and left <= w["x0"] <= right]
    by_text = {}
    for w in sorted(header, key=lambda w: w["x0"]):
        by_text.setdefault(w["text"], []).append(w)
    needed = ["Przedmiot", "Śr.I", "I", "Śr.II", "II", "Śr.R", "R"]
    if not all(t in by_text for t in needed) or len(by_text.get("Oceny", [])) < 2:
        return None
    first_grades, second_grades = by_text["Oceny"][:2]
    labels = [by_text["Przedmiot"][0], first_grades, by_text["Śr.I"][0], by_text["I"][0],
              second_grades, by_text["Śr.II"][0], by_text["II"][0], by_text["Śr.R"][0],
              by_text["R"][0]]
    # Short labels (Śr.I, I, ...) sit at the start of their narrow column, so the
    # border is just before them (or just after one, if the next column is wide).
    # Between the two wide centred labels the border is halfway.
    short = set(needed[1:])
    edges = [left]
    for a, b in zip(labels, labels[1:]):
        if b["text"] in short:
            edges.append(b["x0"] - 3)
        elif a["text"] in short:
            edges.append(a["x1"] + 3)
        else:
            edges.append((a["x1"] + b["x0"]) / 2)
    return edges + [right]


def join_words(words):
    """Join words in reading order: top to bottom, then left to right."""
    words = sorted(words, key=lambda w: (w["top"], w["x0"]))
    lines, current, line_top = [], [], None
    for w in words:
        if line_top is not None and w["top"] - line_top > LINE_TOLERANCE:
            lines.append(current)
            current = []
        if not current:
            line_top = w["top"]
        current.append(w)
    if current:
        lines.append(current)
    return " ".join(w["text"] for line in lines for w in sorted(line, key=lambda w: w["x0"]))


def column_of(x, edges):
    for i in range(len(edges) - 1):
        if edges[i] <= x < edges[i + 1]:
            return i
    return None


def extract_grades(pdf_path):
    """Read the raw grades table (one row per subject, text as printed)."""
    import pdfplumber  # only needed here, so the helpers above import without it

    records, edges, any_text = [], None, False
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            any_text = any_text or bool(words)
            tables = page.find_tables()
            if not tables:
                continue
            table = tables[0]  # the grades table is the first one on each page
            edges = find_column_edges(table, words) or edges
            if edges is None:
                raise LayoutError(
                    "Could not find the grades table columns (Przedmiot, Oceny bieżące, "
                    "Śr.I, I, ...). Is this the Librus 'Oceny ucznia' page saved as PDF?"
                )

            for row in full_width_rows(table):
                top, bottom = row.bbox[1], row.bbox[3]
                cells = [[] for _ in COLUMNS]
                for w in words:
                    y_mid = (w["top"] + w["bottom"]) / 2
                    if not top <= y_mid < bottom:
                        continue
                    col = column_of((w["x0"] + w["x1"]) / 2, edges)
                    if col is not None:
                        cells[col].append(w)
                values = [join_words(c) for c in cells]

                subject = values[0]
                # Skip the header row and the empty/notes rows under the table.
                if not subject or subject.startswith("Przedmiot"):
                    continue
                records.append(dict(zip(COLUMNS, values)))
                if subject == "Zachowanie":  # last row of the grades table
                    return pd.DataFrame(records, columns=COLUMNS)

    if not any_text:
        raise LayoutError(
            "The PDF has no text (scanned or image-only?). Type the grades into a CSV "
            "by hand instead - see the project briefing, step 2."
        )
    if not records:
        raise LayoutError("No subjects found in the PDF. Is this a Librus grades export?")
    return pd.DataFrame(records, columns=COLUMNS)


def read_librus_pdf(pdf_path):
    """PDF -> cleaned table: one row per subject, grade columns hold only 1-6 grades."""
    df = extract_grades(pdf_path)
    for col in GRADE_COLUMNS:
        df[col] = df[col].map(clean_grades)  # "Brak ocen" has no grades -> ""
    # Placeholders like "Brak ocen" or "-" become empty cells, same as blank ones.
    return df.replace(EMPTY_MARKERS + [""], pd.NA)


def main():
    parser = argparse.ArgumentParser(description="Convert a LIBRUS Synergia grades PDF to CSV.")
    parser.add_argument("pdf", type=Path, help="input PDF file")
    parser.add_argument("-o", "--output", type=Path, help="output CSV (default: same name as the PDF)")
    parser.add_argument("--sep", default=",", help='column separator, e.g. ";" for Polish Excel (default: ",")')
    args = parser.parse_args()

    try:
        df = read_librus_pdf(args.pdf)
    except LayoutError as err:
        raise SystemExit(f"Error: {err}")

    output = args.output or args.pdf.with_suffix(".csv")
    # utf-8-sig adds a BOM so Excel shows Polish letters (ą, ę, ł...) correctly.
    df.to_csv(output, index=False, sep=args.sep, encoding="utf-8-sig")
    print(f"Saved {len(df)} subjects to {output}")
    print(df.fillna("").to_string(index=False, max_colwidth=40))


if __name__ == "__main__":
    main()
