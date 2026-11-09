import pandas as pd
import pytest
from starter import load_data, attack_summary, add_group_context, soc_dashboard


def test_load_data():
    df = load_data()
    assert not df.empty
    assert "timestamp" in df.columns
    assert "event_date" in df.columns
    assert "hour" in df.columns
    assert "weekday" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


def test_attack_summary():
    df = load_data()
    summary = attack_summary(df)
    assert not summary.empty
    expected_cols = [
        'attack_type', 'incident_count', 'unique_source_ips',
        'avg_response_time', 'blocked_rate', 'compromise_rate'
    ]
    for col in expected_cols:
        assert col in summary.columns


def test_add_group_context():
    df = load_data()
    enriched = add_group_context(df)
    assert len(enriched) == len(df)
    assert "attack_avg_response" in enriched.columns
    assert "response_vs_attack_avg" in enriched.columns
    assert "above_attack_avg_severity" in enriched.columns


def test_soc_dashboard_keys_and_types():
    df = load_data()
    dashboard = soc_dashboard(df)
    expected_keys = [
        "by_attack", "by_country", "by_asset",
        "by_hour", "top_sources", "daily_trend"
    ]
    for key in expected_keys:
        assert key in dashboard
        assert isinstance(dashboard[key], pd.DataFrame)
        assert not dashboard[key].empty


def test_soc_dashboard_immutability():
    df = load_data()
    original_shape = df.shape
    original_columns = list(df.columns)
    _ = soc_dashboard(df)
    assert df.shape == original_shape
    assert list(df.columns) == original_columns


def test_soc_dashboard_empty_dataframe():
    empty_df = pd.DataFrame(columns=[
        'incident_id', 'timestamp', 'source_ip', 'source_country',
        'target_asset', 'attack_type', 'severity', 'severity_score',
        'response_time_min', 'packets', 'bytes_transferred', 'blocked',
        'compromised', 'analyst'
    ])
    dashboard = soc_dashboard(empty_df)
    for name, table in dashboard.items():
        assert isinstance(table, pd.DataFrame)
        assert table.empty
