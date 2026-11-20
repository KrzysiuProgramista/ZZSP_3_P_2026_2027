"""CityPulse Challenge — Complete Data Pipeline & Dashboard."""
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
SEVERITY_MAP = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
PEAK_HOURS = [7, 8, 9, 16, 17, 18]


def _resolve_data_dir(data_dir=DATA_DIR) -> Path:
    data_dir = Path(data_dir)
    if (data_dir / "traffic.csv").exists():
        return data_dir
    if Path("traffic.csv").exists():
        return Path(".")
    raise FileNotFoundError(f"Could not find CSV files in {data_dir} or current directory.")


def load_data(data_dir=DATA_DIR):
    """Load the four source datasets and parse timestamp columns."""
    base = _resolve_data_dir(data_dir)
    traffic = pd.read_csv(base / "traffic.csv", parse_dates=["timestamp"])
    sensors = pd.read_csv(base / "sensors.csv")
    weather = pd.read_csv(base / "weather.csv", parse_dates=["timestamp"])
    incidents = pd.read_csv(base / "incidents.csv", parse_dates=["timestamp"])
    return traffic, sensors, weather, incidents


def integrate_data(traffic, sensors, weather, incidents, verbose=True):
    """Build one analysis-ready table and return (integrated_df, merge_reports)."""
    reports = {}

    # Key uniqueness checks
    reports["key_uniqueness"] = {
        "traffic_(timestamp,sensor_id)": not traffic.duplicated(["timestamp", "sensor_id"]).any(),
        "sensors_sensor_id": not sensors.duplicated(["sensor_id"]).any(),
        "weather_(timestamp,district)": not weather.duplicated(["timestamp", "district"]).any(),
        "incidents_incident_id": not incidents.duplicated(["incident_id"]).any(),
        "incidents_(timestamp,sensor_id)": not incidents.duplicated(["timestamp", "sensor_id"]).any(),
    }

    # Unknown sensor IDs in incidents
    unknown_sensor_incidents = incidents[~incidents["sensor_id"].isin(sensors["sensor_id"])].copy()
    reports["unknown_sensor_incidents"] = unknown_sensor_incidents

    # 1. Traffic + Sensors
    before_1 = len(traffic)
    step1 = traffic.merge(
        sensors,
        on="sensor_id",
        how="left",
        validate="many_to_one",
        indicator="sensor_match",
    )
    after_1 = len(step1)
    reports["traffic_sensors"] = {
        "before": before_1,
        "after": after_1,
        "match_counts": step1["sensor_match"].value_counts().to_dict(),
    }

    # 2. + Weather
    before_2 = len(step1)
    step2 = step1.merge(
        weather,
        on=["timestamp", "district"],
        how="left",
        validate="many_to_one",
        indicator="weather_match",
    )
    after_2 = len(step2)
    missing_weather_keys = (
        step2.loc[step2["weather_match"] == "left_only", ["timestamp", "district"]]
        .drop_duplicates()
    )
    reports["traffic_weather"] = {
        "before": before_2,
        "after": after_2,
        "match_counts": step2["weather_match"].value_counts().to_dict(),
        "missing_weather_district_hours": len(missing_weather_keys),
    }

    # 3. + Incidents
    before_3 = len(step2)
    inc_validate = (
        "one_to_one"
        if reports["key_uniqueness"]["incidents_(timestamp,sensor_id)"]
        else "one_to_many"
    )
    integrated = step2.merge(
        incidents,
        on=["timestamp", "sensor_id"],
        how="left",
        validate=inc_validate,
        indicator="incident_match",
    )
    after_3 = len(integrated)
    reports["traffic_incidents"] = {
        "before": before_3,
        "after": after_3,
        "validate": inc_validate,
        "match_counts": integrated["incident_match"].value_counts().to_dict(),
        "total_incidents_source": len(incidents),
        "matched_incidents": int((integrated["incident_match"] == "both").sum()),
        "unmatched_incidents_count": len(unknown_sensor_incidents),
    }

    # Helper time & severity columns
    integrated = integrated.sort_values(["timestamp", "sensor_id"]).reset_index(drop=True)
    integrated["hour"] = integrated["timestamp"].dt.hour
    integrated["date"] = integrated["timestamp"].dt.date
    integrated["day_of_week"] = integrated["timestamp"].dt.day_name()
    integrated["is_weekend"] = integrated["timestamp"].dt.dayofweek >= 5
    integrated["period"] = np.where(integrated["hour"].isin(PEAK_HOURS), "peak", "off_peak")
    integrated["severity_score"] = integrated["severity"].map(SEVERITY_MAP)

    if verbose:
        print(f"[Merge 1: traffic + sensors]   before={before_1}, after={after_1}, matches={reports['traffic_sensors']['match_counts']}")
        print(f"[Merge 2: + weather]           before={before_2}, after={after_2}, matches={reports['traffic_weather']['match_counts']} ({len(missing_weather_keys)} missing district-hours)")
        print(f"[Merge 3: + incidents]         before={before_3}, after={after_3}, matches={reports['traffic_incidents']['match_counts']}")
        print(f"[Integrity] Orphan incidents with unknown sensor_id: {len(unknown_sensor_incidents)} -> {unknown_sensor_incidents['sensor_id'].tolist()}")

    return integrated, reports


def traffic_hotspots(integrated):
    """Return tidy DataFrames with district and road rankings."""
    peak_pivot = (
        integrated.pivot_table(
            index="district",
            columns="period",
            values="vehicle_count",
            aggfunc="mean",
        )
        .rename(columns={"peak": "peak_avg_vehicles", "off_peak": "off_peak_avg_vehicles"})
    )
    peak_pivot["peak_vs_off_peak_diff"] = (
        peak_pivot["peak_avg_vehicles"] - peak_pivot["off_peak_avg_vehicles"]
    )

    by_district = (
        integrated.groupby("district")
        .agg(
            avg_vehicles=("vehicle_count", "mean"),
            total_vehicles=("vehicle_count", "sum"),
            avg_speed_kmh=("avg_speed_kmh", "mean"),
            incident_count=("incident_id", "count"),
            avg_severity=("severity_score", "mean"),
            observations=("sensor_id", "size"),
        )
        .join(peak_pivot)
        .sort_values("avg_vehicles", ascending=False)
        .reset_index()
    )

    by_road = (
        integrated.groupby(["sensor_id", "road_name", "district", "road_type", "speed_limit_kmh"])
        .agg(
            avg_vehicles=("vehicle_count", "mean"),
            total_vehicles=("vehicle_count", "sum"),
            avg_speed_kmh=("avg_speed_kmh", "mean"),
            incident_count=("incident_id", "count"),
            avg_severity=("severity_score", "mean"),
        )
        .sort_values("avg_vehicles", ascending=False)
        .reset_index()
    )

    return {
        "by_district": by_district,
        "by_road": by_road,
        "slowest_roads": by_road.sort_values("avg_speed_kmh", ascending=True).reset_index(drop=True),
        "highest_severity_roads": by_road.sort_values(
            ["avg_severity", "incident_count"], ascending=[False, False]
        ).reset_index(drop=True),
    }


def time_series_report(integrated):
    """Return daily and hourly trends, rolling averages, period changes, and weekday vs weekend."""
    ts = integrated.sort_values("timestamp")

    daily_trend = (
        ts.set_index("timestamp")
        .resample("D")
        .agg(
            daily_vehicles=("vehicle_count", "sum"),
            daily_avg_speed_kmh=("avg_speed_kmh", "mean"),
            daily_incidents=("incident_id", "count"),
        )
    )
    daily_trend["vehicles_ma3"] = daily_trend["daily_vehicles"].rolling(3).mean()
    daily_trend["speed_ma3"] = daily_trend["daily_avg_speed_kmh"].rolling(3).mean()
    daily_trend["vehicles_diff"] = daily_trend["daily_vehicles"].diff()
    daily_trend["vehicles_pct_change"] = daily_trend["daily_vehicles"].pct_change() * 100
    daily_trend["speed_diff"] = daily_trend["daily_avg_speed_kmh"].diff()
    daily_trend["speed_pct_change"] = daily_trend["daily_avg_speed_kmh"].pct_change() * 100
    daily_trend["day_name"] = daily_trend.index.day_name()
    daily_trend = daily_trend.reset_index()

    daily_speed_by_district = (
        ts.groupby([pd.Grouper(key="timestamp", freq="D"), "district"])["avg_speed_kmh"]
        .mean()
        .unstack("district")
        .reset_index()
    )

    by_hour = (
        ts.groupby("hour")
        .agg(
            total_vehicles=("vehicle_count", "sum"),
            avg_vehicles_per_sensor=("vehicle_count", "mean"),
            avg_speed_kmh=("avg_speed_kmh", "mean"),
            incident_count=("incident_id", "count"),
        )
        .reset_index()
    )

    weekday_vs_weekend = (
        ts.assign(day_type=np.where(ts["is_weekend"], "Weekend", "Weekday"))
        .groupby("day_type")
        .agg(
            avg_vehicles_per_sensor=("vehicle_count", "mean"),
            avg_speed_kmh=("avg_speed_kmh", "mean"),
            total_incidents=("incident_id", "count"),
            observations=("sensor_id", "size"),
        )
        .reset_index()
    )

    return {
        "daily_trend": daily_trend,
        "daily_speed_by_district": daily_speed_by_district,
        "by_hour": by_hour,
        "weekday_vs_weekend": weekday_vs_weekend,
    }


def investigate_mystery(integrated):
    """Compare 12 Nov 2026 in Riverside (07:00-12:00) against nearby weekdays baseline."""
    event_date = pd.to_datetime("2026-11-12").date()
    baseline_dates = pd.to_datetime(
        ["2026-11-05", "2026-11-06", "2026-11-09", "2026-11-10", "2026-11-11", "2026-11-13"]
    ).date
    anomaly_hours = [7, 8, 9, 10, 11, 12]

    # 1. District-level scan on 2026-11-12 vs baseline dates
    ev_day = integrated[integrated["date"] == event_date]
    bs_days = integrated[integrated["date"].isin(baseline_dates)]

    district_scan = pd.DataFrame(
        {
            "nov12_avg_speed": ev_day.groupby("district")["avg_speed_kmh"].mean(),
            "baseline_avg_speed": bs_days.groupby("district")["avg_speed_kmh"].mean(),
        }
    )
    district_scan["speed_drop_pct"] = (
        (district_scan["baseline_avg_speed"] - district_scan["nov12_avg_speed"])
        / district_scan["baseline_avg_speed"]
        * 100
    )
    district_scan = district_scan.sort_values("speed_drop_pct", ascending=False).reset_index()

    # 2. Hourly comparison for Riverside
    riv_ev = ev_day[ev_day["district"] == "Riverside"]
    riv_bs = bs_days[bs_days["district"] == "Riverside"]

    hourly_comparison = pd.DataFrame(
        {
            "event_speed_kmh": riv_ev.groupby("hour")["avg_speed_kmh"].mean(),
            "baseline_speed_kmh": riv_bs.groupby("hour")["avg_speed_kmh"].mean(),
            "event_vehicles": riv_ev.groupby("hour")["vehicle_count"].mean(),
            "baseline_vehicles": riv_bs.groupby("hour")["vehicle_count"].mean(),
            "rainfall_mm": riv_ev.groupby("hour")["rainfall_mm"].mean(),
            "wind_speed_kmh": riv_ev.groupby("hour")["wind_speed_kmh"].mean(),
            "weather_condition": riv_ev.groupby("hour")["weather_condition"].first(),
            "incidents": riv_ev.groupby("hour")["incident_id"].count(),
        }
    )
    hourly_comparison["speed_drop_pct"] = (
        (hourly_comparison["baseline_speed_kmh"] - hourly_comparison["event_speed_kmh"])
        / hourly_comparison["baseline_speed_kmh"]
        * 100
    )
    hourly_comparison = hourly_comparison.reset_index()

    # 3. Affected roads in Riverside during 07:00-12:00
    win_ev = riv_ev[riv_ev["hour"].isin(anomaly_hours)]
    win_bs = riv_bs[riv_bs["hour"].isin(anomaly_hours)]

    road_impact = (
        win_ev.groupby(["sensor_id", "road_name", "road_type"])
        .agg(
            event_speed_kmh=("avg_speed_kmh", "mean"),
            event_vehicles=("vehicle_count", "mean"),
            incidents=("incident_id", "count"),
        )
        .join(
            win_bs.groupby(["sensor_id", "road_name", "road_type"]).agg(
                baseline_speed_kmh=("avg_speed_kmh", "mean"),
                baseline_vehicles=("vehicle_count", "mean"),
            )
        )
    )
    road_impact["speed_drop_pct"] = (
        (road_impact["baseline_speed_kmh"] - road_impact["event_speed_kmh"])
        / road_impact["baseline_speed_kmh"]
        * 100
    )
    road_impact["vehicle_drop_pct"] = (
        (road_impact["baseline_vehicles"] - road_impact["event_vehicles"])
        / road_impact["baseline_vehicles"]
        * 100
    )
    road_impact = road_impact.sort_values("speed_drop_pct", ascending=False).reset_index()

    # 4. Incidents & weather in the anomaly window
    window_incidents = win_ev[win_ev["incident_id"].notna()][
        [
            "timestamp",
            "sensor_id",
            "road_name",
            "incident_id",
            "incident_type",
            "severity",
            "duration_min",
            "lanes_blocked",
        ]
    ].reset_index(drop=True)

    window_weather = win_ev[
        ["timestamp", "temperature_c", "rainfall_mm", "wind_speed_kmh", "weather_condition"]
    ].drop_duplicates().reset_index(drop=True)

    overall_event_speed = float(win_ev["avg_speed_kmh"].mean())
    overall_base_speed = float(win_bs["avg_speed_kmh"].mean())
    overall_drop_pct = (overall_base_speed - overall_event_speed) / overall_base_speed * 100

    return {
        "affected_district": "Riverside",
        "affected_window": "2026-11-12 07:00-12:59",
        "overall_event_speed_kmh": round(overall_event_speed, 2),
        "overall_baseline_speed_kmh": round(overall_base_speed, 2),
        "overall_speed_drop_pct": round(overall_drop_pct, 2),
        "district_scan": district_scan,
        "hourly_comparison": hourly_comparison,
        "road_impact": road_impact,
        "window_incidents": window_incidents,
        "window_weather": window_weather,
    }


def city_dashboard(traffic, sensors, weather, incidents):
    """Return a dict of tidy DataFrames for the final briefing."""
    integrated, merge_reports = integrate_data(
        traffic, sensors, weather, incidents, verbose=False
    )
    hotspots = traffic_hotspots(integrated)
    ts = time_series_report(integrated)

    incident_summary = (
        integrated[integrated["incident_id"].notna()]
        .groupby(["incident_type", "severity"])
        .agg(
            incident_count=("incident_id", "count"),
            avg_duration_min=("duration_min", "mean"),
            avg_lanes_blocked=("lanes_blocked", "mean"),
        )
        .sort_values("incident_count", ascending=False)
        .reset_index()
    )

    weather_comparison = (
        integrated.dropna(subset=["weather_condition"])
        .groupby("weather_condition")
        .agg(
            observations=("sensor_id", "size"),
            avg_vehicles=("vehicle_count", "mean"),
            avg_speed_kmh=("avg_speed_kmh", "mean"),
            incident_count=("incident_id", "count"),
        )
        .sort_values("avg_speed_kmh", ascending=True)
        .reset_index()
    )

    return {
        "by_district": hotspots["by_district"][
            ["district", "total_vehicles", "avg_vehicles", "avg_speed_kmh", "incident_count", "observations"]
        ],
        "by_road": hotspots["by_road"][
            ["sensor_id", "road_name", "district", "avg_vehicles", "avg_speed_kmh", "incident_count", "avg_severity"]
        ],
        "by_hour": ts["by_hour"],
        "daily_trend": ts["daily_trend"][
            ["timestamp", "daily_vehicles", "daily_avg_speed_kmh", "vehicles_ma3", "speed_ma3", "vehicles_pct_change"]
        ],
        "incident_summary": incident_summary,
        "weather_comparison": weather_comparison,
        "merge_reports": merge_reports,
    }


if __name__ == "__main__":
    frames = load_data()
    integrated, reports = integrate_data(*frames, verbose=True)
    dash = city_dashboard(*frames)
    print("\n=== DASHBOARD TABLES READY ===")
    for k, v in dash.items():
        if isinstance(v, pd.DataFrame):
            print(f"- {k}: shape={v.shape}")