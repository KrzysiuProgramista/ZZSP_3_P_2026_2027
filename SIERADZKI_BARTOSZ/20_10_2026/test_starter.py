"""Tests use fictional records only."""
from io import StringIO

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from starter import (
    grades_below, grades_between_dates, grades_for_subject,
    load_grades, main, report, summary_by_subject,
)


@pytest.fixture
def df():
    return load_grades(StringIO(
        "date,subject,grade,description\n"
        "2026-09-01,Matematyka,2,A\n"
        "2026-09-10,Matematyka,4+,B\n"
        "2026-09-15,Historia,5,C\n"
        "2026-09-20,Historia,np,D\n"
        "bad,,16,E\n"
    ))


def test_load(df):
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["grade_base"].iloc[:3].tolist() == [2, 4, 5]
    assert df["grade_base"].iloc[3:].isna().all()
    assert pd.isna(df.loc[4, "date"])


def test_missing_columns():
    with pytest.raises(ValueError, match="Brak wymaganych kolumn"):
        load_grades(StringIO("subject,grade\nMatematyka,4\n"))


def test_below(df):
    assert_frame_equal(grades_below(df, 4), df.iloc[[0]])


def test_subject(df):
    assert_frame_equal(grades_for_subject(df, "MAT"), df.iloc[[0, 1]])
    assert grades_for_subject(df, ".*").empty  # Literal, not regex.


def test_dates_include_boundaries(df):
    assert_frame_equal(
        grades_between_dates(df, "2026-09-01", "2026-09-10"), df.iloc[[0, 1]]
    )


@pytest.mark.parametrize("start,end", [
    ("bad", "2026-09-01"), ("2026-09-10", "2026-09-01"), ("", "2026-09-01")
])
def test_invalid_dates(df, start, end):
    with pytest.raises(ValueError):
        grades_between_dates(df, start, end)


def test_report(df):
    assert_frame_equal(report(df, subject="Matematyka", grade_base=4), df.iloc[[1]])
    assert_frame_equal(report(df), df)
    assert_frame_equal(report(df, subject=None), df.iloc[[4]])
    assert_frame_equal(report(df, date=pd.Timestamp("2026-09-15")), df.iloc[[2]])


def test_unknown_column_even_after_no_matches(df):
    with pytest.raises(ValueError, match="Nieznana kolumna: missing"):
        report(df, subject="No match", missing=1)


def test_summary_counts_non_grade_records(df):
    summary = summary_by_subject(df).set_index("subject")
    assert summary.loc["Matematyka", "record_count"] == 2
    assert summary.loc["Matematyka", "average_base_grade"] == 3
    assert summary.loc["Historia", "record_count"] == 2
    assert summary.loc["Historia", "average_base_grade"] == 5
    assert summary["record_count"].sum() == len(df)


def test_menu(tmp_path, monkeypatch, capsys):
    path = tmp_path / "fictional.csv"
    path.write_text(
        "date,subject,grade,description\n2026-09-01,Matematyka,2,Fictional\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("sys.argv", ["starter.py", str(path)])
    replies = iter([
        "1", "3", "2", "MAT", "3", "2026-09-01", "2026-09-01",
        "4", "5", "subject", "Matematyka", "grade_base", "2", "",
        "5", "date", "2026-09-01", "",
        "5", "unknown", "6", "9", "0",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(replies))
    main()
    output = capsys.readouterr().out
    assert "Nieznana kolumna: unknown" in output
    assert "nie jest oficjalną oceną" in output
    assert "Do widzenia." in output
