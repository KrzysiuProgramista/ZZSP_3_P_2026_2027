import pandas as pd
import pytest

def load_data(path="soc_incidents.csv"):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["event_date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    return df

def attack_summary(df):
    return df.groupby("attack_type").agg(
        incident_count=("incident_id", "count"),
        unique_ips=("source_ip", "nunique"),
        avg_response_time=("response_time_min", "mean"),
        blocked_rate=("blocked", "mean"),
        compromise_rate=("compromised", "mean")
    ).reset_index().sort_values("incident_count", ascending=False)

def add_group_context(df):
    out = df.copy()
    out["attack_avg_response"] = out.groupby("attack_type")["response_time_min"].transform("mean")
    out["response_vs_attack_avg"] = out["response_time_min"] - out["attack_avg_response"]
    
    avg_sev = out.groupby("attack_type")["severity_score"].transform("mean")
    out["above_attack_avg_severity"] = out["severity_score"] > avg_sev
    return out

def soc_dashboard(df):
    if len(df) == 0:
        return {
            "by_attack": pd.DataFrame(), "by_country": pd.DataFrame(), 
            "by_asset": pd.DataFrame(), "by_hour": pd.DataFrame(), 
            "top_sources": pd.DataFrame(), "daily_trend": pd.DataFrame()
        }

    by_attack = attack_summary(df)

    # by_country
    df_copy = df.copy()
    df_copy['is_crit'] = df_copy['severity'].isin(['Critical', 'Emergency'])
    by_country = df_copy.groupby("source_country").agg(
        incident_count=("incident_id", "count"),
        critical_count=("is_crit", "sum"),
        unique_assets=("target_asset", "nunique"),
        blocked_rate=("blocked", "mean")
    ).reset_index()

    # by_asset
    by_asset = df.groupby("target_asset").agg(
        incident_count=("incident_id", "count"),
        compromised_count=("compromised", "sum"),
        avg_severity=("severity_score", "mean"),
        avg_response_time=("response_time_min", "mean")
    ).reset_index()

    # by_hour
    by_hour = df.groupby("hour").agg(
        incident_count=("incident_id", "count"),
        avg_severity=("severity_score", "mean"),
        avg_response_time=("response_time_min", "mean")
    ).reset_index().sort_values("hour")

    # top_sources
    top_sources = df.groupby("source_ip").agg(
        incident_count=("incident_id", "count"),
        unique_targets=("target_asset", "nunique"),
        compromised_incidents=("compromised", "sum")
    ).reset_index().sort_values("incident_count", ascending=False).head(5)

    # daily_trend
    daily_trend = df.groupby("event_date").agg(
        daily_incident_count=("incident_id", "count"),
        daily_compromise_count=("compromised", "sum")
    ).reset_index().sort_values("event_date")

    return {
        "by_attack": by_attack,
        "by_country": by_country,
        "by_asset": by_asset,
        "by_hour": by_hour,
        "top_sources": top_sources,
        "daily_trend": daily_trend,
    }

# --- TESTY ---
def test_dashboard_type():
    res = soc_dashboard(pd.DataFrame())
    assert type(res) == dict

def test_dashboard_keys():
    res = soc_dashboard(pd.DataFrame())
    assert "by_attack" in res.keys()

def test_top_sources():
    df = pd.DataFrame({
        "incident_id": range(10),
        "source_ip": [f"1.1.1.{i}" for i in range(10)],
        "target_asset": ["Web"] * 10,
        "compromised": [False] * 10,
        "severity": ["Low"] * 10,
        "severity_score": [1] * 10,
        "attack_type": ["DDoS"] * 10,
        "response_time_min": [10] * 10,
        "blocked": [True] * 10,
        "source_country": ["Poland"] * 10,
        "hour": [12] * 10,
        "event_date": ["2026-09-01"] * 10
    })
    res = soc_dashboard(df)
    assert len(res["top_sources"]) == 5

def test_context_calc():
    df = pd.DataFrame({
        "attack_type": ["DDoS", "DDoS"],
        "response_time_min": [10, 30],
        "severity_score": [2, 4]
    })
    res = add_group_context(df)
    assert res["attack_avg_response"].iloc[0] == 20.0

def test_empty_df_handling():
    res = soc_dashboard(pd.DataFrame())
    assert res["by_attack"].empty

def test_attack_summary():
    df = pd.DataFrame({
        "incident_id": [1, 2], "attack_type": ["A", "A"],
        "source_ip": ["1.1", "1.2"], "response_time_min": [10, 20],
        "blocked": [True, False], "compromised": [False, True]
    })
    res = attack_summary(df)
    assert res["blocked_rate"].iloc[0] == 0.5

if __name__ == "__main__":
    df = load_data()
    dash = soc_dashboard(df)
    for name, table in dash.items():
        print(f"\n--- {name} ---")
        print(table.head())