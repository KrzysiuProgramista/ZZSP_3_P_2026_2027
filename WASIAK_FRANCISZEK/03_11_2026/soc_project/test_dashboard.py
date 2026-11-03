import pandas as pd
import pytest
from starter import load_data, soc_dashboard, attack_summary, add_group_context

KEYS = {"by_attack", "by_country", "by_asset", "by_hour", "top_sources", "daily_trend"}


@pytest.fixture(scope="module")
def df():
    return load_data()


def test_returns_six_tables(df):
    assert set(soc_dashboard(df)) == KEYS


def test_does_not_mutate_input(df):
    before = df.copy()
    soc_dashboard(df)
    pd.testing.assert_frame_equal(df, before)


def test_empty_dataframe(df):
    out = soc_dashboard(df.iloc[0:0])
    assert set(out) == KEYS and all(t.empty for t in out.values())


def test_attack_counts_sum_to_total(df):
    assert soc_dashboard(df)["by_attack"]["incidents"].sum() == len(df)


def test_top_sources_five_sorted(df):
    t = soc_dashboard(df)["top_sources"]
    assert len(t) == 5 and t["incidents"].is_monotonic_decreasing


def test_by_hour_sorted_and_complete(df):
    h = soc_dashboard(df)["by_hour"]
    assert h["hour"].is_monotonic_increasing
    assert h["incidents"].sum() == len(df)


def test_daily_trend_chronological(df):
    t = soc_dashboard(df)["daily_trend"]
    assert t["event_date"].is_monotonic_increasing
    assert t["compromised"].sum() == df["compromised"].sum()


def test_rates_between_0_and_1(df):
    a = attack_summary(df)
    assert a[["blocked_rate", "compromise_rate"]].apply(lambda s: s.between(0, 1).all()).all()


def test_group_context_columns(df):
    out = add_group_context(df)
    assert len(out) == len(df)
    assert {"attack_avg_response", "response_vs_attack_avg", "above_attack_avg_severity"} <= set(out.columns)
    assert "attack_avg_response" not in df.columns
