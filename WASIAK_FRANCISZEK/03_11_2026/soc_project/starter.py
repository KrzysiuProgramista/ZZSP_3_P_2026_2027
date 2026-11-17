"""SOC Analyst project - completed solution."""
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).with_name("soc_incidents.csv")


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["event_date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    return df


def attack_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("attack_type")
        .agg(
            incidents=("incident_id", "count"),
            unique_sources=("source_ip", "nunique"),
            avg_response_min=("response_time_min", "mean"),
            blocked_rate=("blocked", "mean"),
            compromise_rate=("compromised", "mean"),
        )
        .reset_index()
        .sort_values("incidents", ascending=False)
        .reset_index(drop=True)
    )


def add_group_context(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    g = out.groupby("attack_type")
    out["attack_avg_response"] = g["response_time_min"].transform("mean")
    out["response_vs_attack_avg"] = out["response_time_min"] - out["attack_avg_response"]
    out["above_attack_avg_severity"] = out["severity_score"] > g["severity_score"].transform("mean")
    # agg() collapses each group to ONE row (shape = n_groups);
    # transform() returns a result aligned to the original index (shape = n_rows).
    return out


def _empty_dashboard() -> dict[str, pd.DataFrame]:
    cols = {
        "by_attack": ["attack_type", "incidents", "unique_sources", "avg_response_min", "blocked_rate", "compromise_rate"],
        "by_country": ["source_country", "incidents", "critical_emergency", "unique_assets", "blocked_rate"],
        "by_asset": ["target_asset", "incidents", "compromised", "avg_severity_score", "avg_response_min"],
        "by_hour": ["hour", "incidents", "avg_severity_score", "avg_response_min"],
        "top_sources": ["source_ip", "incidents", "unique_targets", "compromised"],
        "daily_trend": ["event_date", "incidents", "compromised"],
    }
    return {k: pd.DataFrame(columns=v) for k, v in cols.items()}


def soc_dashboard(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if df is None or df.empty:
        return _empty_dashboard()
    d = df.copy()  # never mutate the input
    d["timestamp"] = pd.to_datetime(d["timestamp"], errors="coerce")
    d["hour"] = d["timestamp"].dt.hour
    d["event_date"] = d["timestamp"].dt.date
    d["is_crit"] = d["severity"].isin(["Critical", "Emergency"])

    by_country = (
        d.groupby("source_country")
        .agg(
            incidents=("incident_id", "count"),
            critical_emergency=("is_crit", "sum"),
            unique_assets=("target_asset", "nunique"),
            blocked_rate=("blocked", "mean"),
        )
        .reset_index()
        .sort_values("incidents", ascending=False)
        .reset_index(drop=True)
    )
    by_asset = (
        d.groupby("target_asset")
        .agg(
            incidents=("incident_id", "count"),
            compromised=("compromised", "sum"),
            avg_severity_score=("severity_score", "mean"),
            avg_response_min=("response_time_min", "mean"),
        )
        .reset_index()
        .sort_values("incidents", ascending=False)
        .reset_index(drop=True)
    )
    by_hour = (
        d.groupby("hour")
        .agg(
            incidents=("incident_id", "count"),
            avg_severity_score=("severity_score", "mean"),
            avg_response_min=("response_time_min", "mean"),
        )
        .reset_index()
        .sort_values("hour")
        .reset_index(drop=True)
    )
    top_sources = (
        d.groupby("source_ip")
        .agg(
            incidents=("incident_id", "count"),
            unique_targets=("target_asset", "nunique"),
            compromised=("compromised", "sum"),
        )
        .reset_index()
        .sort_values(["incidents", "source_ip"], ascending=[False, True])
        .head(5)
        .reset_index(drop=True)
    )
    daily_trend = (
        d.groupby("event_date")
        .agg(incidents=("incident_id", "count"), compromised=("compromised", "sum"))
        .reset_index()
        .sort_values("event_date")
        .reset_index(drop=True)
    )
    return {
        "by_attack": attack_summary(d),
        "by_country": by_country,
        "by_asset": by_asset,
        "by_hour": by_hour,
        "top_sources": top_sources,
        "daily_trend": daily_trend,
    }


if __name__ == "__main__":
    events = load_data()
    print(events.head())
    print("Rows:", len(events))
    dashboard = soc_dashboard(events)
    for name, table in dashboard.items():
        print(f"\n=== {name} ===")
        print(table.to_string(index=False))
