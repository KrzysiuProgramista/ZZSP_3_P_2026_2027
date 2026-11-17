import numpy as np
import pandas as pd
import pytest

from analysis import (
    add_features, clean_sales, prepare_sales,
    product_label_apply, product_label_vectorised,
)

COLS = ["id", "order_date", "product", "category", "region", "quantity", "price", "channel"]


def make(rows):
    return pd.DataFrame(rows, columns=COLS, dtype="str")


@pytest.fixture
def raw():
    return make([
        ["A1", "01.08.2026", "Office Chair", "Furniture", "East", "2", "799.00", "Phone"],
        ["A2", "02.08.2026", " office chair ", "furniture ", " north ", "3", "$1,299.99", "Store"],
        ["A3", "31.02.2026", "Desk Lamp", "Furniture", "SOUTH", "five", "€ 349,00", "Online"],
        ["A4", "03.08.2026", "Desk Lamp", "Furniture", "Mars", "", "unknown", "Online"],
        ["A5", "04.08.2026", "Desk Lamp", "Furniture", "West", "-3", "", "Online"],
        ["A6", "05.08.2026", "Desk Lamp", "Furniture", "West", "0", "1,299", "Online"],
        ["A1", "01.08.2026", "Office Chair", "Furniture", "East", "2", "799.00", "Phone"],   # exact dup
        ["A7", "06.08.2026", "Whiteboard", "Stationery", "East", "4", "189.00", "Phone"],
        ["A7", "20.08.2026", "Whiteboard", "Stationery", "East", "4", "189.00", "Phone"],   # id conflict
    ])


@pytest.fixture
def real():
    return pd.read_csv("dirty_sales.csv", dtype=str)


def test_input_unchanged(raw):
    snapshot = raw.copy(deep=True)
    prepare_sales(raw)
    pd.testing.assert_frame_equal(raw, snapshot)


def test_price_numeric_conversion(raw):
    out, _ = clean_sales(raw)
    p = out.set_index("id")["price"]
    assert p.dtype == "float64"
    assert p["A1"] == 799.00
    assert p["A2"] == pytest.approx(1299.99)      # $ + thousands separator
    assert p["A3"] == pytest.approx(349.00)       # € + decimal comma
    assert p["A6"] == pytest.approx(1299.0)       # thousands separator only
    assert np.isnan(p["A4"]) and np.isnan(p["A5"])  # 'unknown' and blank → NaN, not 0
    assert (out.set_index("id").loc[["A2", "A3"], "currency"] == ["USD", "EUR"]).all()


def test_quantity_rules(raw):
    out, _ = clean_sales(raw)
    q = out.set_index("id")["quantity"]
    assert str(q.dtype) == "Int64"
    assert q["A1"] == 2
    for i in ["A3", "A4", "A5", "A6"]:           # 'five', blank, -3, 0 → <NA>
        assert pd.isna(q[i])
    o = out.set_index("id")
    assert o.loc["A3", "qty_non_numeric"] and o.loc["A4", "qty_missing"]
    assert o.loc["A5", "qty_non_positive"] and o.loc["A6", "qty_non_positive"]


def test_duplicate_handling(raw):
    out, rep = clean_sales(raw)
    assert rep["exact_duplicates_dropped"] == 1
    assert rep["id_conflicts_dropped"] == 1
    assert out["id"].is_unique
    a7 = out.set_index("id").loc["A7"]
    assert a7["order_date"] == pd.Timestamp("2026-08-20")   # newest kept
    assert a7["id_conflict"]


def test_standardisation_and_dates(raw):
    out, _ = clean_sales(raw)
    o = out.set_index("id")
    assert o.loc["A2", "product"] == "Office Chair"
    assert o.loc["A2", "region"] == "North"
    assert o.loc["A2", "category"] == "Furniture"
    assert pd.isna(o.loc["A3", "order_date"]) and o.loc["A3", "invalid_date"]
    assert pd.api.types.is_datetime64_any_dtype(out["order_date"])


def test_derived_total_and_priority(raw):
    out, _ = prepare_sales(raw)
    o = out.set_index("id")
    assert o.loc["A1", "total"] == pytest.approx(1598.0)
    assert o.loc["A1", "total_with_vat"] == pytest.approx(1598.0 * 1.23, abs=0.01)
    assert o.loc["A1", "priority"] == "medium"
    assert o.loc["A2", "priority"] == "medium"     # 3 * 1299.99 = 3899.97
    assert np.isnan(o.loc["A4", "total"])           # missing price → missing total, not 0
    assert o.loc["A4", "priority"] == "unknown"
    assert o.loc["A4", "region_code"] == "UNK"      # unknown region handled
    assert pd.isna(o.loc["A4", "is_bulk"])


def test_invalid_rows_flagged_for_review(raw):
    out, _ = prepare_sales(raw)
    o = out.set_index("id")
    assert o.loc[["A3", "A4", "A5", "A6"], "needs_review"].all()
    assert "invalid_date" in o.loc["A3", "review_reason"]
    assert not o.loc["A1", "needs_review"]


def test_pipeline_is_deterministic(real):
    a, ra = prepare_sales(real)
    b, rb = prepare_sales(real)
    pd.testing.assert_frame_equal(a, b)
    assert ra == rb


def test_real_file_expectations(real):
    out, rep = prepare_sales(real)
    assert rep["rows_in"] == 120 and rep["rows_out"] == 118
    assert set(out["region"]) == {"North", "South", "East", "West"}
    assert set(out["category"]) == {"Electronics", "Accessories", "Furniture", "Stationery"}
    assert out["id"].is_unique


def test_label_vectorised_matches_apply(raw):
    out, _ = clean_sales(raw)
    v = product_label_vectorised(out).astype(str)
    a = product_label_apply(out).astype(str)
    assert (v == a).all()
