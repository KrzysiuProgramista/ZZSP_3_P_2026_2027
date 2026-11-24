import pandas as pd, pytest
from analysis import prepare_sales, parse_price

def mk(**o):
    base = dict(id="ORD-1", order_date="01.08.2026", product="Desk Lamp", category="Furniture",
                region=" north ", quantity="2", price="10.00", channel="Online")
    base.update(o); return base

def frame(*rows): return pd.DataFrame(list(rows), dtype=str)

def test_input_unchanged():
    raw = frame(mk(), mk(id="ORD-2", price="$1,299.99"))
    snap = raw.copy(deep=True); prepare_sales(raw)
    pd.testing.assert_frame_equal(raw, snap)

def test_price_conversion():
    r = parse_price(pd.Series(["$1,299.99", "€ 349,00", "799.00", "unknown", "", None]))
    assert r.iloc[:3].tolist() == [1299.99, 349.0, 799.0]
    assert r.iloc[3:].isna().all()

def test_exact_duplicate_dropped_and_conflict_keeps_newest():
    raw = frame(mk(), mk(), mk(id="ORD-2", quantity="1"), mk(id="ORD-2", order_date="05.09.2026", quantity="4"))
    df, rep = prepare_sales(raw)
    assert rep["exact_duplicates_dropped"] == 1 and len(df) == 2
    row = df[df.id == "ORD-2"].iloc[0]
    assert row.quantity == 4 and row.id_conflict

def test_total_and_vat():
    df, _ = prepare_sales(frame(mk(quantity="3", price="100,50")))
    assert df.total.iloc[0] == pytest.approx(301.5)
    assert df.total_with_vat.iloc[0] == pytest.approx(301.5 * 1.23)

def test_invalid_data_becomes_nan_not_zero():
    raw = frame(mk(id="A", quantity="five"), mk(id="B", quantity="0"), mk(id="C", quantity="-3"),
                mk(id="D", price="unknown"), mk(id="E", order_date="31.02.2026"))
    df, _ = prepare_sales(raw)
    d = df.set_index("id")
    assert d.loc[["A", "B", "C"], "quantity"].isna().all()
    assert pd.isna(d.loc["D", "price"]) and pd.isna(d.loc["D", "total"])
    assert pd.isna(d.loc["E", "order_date"]) and df.needs_review.all()
    assert (d.loc[["A", "B", "C", "D"], "priority"] == "unknown").all()

def test_idempotent_and_dtypes():
    raw = frame(mk(), mk(id="ORD-2", quantity=""))
    a, _ = prepare_sales(raw); b, _ = prepare_sales(raw)
    pd.testing.assert_frame_equal(a, b)
    assert str(a.quantity.dtype) == "Int64"

def test_names_standardised():
    df, _ = prepare_sales(frame(mk(product=" desk LAMP ", category="Accessories"), mk(id="2"), mk(id="3")))
    assert df["product"].nunique() == 1 and df["region"].unique().tolist() == ["North"]
    assert df["category"].nunique() == 1
