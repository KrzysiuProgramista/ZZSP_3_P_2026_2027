"""Tests for the Data Rescue pipeline.  Run with:  pytest -q"""
import math

import numpy as np
import pandas as pd

from sales_pipeline import clean_sales, prepare_sales

COLUMNS = ["id", "order_date", "product", "category", "region", "quantity",
           "price", "channel"]


def make_df(*rows):
    """Build a raw-style (all text) DataFrame.  Missing fields use defaults."""
    base = dict(id="ORD-0001", order_date="01.09.2026", product="Desk Lamp",
                category="Furniture", region="North", quantity="2",
                price="100.00", channel="Online")
    return pd.DataFrame([{**base, **r} for r in rows], columns=COLUMNS)


# 1. input unchanged ---------------------------------------------------------
def test_input_is_not_modified():
    raw = make_df({"region": " north ", "price": "$1,299.99"},
                  {"id": "ORD-0002", "quantity": "five"})
    snapshot = raw.copy(deep=True)
    prepare_sales(raw)
    clean_sales(raw)
    pd.testing.assert_frame_equal(raw, snapshot)


# 2. correct numeric conversion ---------------------------------------------
def test_price_conversion_formats():
    cases = {
        "799.00": 799.0,
        "$1,299.99": 1299.99,       # currency symbol + thousands separator
        "€ 349,00": 349.0,          # decimal comma + symbol + space
        "1.299,99": 1299.99,        # European thousands + decimal comma
        "  42.5 ": 42.5,            # whitespace
    }
    raw = make_df(*[{"id": f"ORD-{i:04d}", "price": p}
                    for i, p in enumerate(cases, 1)])
    out, _ = clean_sales(raw)
    assert out["price"].dtype == "float64"
    for got, want in zip(out["price"], cases.values()):
        assert math.isclose(got, want)


def test_quantity_becomes_nullable_int_and_never_zero_filled():
    raw = make_df(
        {"id": "ORD-0001", "quantity": "3"},
        {"id": "ORD-0002", "quantity": "five"},    # word -> 5
        {"id": "ORD-0003", "quantity": ""},        # blank -> NA
        {"id": "ORD-0004", "quantity": "0"},       # zero -> NA
        {"id": "ORD-0005", "quantity": "-3"},      # negative -> NA
        {"id": "ORD-0006", "quantity": "abc"},     # junk -> NA
    )
    out, _ = clean_sales(raw)
    assert str(out["quantity"].dtype) == "Int64"
    assert out["quantity"].tolist()[:2] == [3, 5]
    assert out["quantity"].iloc[2:].isna().all()
    assert (out["quantity"].fillna(-1) != 0).all()      # no hidden zeros


def test_dates_parsed_and_invalid_become_nat():
    raw = make_df({"id": "ORD-0001", "order_date": "19.09.2026"},
                  {"id": "ORD-0002", "order_date": "31.02.2026"},   # impossible
                  {"id": "ORD-0003", "order_date": ""})
    out, _ = clean_sales(raw)
    assert pd.api.types.is_datetime64_any_dtype(out["order_date"])
    assert out["order_date"].iloc[0] == pd.Timestamp("2026-09-19")
    assert out["order_date"].iloc[1:].isna().all()


# 3. duplicate handling -----------------------------------------------------
def test_exact_duplicates_are_dropped():
    row = {"id": "ORD-0001"}
    raw = make_df(row, row, {"id": "ORD-0002"})
    out, rep = clean_sales(raw)
    assert len(out) == 2
    assert rep["dropped_exact_duplicates"] == 1
    # a pure copy is noise, not a conflict: it must not raise an id-conflict flag
    assert not out["id_conflict"].any()
    assert rep["dropped_older_duplicate_ids"] == 0


def test_repeated_id_keeps_newest_and_flags_conflict():
    raw = make_df({"id": "ORD-0040", "order_date": "09.10.2026"},
                  {"id": "ORD-0040", "order_date": "27.10.2026"},
                  {"id": "ORD-0041"})
    out, rep = clean_sales(raw)
    kept = out[out["id"] == "ORD-0040"]
    assert len(kept) == 1
    assert kept["order_date"].iloc[0] == pd.Timestamp("2026-10-27")
    assert bool(kept["id_conflict"].iloc[0]) is True
    assert rep["dropped_older_duplicate_ids"] == 1


def test_whitespace_and_case_variants_collapse_to_one_value():
    raw = make_df({"id": "ORD-0001", "region": " north "},
                  {"id": "ORD-0002", "region": "NORTH"},
                  {"id": "ORD-0003", "region": "North"},
                  {"id": "ORD-0004", "product": " desk LAMP "})
    out, _ = clean_sales(raw)
    assert out["region"].unique().tolist() == ["North"]
    assert out["product"].unique().tolist() == ["Desk Lamp"]


# 4. derived columns --------------------------------------------------------
def test_derived_total_vat_bulk_priority_and_codes():
    raw = make_df(
        {"id": "ORD-0001", "quantity": "2", "price": "100", "region": "East"},
        {"id": "ORD-0002", "quantity": "10", "price": "100", "region": "West"},
        {"id": "ORD-0003", "quantity": "5", "price": "1000", "region": "Mars"},
    )
    out, _ = prepare_sales(raw)
    assert out["total"].tolist() == [200.0, 1000.0, 5000.0]
    assert np.allclose(out["total_with_vat"], [246.0, 1230.0, 6150.0])
    assert out["is_bulk"].tolist() == [False, True, False]
    assert out["priority"].tolist() == ["low", "medium", "high"]  # 1000 / 5000 are inclusive
    assert out["region_code"].tolist() == ["E", "W", "UNK"]       # unknown region handled
    assert out["product_label"].iloc[0] == "Desk Lamp x2"


# 5. invalid / missing data -------------------------------------------------
def test_missing_values_stay_missing_not_zero():
    raw = make_df({"id": "ORD-0001", "price": "unknown"},
                  {"id": "ORD-0002", "price": ""},
                  {"id": "ORD-0003", "quantity": ""},
                  {"id": "ORD-0004", "quantity": "2", "price": "50"})
    out, _ = prepare_sales(raw)
    assert out["total"].isna().tolist() == [True, True, True, False]
    assert out["priority"].tolist()[:3] == ["unknown"] * 3     # not silently 'low'
    assert out["total"].sum() == 100.0                         # NaN rows add nothing
    assert (out.loc[out["total"].isna(), "needs_review"]).all()


def test_review_flags_explain_why():
    raw = make_df(
        {"id": "ORD-0001", "order_date": "31.02.2026"},
        {"id": "ORD-0002", "quantity": "25"},
        {"id": "ORD-0003", "order_date": "01.01.2030"},
        {"id": "ORD-0004", "product": "Laptop Pro 14", "category": "Accessories"},
        {"id": "ORD-0005"},
    )
    out, _ = prepare_sales(raw)
    why = dict(zip(out["id"], out["review_reason"]))
    assert "invalid_date" in why["ORD-0001"]
    assert "suspicious_quantity" in why["ORD-0002"]
    assert "future_date" in why["ORD-0003"]
    assert "category_mismatch" in why["ORD-0004"]
    assert why["ORD-0005"] == ""                       # clean row stays unflagged


def test_category_follows_product_when_they_disagree():
    raw = make_df({"product": "Laptop Pro 14", "category": "Accessories"})
    out, rep = clean_sales(raw)
    assert out["category"].iloc[0] == "Electronics"
    assert rep["fixed_values"]["category_overridden_by_product"] == 1


# 6. repeatability ----------------------------------------------------------
def test_prepare_sales_is_repeatable():
    raw = make_df({"id": "ORD-0001", "price": "$1,299.99", "region": " east "},
                  {"id": "ORD-0001", "price": "$1,299.99", "region": " east "},
                  {"id": "ORD-0002", "quantity": "five", "order_date": "x"})
    first, rep1 = prepare_sales(raw)
    second, rep2 = prepare_sales(raw)
    pd.testing.assert_frame_equal(first, second)
    assert rep1 == rep2


def test_works_on_real_nan_input_too():
    """pd.read_csv gives NaN for blanks; the pipeline must cope with that."""
    raw = make_df({"id": "ORD-0001", "price": None, "quantity": None})
    out, _ = prepare_sales(raw)
    assert out["total"].isna().all()
