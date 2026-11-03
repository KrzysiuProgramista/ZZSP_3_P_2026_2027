import numpy as np
import pandas as pd
import pytest

from analysis import add_features, clean_sales, prepare_sales

TODAY = "2026-11-03"

def sample_raw():
    return pd.DataFrame({
        "id": ["ORD-0001", "ORD-0002", "ORD-0003", "ORD-0004"],
        "order_date": ["19.09.2026", "02.08.2026", "31.02.2026",
                       "05.12.2027"],
        "product": ["Office Chair", " laptop pro 14 ", "WIRELESS MOUSE",
                    "USB-C Hub"],
        "category": ["Furniture", "Electronics", "Accessories ",
                     "Accessories"],
        "region": ["East", " north ", "NORTH", "west"],
        "quantity": ["2", "12", "five", "3"],
        "price": ["799.00", "$1,299.99", "unknown", "€ 349,00"],
        "channel": ["Phone", "Online", "Store", "Phone"],
    })


@pytest.fixture
def raw():
    return sample_raw()


@pytest.fixture
def real_raw():
    return pd.read_csv("dirty_sales.csv", dtype=str)

def test_clean_sales_does_not_modify_input(raw):
    before = raw.copy(deep=True)
    clean_sales(raw, today=TODAY)
    pd.testing.assert_frame_equal(raw, before)


def test_prepare_sales_does_not_modify_input(real_raw):
    before = real_raw.copy(deep=True)
    prepare_sales(real_raw, today=TODAY)
    pd.testing.assert_frame_equal(real_raw, before)


def test_add_features_does_not_modify_input(raw):
    cleaned, _ = clean_sales(raw, today=TODAY)
    before = cleaned.copy(deep=True)
    add_features(cleaned, today=TODAY)
    pd.testing.assert_frame_equal(cleaned, before)

def test_price_handles_every_broken_format(raw):
    cleaned, _ = clean_sales(raw, today=TODAY)
    price = cleaned.set_index("id")["price"]

    assert price["ORD-0001"] == pytest.approx(799.00)
    assert price["ORD-0002"] == pytest.approx(1299.99)
    assert pd.isna(price["ORD-0003"])
    assert price["ORD-0004"] == pytest.approx(349.00)
    assert pd.api.types.is_float_dtype(cleaned["price"])


def test_missing_price_is_nan_not_zero(real_raw):
    cleaned, report = clean_sales(real_raw, today=TODAY)
    assert report["price"]["blank_to_nan"] == 4
    assert report["price"]["unknown_literal_to_nan"] == 2
    assert cleaned["price"].isna().sum() == 6
    assert (cleaned["price"] == 0).sum() == 0


def test_quantity_is_nullable_int64(raw):
    cleaned, _ = clean_sales(raw, today=TODAY)
    quantity = cleaned.set_index("id")["quantity"]

    assert str(cleaned["quantity"].dtype) == "Int64"
    assert quantity["ORD-0001"] == 2
    assert quantity["ORD-0002"] == 12
    assert pd.isna(quantity["ORD-0003"])


def test_negative_quantity_becomes_nan_and_is_explained(real_raw):
    cleaned, report = clean_sales(real_raw, today=TODAY)
    assert report["quantity"]["negative_to_nan"] == 1
    assert (cleaned["quantity"] < 0).sum() == 0

    row = cleaned.loc[cleaned["id"] == "ORD-0094"].iloc[0]
    assert pd.isna(row["quantity"])
    assert "negative" in row["quantity_issue"]


def test_zero_quantity_is_kept_not_dropped(real_raw):
    cleaned, report = clean_sales(real_raw, today=TODAY)
    assert report["quantity"]["zero_kept"] == 1
    row = cleaned.loc[cleaned["id"] == "ORD-0022"].iloc[0]
    assert row["quantity"] == 0

def test_exact_duplicate_row_is_dropped(real_raw):
    cleaned, report = clean_sales(real_raw, today=TODAY)
    assert report["exact_duplicates_dropped"] == 1
    assert (cleaned["id"] == "ORD-0026").sum() == 1


def test_repeated_id_keeps_the_newest_record(real_raw):
    cleaned, report = clean_sales(real_raw, today=TODAY)
    assert report["id_conflicts"] == ["ORD-0040"]
    assert (cleaned["id"] == "ORD-0040").sum() == 1

    kept = cleaned.loc[cleaned["id"] == "ORD-0040", "order_date"].iloc[0]
    assert kept == pd.Timestamp("2026-10-27")


def test_every_id_is_unique_after_cleaning(real_raw):
    cleaned, _ = clean_sales(real_raw, today=TODAY)
    assert cleaned["id"].is_unique


def test_total_and_vat(raw):
    sales, _ = prepare_sales(raw, today=TODAY)
    row = sales.set_index("id").loc["ORD-0001"]

    assert row["total"] == pytest.approx(2 * 799.00)
    assert row["total_with_vat"] == pytest.approx(1598.00 * 1.23, abs=0.01)


def test_total_is_na_when_an_input_is_na(raw):
    sales, _ = prepare_sales(raw, today=TODAY)
    row = sales.set_index("id").loc["ORD-0003"]
    assert pd.isna(row["total"])
    assert row["priority"] == "unknown"


def test_priority_boundaries():
    frame = pd.DataFrame({
        "product": pd.array(["Desk Lamp"] * 5, dtype="string"),
        "region": pd.array(["North"] * 5, dtype="string"),
        "quantity": pd.array([1, 1, 1, 1, 1], dtype="Int64"),
        "price": [5000.0, 4999.0, 1000.0, 999.0, np.nan],
        "category": pd.array(["Furniture"] * 5, dtype="string"),
        "order_date": pd.to_datetime(["2026-08-01"] * 5),
    })
    out = add_features(frame, today=TODAY)
    assert out["priority"].tolist() == ["high", "medium", "medium", "low",
                                        "unknown"]


def test_is_bulk_keeps_missing_distinguishable(raw):
    sales, _ = prepare_sales(raw, today=TODAY)
    is_bulk = sales.set_index("id")["is_bulk"]

    assert str(sales["is_bulk"].dtype) == "boolean"
    assert not is_bulk["ORD-0001"]
    assert is_bulk["ORD-0002"]
    assert pd.isna(is_bulk["ORD-0003"])


def test_region_code_and_unknown_region():
    frame = pd.DataFrame({
        "product": pd.array(["Desk Lamp", "Desk Lamp"], dtype="string"),
        "region": pd.array(["North", "Unknown region"], dtype="string"),
        "quantity": pd.array([1, 1], dtype="Int64"),
        "price": [10.0, 10.0],
        "category": pd.array(["Furniture", "Furniture"], dtype="string"),
        "order_date": pd.to_datetime(["2026-08-01", "2026-08-01"]),
    })
    out = add_features(frame, today=TODAY)
    assert out["region_code"].tolist() == ["N", "UNK"]


def test_product_label_is_vectorised_and_handles_missing(raw):
    sales, _ = prepare_sales(raw, today=TODAY)
    label = sales.set_index("id")["product_label"]

    assert label["ORD-0001"] == "Office Chair x2"
    assert label["ORD-0002"] == "Laptop Pro 14 x12"
    assert label["ORD-0003"] == "Wireless Mouse x?"


def test_impossible_date_becomes_nat_and_is_flagged(raw):
    sales, report = prepare_sales(raw, today=TODAY)
    row = sales.set_index("id").loc["ORD-0003"]

    assert pd.isna(row["order_date"])
    assert report["order_date"]["invalid_to_nat"] == 1
    assert "impossible" in row["review_reasons"]


def test_future_date_is_flagged_not_removed(raw):
    sales, report = prepare_sales(raw, today=TODAY)
    row = sales.set_index("id").loc["ORD-0004"]

    assert row["order_date"] == pd.Timestamp("2027-12-05")
    assert report["order_date"]["in_the_future"] == 1
    assert "future" in row["review_reasons"]


def test_strings_are_standardised(raw):
    cleaned, _ = clean_sales(raw, today=TODAY)
    frame = cleaned.set_index("id")

    assert frame.loc["ORD-0002", "product"] == "Laptop Pro 14"
    assert frame.loc["ORD-0003", "product"] == "Wireless Mouse"
    assert frame.loc["ORD-0003", "category"] == "Accessories"
    assert frame.loc["ORD-0002", "region"] == "North"
    assert frame.loc["ORD-0003", "region"] == "North"
    assert frame.loc["ORD-0004", "region"] == "West"
    assert frame.loc["ORD-0004", "product"] == "USB-C Hub"


def test_product_category_mismatch_is_flagged_not_corrected(real_raw):
    sales, _ = prepare_sales(real_raw, today=TODAY)
    row = sales.set_index("id").loc["ORD-0043"]

    assert row["category"] == "Accessories"
    assert "category" in row["review_reasons"]


def test_unmapped_label_is_reported_not_dropped():
    frame = sample_raw()
    frame.loc[0, "region"] = "Central"
    cleaned, report = clean_sales(frame, today=TODAY)

    assert report["region"]["unmapped"] == 1
    assert cleaned.loc[0, "region"] == "Unknown region"
    assert len(cleaned) == len(frame)


def test_pipeline_is_reproducible(real_raw):
    first, report_a = prepare_sales(real_raw, today=TODAY)
    second, report_b = prepare_sales(real_raw, today=TODAY)

    pd.testing.assert_frame_equal(first, second)
    assert report_a == report_b


def test_report_accounts_for_every_row(real_raw):
    _, report = clean_sales(real_raw, today=TODAY)
    assert (report["rows_before"] - report["rows_dropped"]
            == report["rows_after"])
    assert (report["exact_duplicates_dropped"]
            + report["id_conflict_rows_dropped"] == report["rows_dropped"])


def test_empty_input_does_not_crash():
    empty = sample_raw().iloc[0:0]
    sales, report = prepare_sales(empty, today=TODAY)

    assert len(sales) == 0
    assert report["rows_before"] == 0
    assert report["rows_after"] == 0
    assert "total" in sales.columns
