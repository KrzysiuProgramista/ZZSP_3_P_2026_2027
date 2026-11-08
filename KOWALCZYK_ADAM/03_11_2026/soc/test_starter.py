import pandas as pd
import pytest
from starter import load_data, soc_dashboard, add_group_context
from make_dashboard import build_html

TABLES = {"by_attack", "by_country", "by_asset", "by_hour", "top_sources", "daily_trend"}


@pytest.fixture(scope="module")
def df():
    return load_data()


def test_returns_six_tables(df):
    out = soc_dashboard(df)
    assert set(out) == TABLES
    assert all(isinstance(t, pd.DataFrame) for t in out.values())


def test_does_not_mutate_input(df):
    before = df.copy()
    soc_dashboard(df)
    pd.testing.assert_frame_equal(df, before)


def test_incident_totals_match(df):
    out = soc_dashboard(df)
    for name in ("by_attack", "by_country", "by_asset", "by_hour", "daily_trend"):
        assert out[name]["incidents"].sum() == len(df)


def test_top_sources_five_sorted(df):
    t = soc_dashboard(df)["top_sources"]
    assert len(t) == 5
    assert t["incidents"].is_monotonic_decreasing


def test_by_hour_and_daily_sorted(df):
    out = soc_dashboard(df)
    assert out["by_hour"]["hour"].is_monotonic_increasing
    assert out["daily_trend"]["event_date"].is_monotonic_increasing


def test_rates_are_percentages(df):
    a = soc_dashboard(df)["by_attack"]
    assert a[["blocked_rate_pct", "compromise_rate_pct"]].stack().between(0, 100).all()


def test_empty_dataframe_gives_empty_tables(df):
    out = soc_dashboard(df.iloc[0:0])
    assert set(out) == TABLES
    assert all(t.empty for t in out.values())
    assert "SOC Dashboard" in build_html(df.iloc[0:0], out)


def test_missing_columns_raise_clear_error():
    with pytest.raises(ValueError, match="missing required columns"):
        soc_dashboard(pd.DataFrame())


def test_group_context_keeps_rows_and_matches_mean(df):
    ctx = add_group_context(df)
    assert len(ctx) == len(df)
    assert ctx["response_vs_attack_avg"].groupby(ctx["attack_type"]).sum().abs().max() < 1e-6
    assert "attack_avg_response" not in df.columns  # input untouched
