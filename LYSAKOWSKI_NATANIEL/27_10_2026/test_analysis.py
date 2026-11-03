"""pytest tests for the Data Rescue pipeline.  Run:  pytest -q test_analysis.py
Plain asserts only, so no fixtures/plugins are required."""
import numpy as np
import pandas as pd

from analysis import clean_sales, prepare_sales, _parse_price


def make_raw() -> pd.DataFrame:
    """Small hand-made frame covering every kind of damage."""
    return pd.DataFrame({
        "id":         ["A1", "A2", "A2", "A3", "A4", "A5", "A6", "A6", "A7"],
        "order_date": ["01.08.2026", "02.08.2026", "02.08.2026", "31.02.2026", "03.08.2026",
                       "04.08.2026", "05.08.2026", "09.08.2026", "06.08.2026"],
        "product":    [" Desk Lamp ", "Mouse", "Mouse", "WIRELESS", "Mouse", "Mouse", "Mouse", "Mouse", "Mouse"],
        "category":   ["furniture", "Accessories", "Accessories", "Accessories", "Accessories",
                       "Accessories", "Accessories", "Accessories", "Accessories"],
        "region":     ["NORTH", "South", "South", " east ", "West", "West", "West", "West", "West"],
        "quantity":   ["2", "10", "10", "-3", "five", "", "1", "1", "0"],
        "price":      ["$1,299.99", "€ 349,00", "€ 349,00", "unknown", "", "12.50", "1.299,99", "10", "5"],
        "channel":    ["Store", "Online", "Online", "Phone", "Store", "Store", "Store", "Store", "Store"],
    })


def test_input_is_not_modified():
    raw = make_raw()
    snapshot = raw.copy(deep=True)
    prepare_sales(raw)
    assert raw.equals(snapshot)


def test_price_numeric_conversion():
    prices = pd.Series(["$1,299.99", "€ 349,00", "1.299,99", "799.00", "12,5", "", "unknown", None, "0", "-5"])
    out = _parse_price(prices)
    assert out.dtype == "float64"
    assert out.iloc[:5].round(2).tolist() == [1299.99, 349.0, 1299.99, 799.0, 12.5]
    # blank, 'unknown', None, zero and negative prices are NaN - never silently 0
    assert out.iloc[5:].isna().all()


def test_duplicate_handling():
    clean, rep = clean_sales(make_raw())
    # exact duplicate (A2 twice, identical) is dropped
    assert rep["exact_duplicates_dropped"] == 1
    assert (clean["id"] == "A2").sum() == 1
    # A6 appears twice with different dates: newest (09.08) kept and flagged as a conflict
    a6 = clean[clean["id"] == "A6"]
    assert len(a6) == 1
    assert a6["order_date"].iloc[0] == pd.Timestamp("2026-08-09")
    assert bool(a6["id_conflict"].iloc[0]) is True
    assert clean["id"].is_unique


def test_derived_total_and_vat_and_priority():
    result, _ = prepare_sales(make_raw())
    r = result.set_index("id")
    assert abs(r.loc["A1", "total"] - 2 * 1299.99) < 0.01       # 2 * 1299.99
    assert abs(r.loc["A1", "total_with_vat"] - round(2 * 1299.99 * 1.23, 2)) < 0.01
    assert r.loc["A1", "priority"] == "medium"                  # 2599.98 -> medium
    assert r.loc["A2", "priority"] == "medium"                  # 10 * 349 = 3490
    assert bool(r.loc["A2", "is_bulk"]) is True                 # 10 >= 10
    assert r.loc["A2", "product_label"] == "Mouse x10"


def test_invalid_and_missing_data_stay_missing():
    result, rep = prepare_sales(make_raw())
    r = result.set_index("id")
    assert str(result["quantity"].dtype) == "Int64"
    assert pd.isna(r.loc["A3", "order_date"])                   # 31.02 is not a date
    assert pd.isna(r.loc["A3", "quantity"])                     # negative quantity
    assert pd.isna(r.loc["A3", "price"])                        # 'unknown'
    assert r.loc["A4", "quantity"] == 5                         # 'five' -> 5 (documented repair)
    assert pd.isna(r.loc["A5", "quantity"])                     # blank quantity
    assert pd.isna(r.loc["A7", "quantity"])                     # zero quantity
    # missing inputs -> missing total + visible priority label, NOT zero / 'low'
    assert pd.isna(r.loc["A3", "total"]) and r.loc["A3", "priority"] == "unknown"
    assert pd.isna(r.loc["A4", "total"])                        # price blank
    assert bool(r.loc["A3", "needs_review"]) and "invalid_date" in r.loc["A3", "review_reasons"]


def test_label_standardisation():
    clean, _ = clean_sales(make_raw())
    assert set(clean["region"]) == {"North", "South", "East", "West"}
    assert clean.loc[clean["id"] == "A1", "category"].iloc[0] == "Furniture"
    assert clean.loc[clean["id"] == "A1", "product"].iloc[0] == "Desk Lamp"  # whitespace stripped


def test_pipeline_is_repeatable():
    raw = make_raw()
    first, rep1 = prepare_sales(raw)
    second, rep2 = prepare_sales(raw)
    assert first.equals(second)
    assert rep1 == rep2
    # running the pipeline on its own cleaned input columns must not change the data
    again, _ = prepare_sales(first[["id", "order_date", "product", "category", "region", "quantity", "price", "channel"]]
                             .assign(order_date=lambda d: d["order_date"].dt.strftime("%d.%m.%Y")))
    assert again["total"].fillna(-1).tolist() == first["total"].fillna(-1).tolist()


def test_unknown_region_gets_code_not_nan():
    raw = make_raw()
    raw.loc[0, "region"] = "Atlantis"
    result, _ = prepare_sales(raw)
    assert result.loc[result["id"] == "A1", "region_code"].iloc[0] == "UNK"
    assert result["region_code"].notna().all()
