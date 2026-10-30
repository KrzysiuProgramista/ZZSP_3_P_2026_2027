"""Unit tests for inspect_librus_pdf.py and starter.py."""
import io
from pathlib import Path
import pytest
import pandas as pd
from PIL import Image

import inspect_librus_pdf
import starter


@pytest.fixture
def dummy_pdf_without_columns(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "dummy_no_cols.pdf"
    img = Image.new("RGB", (100, 100), color="white")
    img.save(pdf_path)
    return pdf_path


def test_inspect_librus_pdf_success(tmp_path: Path):
    pdf_path = Path("Synergia.pdf")
    assert pdf_path.exists(), "Synergia.pdf must exist for this test"

    out_csv = tmp_path / "test_grades.csv"
    res_path = inspect_librus_pdf.convert_pdf_to_csv(pdf_path, out_csv)
    assert res_path.exists()

    df = pd.read_csv(res_path)
    assert list(df.columns) == ["Przedmiot", "Oceny bieżące"]
    assert len(df) > 0

    # Check some known subjects from Synergia.pdf
    subjects = list(df["Przedmiot"])
    assert "Matematyka" in subjects
    assert "Język angielski" in subjects
    assert "Geografia" in subjects


def test_inspect_librus_pdf_missing_columns(dummy_pdf_without_columns: Path):
    with pytest.raises(ValueError, match="PDF does not contain required columns"):
        inspect_librus_pdf.extract_librus_grades_from_pdf(dummy_pdf_without_columns)


def test_inspect_librus_pdf_invalid_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        inspect_librus_pdf.extract_librus_grades_from_pdf(tmp_path / "nonexistent.pdf")

    txt_file = tmp_path / "some.txt"
    txt_file.write_text("hello")
    with pytest.raises(ValueError, match="The input file must have a .pdf extension"):
        inspect_librus_pdf.extract_librus_grades_from_pdf(txt_file)


def test_starter_parse_grades():
    assert starter.parse_grades("Brak ocen") == []
    assert starter.parse_grades("5 5 6") == [5, 5, 6]
    assert starter.parse_grades("556") == [5, 5, 6]
    assert starter.parse_grades("T 5 + +") == [5]
    assert starter.parse_grades("3 + + 3 + +") == [3, 3]
    assert starter.parse_grades("$1++np~4+5++$ +5") == [1, 4, 5, 5]
    assert starter.parse_grades("+ + +") == []
    assert starter.parse_grades(None) == []


def test_starter_load_grades(tmp_path: Path):
    csv_file = tmp_path / "grades.csv"
    csv_file.write_text(
        "Przedmiot,Oceny bieżące\n"
        "Matematyka,3 3\n"
        "Historia,5 5\n"
        "Fizyka,Brak ocen\n",
        encoding="utf-8"
    )

    df = starter.load_grades(csv_file)
    assert "Przedmiot" in df.columns
    assert "Oceny bieżące" in df.columns
    assert "srednia" in df.columns
    assert "liczba_ocen" in df.columns

    mat = df[df["Przedmiot"] == "Matematyka"].iloc[0]
    assert mat["srednia"] == 3.0
    assert mat["liczba_ocen"] == 2

    hist = df[df["Przedmiot"] == "Historia"].iloc[0]
    assert hist["srednia"] == 5.0
    assert hist["liczba_ocen"] == 2

    fiz = df[df["Przedmiot"] == "Fizyka"].iloc[0]
    assert pd.isna(fiz["srednia"])
    assert fiz["liczba_ocen"] == 0


def test_starter_load_grades_missing_columns(tmp_path: Path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("col1,col2\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required columns"):
        starter.load_grades(bad_csv)


def test_starter_subjects_to_focus_on(tmp_path: Path):
    csv_file = tmp_path / "grades.csv"
    csv_file.write_text(
        "Przedmiot,Oceny bieżące\n"
        "Informatyka,6\n"
        "Język polski,5 4\n"
        "Matematyka,2 3\n"
        "Fizyka,3\n",
        encoding="utf-8"
    )
    df = starter.load_grades(csv_file)
    focus = starter.subjects_to_focus_on(df, threshold=3.5)
    focus_subjects = list(focus["Przedmiot"])

    # Matematyka has average 2.5 and contains grade 2 -> definitely in focus
    assert "Matematyka" in focus_subjects
    # Fizyka has average 3.0 (<= 3.5) -> in focus
    assert "Fizyka" in focus_subjects
    # Informatyka has average 6.0 -> not in focus
    assert "Informatyka" not in focus_subjects


def test_starter_invalid_path_raises(monkeypatch):
    # Simulate user entering invalid path
    monkeypatch.setattr("sys.stdin", io.StringIO("nonexistent_file.pdf\n"))
    with pytest.raises(FileNotFoundError, match="Invalid file path"):
        starter.main()


def test_starter_backspace_exits(monkeypatch, capsys):
    # Simulate user pressing backspace
    monkeypatch.setattr("sys.stdin", io.StringIO("backspace\n"))
    starter.main()
    captured = capsys.readouterr()
    assert "Program terminated." in captured.out
