"""SOC Analyst project: data loading, group context, dashboard tables and HTML report."""
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).with_name("soc_incidents.csv")
CRITICAL = ["Critical", "Emergency"]
REQUIRED = ["incident_id", "timestamp", "source_ip", "source_country", "target_asset",
            "attack_type", "severity", "severity_score", "response_time_min",
            "blocked", "compromised"]


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with datetime + event_date, hour, weekday columns (idempotent)."""
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    out["event_date"] = out["timestamp"].dt.date
    out["hour"] = out["timestamp"].dt.hour
    out["weekday"] = out["timestamp"].dt.day_name()
    return out


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the events and parse timestamp. Add event_date, hour and weekday."""
    return _prepare(pd.read_csv(path))


def attack_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return one row per attack type with useful SOC metrics."""
    return (
        df.groupby("attack_type")
        .agg(
            incidents=("incident_id", "count"),
            unique_source_ips=("source_ip", "nunique"),
            avg_response_min=("response_time_min", "mean"),
            median_response_min=("response_time_min", "median"),
            blocked_rate_pct=("blocked", lambda s: s.mean() * 100),
            compromise_rate_pct=("compromised", lambda s: s.mean() * 100),
        )
        .round(1)
        .reset_index()
        .sort_values("incidents", ascending=False, ignore_index=True)
    )


def add_group_context(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy enriched with group-level context using transform."""
    out = df.copy()
    by_attack = out.groupby("attack_type")
    out["attack_avg_response"] = by_attack["response_time_min"].transform("mean")
    out["response_vs_attack_avg"] = out["response_time_min"] - out["attack_avg_response"]
    out["above_attack_avg_severity"] = (
        out["severity_score"] > by_attack["severity_score"].transform("mean")
    )
    return out


def soc_dashboard(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return the six tidy dashboard DataFrames. Does not modify df.

    An empty DataFrame (with the right columns) gives six empty tables;
    a DataFrame missing required columns raises ValueError.
    """
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    d = _prepare(df)
    d["is_critical"] = d["severity"].isin(CRITICAL)

    by_attack = attack_summary(d).drop(columns="median_response_min")
    by_country = (
        d.groupby("source_country")
        .agg(
            incidents=("incident_id", "count"),
            critical_emergency=("is_critical", "sum"),
            unique_assets=("target_asset", "nunique"),
            blocked_rate_pct=("blocked", lambda s: round(s.mean() * 100, 1)),
        )
        .reset_index()
        .sort_values("incidents", ascending=False, ignore_index=True)
    )
    by_asset = (
        d.groupby("target_asset")
        .agg(
            incidents=("incident_id", "count"),
            compromised=("compromised", "sum"),
            avg_severity=("severity_score", "mean"),
            avg_response_min=("response_time_min", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("incidents", ascending=False, ignore_index=True)
    )
    by_hour = (
        d.groupby("hour")
        .agg(
            incidents=("incident_id", "count"),
            avg_severity=("severity_score", "mean"),
            avg_response_min=("response_time_min", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("hour", ignore_index=True)
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
        .sort_values("event_date", ignore_index=True)
    )
    return {
        "by_attack": by_attack,
        "by_country": by_country,
        "by_asset": by_asset,
        "by_hour": by_hour,
        "top_sources": top_sources,
        "daily_trend": daily_trend,
    }


if __name__ == "__main__":
    events = load_data()
    dashboard = soc_dashboard(events)
    out_dir = Path(__file__).with_name("output")
    out_dir.mkdir(exist_ok=True)
    for name, table in dashboard.items():
        print(f"\n=== {name} ===")
        print(table.to_string(index=False))
        table.to_csv(out_dir / f"{name}.csv", index=False)
    print(f"\nWrote six CSVs to {out_dir.name}/")
