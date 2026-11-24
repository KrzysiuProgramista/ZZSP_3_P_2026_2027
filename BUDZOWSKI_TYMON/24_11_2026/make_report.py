#!/usr/bin/env python3
"""One command: Librus grades PDF -> website with the dashboard.

    python make_report.py "LIBRUS Synergia.pdf"

That is all. It reads the PDF, cleans the grades, runs the analysis and opens
the finished page in your browser. Everything lands in one folder next to
where you run it (default: <pdf name>_report/):

    <pdf name>_report/
        index.html       the website: key numbers, dashboard, tables, alerts
        dashboard.png    the 2x2 dashboard image
        grades.csv       cleaned grades, one row per subject
        grades_raw.csv   one row per grade

The folder holds your private grades, so keep it out of git (it is in .gitignore).

Options:
    -o FOLDER           where to put the files
    --plus 0.5          count "4+" as 4.5   (default: grades with +/- are left out)
    --minus 0.25        count "4-" as 3.75
    --no-open           don't open the browser
    --sep ";"           separator for grades.csv (";" opens nicely in Polish Excel)

Requires: pip install -r requirements.txt   (pdfplumber, pandas, matplotlib)
"""

import argparse
import re
import sys
import webbrowser
from pathlib import Path


def check_requirements():
    missing = []
    for module in ("pdfplumber", "pandas", "matplotlib"):
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        raise SystemExit(
            f"Missing Python packages: {', '.join(missing)}\n"
            f"Install them with:  {Path(sys.executable).name} -m pip install -r requirements.txt"
        )


def default_out_dir(pdf):
    safe = re.sub(r"[^\w-]+", "_", pdf.stem).strip("_") or "grades"
    return Path(f"{safe}_report")


def main():
    parser = argparse.ArgumentParser(
        description="Turn a Librus grades PDF into a dashboard website in one step.")
    parser.add_argument("pdf", type=Path, help="the Librus 'Oceny ucznia' PDF")
    parser.add_argument("-o", "--out-dir", type=Path,
                        help="output folder (default: <pdf name>_report)")
    parser.add_argument("--plus", type=float, help='value added for "+" (e.g. 0.5)')
    parser.add_argument("--minus", type=float, help='value taken for "-" (e.g. 0.25)')
    parser.add_argument("--sep", default=",", help='separator for grades.csv (default ",")')
    parser.add_argument("--no-open", action="store_true", help="don't open the browser")
    args = parser.parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"Error: file not found: {args.pdf}")
    check_requirements()

    # Imported here so a missing package gives the friendly message above.
    from analyse_grades import analyse
    from pdf_to_csv import LayoutError, read_librus_pdf

    out = args.out_dir or default_out_dir(args.pdf)
    out.mkdir(parents=True, exist_ok=True)

    print(f"1/3  Reading {args.pdf.name} ...")
    try:
        wide = read_librus_pdf(args.pdf)
    except LayoutError as err:
        raise SystemExit(f"Error: {err}")
    csv_path = out / "grades.csv"
    wide.to_csv(csv_path, index=False, sep=args.sep, encoding="utf-8-sig")
    print(f"     {len(wide)} subjects -> {csv_path}")

    print("2/3  Analysing grades ...\n")
    html_path = out / "index.html"
    try:
        analyse(wide,
                long_path=out / "grades_raw.csv",
                png_path=out / "dashboard.png",
                html_path=html_path,
                plus=args.plus, minus=args.minus)
    except ValueError as err:
        raise SystemExit(f"Error: {err}")

    print(f"\n3/3  Done. Website: {html_path.resolve()}")
    if not args.no_open:
        webbrowser.open(html_path.resolve().as_uri())


if __name__ == "__main__":
    main()
