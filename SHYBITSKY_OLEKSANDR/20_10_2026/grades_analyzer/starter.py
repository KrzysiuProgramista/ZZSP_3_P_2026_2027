"""Librus Intelligence — student starter code.

Data format: Przedmiot,Oceny bieżące
Analyzes grades, displays averages, and highlights subjects to focus on.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
import pandas as pd

from inspect_librus_pdf import convert_pdf_to_csv

REQUIRED_COLUMNS = {"Przedmiot", "Oceny bieżące"}


def parse_grades(raw_grades: object) -> list[int]:
    """Parse grade string into a list of base numeric grades (1-6).

    Handles spaces, concatenations (e.g. '556'), annotations ('bz', 'np', 'T'),
    and modifiers ('+', '-').
    """
    if raw_grades is None or pd.isna(raw_grades):
        return []
    text = str(raw_grades).strip()
    if text.lower() in ("brak ocen", "-", "none", "nan", "no grades"):
        return []

    # Extract all grade digits 1-6
    digits = re.findall(r"[1-6]", text)
    return [int(d) for d in digits]


def load_grades(path: str | Path = "grades.csv") -> pd.DataFrame:
    """Load grades CSV with columns 'Przedmiot' and 'Oceny bieżące' and calculate metrics."""
    file_path = Path(path).expanduser()
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path, dtype={"Przedmiot": "string", "Oceny bieżące": "string"})

    # Gracefully accept alias from earlier exports if present
    if "Oceny bieżące" not in df.columns and "Oceny bieżące Okres 1" in df.columns:
        df = df.rename(columns={"Oceny bieżące Okres 1": "Oceny bieżące"})

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df["Przedmiot"] = df["Przedmiot"].astype("string").str.strip()
    df["Oceny bieżące"] = df["Oceny bieżące"].fillna("Brak ocen").astype("string").str.strip()

    df["oceny_lista"] = df["Oceny bieżące"].apply(parse_grades)
    df["liczba_ocen"] = df["oceny_lista"].apply(len)
    df["srednia"] = df["oceny_lista"].apply(
        lambda grades: round(sum(grades) / len(grades), 2) if grades else float("nan")
    )

    # Aliases for backward compatibility
    df["subject"] = df["Przedmiot"]
    df["grade_base"] = df["srednia"]

    return df


def subjects_to_focus_on(df: pd.DataFrame, threshold: float = 3.5) -> pd.DataFrame:
    """Return subjects that need focus: average <= threshold or containing grades <= 2."""
    with_grades = df[df["liczba_ocen"] > 0].copy()
    if with_grades.empty:
        return pd.DataFrame()

    has_low_grade = with_grades["oceny_lista"].apply(lambda g: any(grade <= 2 for grade in g))
    low_avg = with_grades["srednia"] <= threshold

    focus_df = with_grades[low_avg | has_low_grade].sort_values(by="srednia", ascending=True)

    # If no subjects meet threshold, return 3 lowest to give informative feedback
    if focus_df.empty:
        return with_grades.sort_values(by="srednia", ascending=True).head(3)

    return focus_df


def grades_below(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Return subjects whose base average is below threshold."""
    with_grades = df[df["liczba_ocen"] > 0]
    return with_grades[with_grades["srednia"] < threshold].sort_values(by="srednia", ascending=True)


def grades_for_subject(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """Return grade records for a subject, ignoring letter case."""
    return df[df["Przedmiot"].str.contains(subject, case=False, na=False, regex=False)]


def summary_by_subject(df: pd.DataFrame) -> pd.DataFrame:
    """Return record count and mean base grade by subject."""
    summary = df[["Przedmiot", "Oceny bieżące", "liczba_ocen", "srednia"]].copy()
    summary["avg_base_grade"] = summary["srednia"]
    summary["record_count"] = summary["liczba_ocen"]
    return summary.sort_values(by=["srednia", "liczba_ocen"], ascending=[False, False], na_position="last")


def print_averages_table(df: pd.DataFrame) -> None:
    """Display table of all subjects and their averages."""
    summary = summary_by_subject(df)
    print("\n" + "=" * 80)
    print(f"{'SUBJECT':<44} | {'COUNT':<6} | {'AVERAGE':<7} | {'CURRENT GRADES'}")
    print("-" * 80)
    for _, row in summary.iterrows():
        subj = str(row["Przedmiot"])[:44]
        cnt = row["liczba_ocen"]
        avg = f"{row['srednia']:.2f}" if pd.notna(row["srednia"]) else "-"
        grades_txt = str(row["Oceny bieżące"])
        print(f"{subj:<44} | {cnt:<6} | {avg:<7} | {grades_txt}")
    print("=" * 80)

    valid_averages = df["srednia"].dropna()
    if not valid_averages.empty:
        overall_gpa = valid_averages.mean()
        print(f"Overall arithmetic grade point average across graded subjects: {overall_gpa:.2f}")


def print_focus_subjects(df: pd.DataFrame, threshold: float = 3.5) -> None:
    """Display subjects that require attention/focus."""
    focus = subjects_to_focus_on(df, threshold)
    print("\n" + "=" * 80)
    print("🎯 SUBJECTS TO FOCUS ON")
    print("=" * 80)
    if focus.empty:
        print("No grades found in file.")
        return

    any_below = any(row["srednia"] <= threshold for _, row in focus.iterrows())
    if not any_below:
        print(f"All subjects have an average above {threshold:.2f}! Lowest averages:")
    else:
        print(f"Criteria: average <= {threshold:.2f} or grade 1-2 (failing / warning):")

    print("-" * 80)
    for idx, (_, row) in enumerate(focus.iterrows(), start=1):
        subj = row["Przedmiot"]
        avg = f"{row['srednia']:.2f}" if pd.notna(row["srednia"]) else "-"
        grades = row["oceny_lista"]
        grades_str = ", ".join(str(g) for g in grades) if grades else "No grades"
        reasons = []
        if pd.notna(row["srednia"]) and row["srednia"] <= threshold:
            reasons.append(f"low average ({avg})")
        if any(g <= 2 for g in grades):
            reasons.append("contains grade 1 or 2")
        reason_str = f" [{', '.join(reasons)}]" if reasons else ""
        print(f"  {idx}. {subj} — Average: {avg} (Grades: {grades_str}){reason_str}")
    print("=" * 80)


def get_user_input(prompt: str) -> str:
    """Read user input in console. Pressing Backspace on empty input returns '__BACKSPACE__'."""
    if sys.stdin.isatty():
        import termios
        import tty

        sys.stdout.write(prompt)
        sys.stdout.flush()
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        chars: list[str] = []
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\x03", "\x04"):  # Ctrl+C, Ctrl+D
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    raise KeyboardInterrupt
                if ch in ("\r", "\n"):  # Enter
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    break
                if ch in ("\x7f", "\x08", "\b"):  # Backspace
                    if not chars:
                        sys.stdout.write("\r\nExiting via Backspace.\r\n")
                        sys.stdout.flush()
                        return "__BACKSPACE__"
                    else:
                        chars.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                else:
                    chars.append(ch)
                    sys.stdout.write(ch)
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return "".join(chars).strip()
    else:
        try:
            val = input(prompt).strip()
        except EOFError:
            return "__BACKSPACE__"
        if val.lower() in ("backspace", "\x7f", "\x08", "\b"):
            return "__BACKSPACE__"
        return val


def main() -> None:
    print("\n" + "=" * 80)
    print("                    LIBRUS INTELLIGENCE — GRADE ANALYZER")
    print("=" * 80)

    prompt_msg = "Enter path to Librus PDF file (or press Backspace to exit): "
    pdf_input = get_user_input(prompt_msg)

    if pdf_input == "__BACKSPACE__":
        print("Program terminated.")
        return

    # Validate path — if invalid: raise exception
    raw_path = pdf_input.strip().strip("'\"")
    pdf_path = Path(raw_path).expanduser()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Invalid file path: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"The specified file does not have a .pdf extension: {pdf_path}")

    # Process PDF to CSV and load data
    csv_path = convert_pdf_to_csv(pdf_path, "grades.csv")
    df = load_grades(csv_path)

    if df.empty:
        print("The file contains no records.")
        return

    # Display averages and subjects to focus on
    print_averages_table(df)
    print_focus_subjects(df)

    # Interactive menu
    while True:
        print("\nOptions:")
        print("  1. Display averages table again")
        print("  2. Display subjects to focus on")
        print("  3. Search grades for a subject")
        print("  4. Show subjects with average below a threshold")
        print("  [Backspace] Exit program")

        choice = get_user_input("Select an option: ")
        if choice == "__BACKSPACE__":
            print("Program terminated.")
            break
        elif choice == "1":
            print_averages_table(df)
        elif choice == "2":
            threshold_str = get_user_input("Enter average threshold (default 3.5): ")
            if threshold_str == "__BACKSPACE__":
                print("Program terminated.")
                break
            try:
                threshold = float(threshold_str) if threshold_str else 3.5
            except ValueError:
                threshold = 3.5
            print_focus_subjects(df, threshold)
        elif choice == "3":
            subj_query = get_user_input("Enter subject name (or part of it): ")
            if subj_query == "__BACKSPACE__":
                print("Program terminated.")
                break
            found = grades_for_subject(df, subj_query)
            if found.empty:
                print("No matching subject found.")
            else:
                for _, r in found.iterrows():
                    avg_txt = f"{r['srednia']:.2f}" if pd.notna(r["srednia"]) else "none"
                    print(f" -> {r['Przedmiot']}: Grades: {r['Oceny bieżące']} | Average: {avg_txt}")
        elif choice == "4":
            threshold_str = get_user_input("Show subjects with average below: ")
            if threshold_str == "__BACKSPACE__":
                print("Program terminated.")
                break
            try:
                thr = float(threshold_str)
                below = grades_below(df, thr)
                if below.empty:
                    print(f"No subjects with average below {thr}.")
                else:
                    for _, r in below.iterrows():
                        print(f" -> {r['Przedmiot']}: Average {r['srednia']:.2f} ({r['Oceny bieżące']})")
            except ValueError as e:
                print(f"Invalid input: {e}")
        else:
            print("Unknown option. Press Backspace to exit.")


if __name__ == "__main__":
    main()
