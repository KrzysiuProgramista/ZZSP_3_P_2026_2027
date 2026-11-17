from pathlib import Path
import pandas as pd
import pytest

from slide_22 import report

df = pd.read_csv(Path(__file__).parent / "data.csv")


def test_one_filter():
    result = report(df, region="North")
    assert (result["region"] == "North").all()


def test_two_filters():
    result = report(df, region="North", category="Electronics")
    assert (result["region"] == "North").all()
    assert (result["category"] == "Electronics").all()


def test_no_match():
    result = report(df, region="Antarctica")
    assert result.empty


def test_unknown_column():
    with pytest.raises(ValueError, match="Unknown column"):
        report(df, department="North")


def test_no_filters():
    result = report(df)
    assert len(result) == len(df)
