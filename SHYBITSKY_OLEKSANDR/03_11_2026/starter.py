"""SOC Analyst project — student starter code."""
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).with_name("soc_incidents.csv")


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the events and parse timestamp. Add any additional preparation."""
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["event_date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    return df


def attack_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return one row per attack type with useful SOC metrics."""
    if df.empty:
        return pd.DataFrame(columns=[
            'attack_type', 'incident_count', 'unique_source_ips',
            'avg_response_time', 'blocked_rate', 'compromise_rate'
        ])
    
    # Normalize 'compromised' column to boolean in case it's stored as string
    comp_series = df['compromised']
    if comp_series.dtype == object:
        comp_bool = comp_series.astype(str).str.lower() == 'true'
    else:
        comp_bool = comp_series.astype(bool)

    res = df.groupby('attack_type').agg(
        incident_count=('incident_id', 'count'),
        unique_source_ips=('source_ip', 'nunique'),
        avg_response_time=('response_time_min', 'mean'),
        blocked_rate=('blocked', 'mean'),
        compromise_rate=(
            'compromised',
            lambda x: (x.astype(str).str.lower() == 'true').mean()
            if x.dtype == object else x.astype(bool).mean()
        )
    ).reset_index()
    return res


def add_group_context(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy enriched with group-level context using transform."""
    out = df.copy()
    if out.empty:
        out['attack_avg_response'] = pd.Series(dtype=float)
        out['response_vs_attack_avg'] = pd.Series(dtype=float)
        out['above_attack_avg_severity'] = pd.Series(dtype=bool)
        return out

    # attack_avg_response using transform
    out['attack_avg_response'] = out.groupby('attack_type')['response_time_min'].transform('mean')
    
    # response_vs_attack_avg: difference between incident response time and attack-type average
    out['response_vs_attack_avg'] = out['response_time_min'] - out['attack_avg_response']
    
    # above_attack_avg_severity: Boolean showing whether severity_score is above its attack-type average
    attack_avg_severity = out.groupby('attack_type')['severity_score'].transform('mean')
    out['above_attack_avg_severity'] = out['severity_score'] > attack_avg_severity
    
    # Note on shape: agg() reduces rows (one row per group), whereas transform()
    # broadcasts the group aggregate back to match the original DataFrame's shape (row-for-row).
    return out


def soc_dashboard(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return the six tidy dashboard DataFrames described in the brief."""
    if df is None or df.empty:
        empty_cols = {
            "by_attack": ['attack_type', 'incident_count', 'unique_source_ips', 'avg_response_time', 'blocked_rate', 'compromise_rate'],
            "by_country": ['source_country', 'incident_count', 'critical_emergency_count', 'unique_target_assets', 'blocked_rate'],
            "by_asset": ['target_asset', 'incident_count', 'compromised_count', 'avg_severity_score', 'avg_response_time'],
            "by_hour": ['hour', 'incident_count', 'avg_severity_score', 'avg_response_time'],
            "top_sources": ['source_ip', 'incident_count', 'unique_targets', 'compromised_incidents'],
            "daily_trend": ['event_date', 'incident_count', 'compromise_count']
        }
        return {name: pd.DataFrame(columns=cols) for name, cols in empty_cols.items()}

    # Helper for boolean/string compromise conversion
    if df['compromised'].dtype == object:
        comp_cond = df['compromised'].astype(str).str.lower() == 'true'
    else:
        comp_cond = df['compromised'].astype(bool)

    # 1. by_attack
    by_attack = df.groupby('attack_type').agg(
        incident_count=('incident_id', 'count'),
        unique_source_ips=('source_ip', 'nunique'),
        avg_response_time=('response_time_min', 'mean'),
        blocked_rate=('blocked', 'mean'),
        compromise_rate=('compromised', lambda x: (x.astype(str).str.lower() == 'true').mean() if x.dtype == object else x.astype(bool).mean())
    ).reset_index()

    # 2. by_country
    crit_mask = df['severity'].astype(str).str.lower().isin(['critical', 'emergency'])
    by_country = df.groupby('source_country').agg(
        incident_count=('incident_id', 'count'),
        critical_emergency_count=('severity', lambda x: x.astype(str).str.lower().isin(['critical', 'emergency']).sum()),
        unique_target_assets=('target_asset', 'nunique'),
        blocked_rate=('blocked', 'mean')
    ).reset_index()

    # 3. by_asset
    by_asset = df.groupby('target_asset').agg(
        incident_count=('incident_id', 'count'),
        compromised_count=('compromised', lambda x: (x.astype(str).str.lower() == 'true').sum() if x.dtype == object else x.astype(bool).sum()),
        avg_severity_score=('severity_score', 'mean'),
        avg_response_time=('response_time_min', 'mean')
    ).reset_index()

    # 4. by_hour
    by_hour = df.groupby('hour').agg(
        incident_count=('incident_id', 'count'),
        avg_severity_score=('severity_score', 'mean'),
        avg_response_time=('response_time_min', 'mean')
    ).reset_index().sort_values('hour')

    # 5. top_sources
    top_sources = df.groupby('source_ip').agg(
        incident_count=('incident_id', 'count'),
        unique_targets=('target_asset', 'nunique'),
        compromised_incidents=('compromised', lambda x: (x.astype(str).str.lower() == 'true').sum() if x.dtype == object else x.astype(bool).sum())
    ).reset_index().sort_values(by='incident_count', ascending=False).head(5)

    # 6. daily_trend
    daily_trend = df.groupby('event_date').agg(
        incident_count=('incident_id', 'count'),
        compromise_count=('compromised', lambda x: (x.astype(str).str.lower() == 'true').sum() if x.dtype == object else x.astype(bool).sum())
    ).reset_index().sort_values('event_date')

    return {
        "by_attack": by_attack,
        "by_country": by_country,
        "by_asset": by_asset,
        "by_hour": by_hour,
        "top_sources": top_sources,
        "daily_trend": daily_trend
    }

if __name__ == "__main__":
  events = load_data()
  print(events.head())
  print("Rows:", len(events))

  dashboard = soc_dashboard(events)
  output_filename = "soc_dashboard_report.xlsx"

  with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
    for name, table in dashboard.items():
      sheet_name = str(name)[:31]
      table.to_excel(writer, sheet_name=sheet_name, index=False)

    events.to_excel(writer, sheet_name="All_Events", index=False)

  print(
      f"\nDashboard and full attack logs successfully saved to:"
      f" {output_filename}"
  )

