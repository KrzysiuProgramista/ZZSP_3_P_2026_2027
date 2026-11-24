import pandas as pd
import pytest
from starter import load_grades, grades_below, grades_for_subject, grades_between_dates, report, summary_by_subject

@pytest.fixture
def df():
    from pathlib import Path
    return load_grades(Path(__file__).parent / "sample_grades.csv")

def test_below(df):
    assert grades_below(df, 3)["grade"].tolist() == ["2"]

def test_subject(df):
    assert len(grades_for_subject(df, "MATH")) == 2

def test_dates(df):
    assert len(grades_between_dates(df, "2026-09-10", "2026-09-12")) == 2

def test_reversed(df):
    with pytest.raises(ValueError):
        grades_between_dates(df, "2026-10-01", "2026-09-01")

def test_report(df):
    assert len(report(df, subject="Mathematics", grade="4+")) == 1
    assert len(report(df)) == len(df)
    assert len(report(df, date=pd.Timestamp("2026-09-10"))) == 1

def test_unknown(df):
    with pytest.raises(ValueError, match="Unknown columns"):
        report(df, unknown=1)

def test_summary(df):
    row = summary_by_subject(df).set_index("subject").loc["Mathematics"]
    assert row["record_count"] == 2
    assert row["average_base_grade"] == 3
