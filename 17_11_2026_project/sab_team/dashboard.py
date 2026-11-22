"""CityPulse — sab_team dashboard.

Usage:
    python dashboard.py            # prints every dashboard table
    from dashboard import load_data, integrate_data, city_dashboard
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"

SEVERITY_SCORE = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
PEAK_HOURS = [7, 8, 9, 16, 17, 18]  # morning + evening rush, see by_hour table


def load_data(data_dir=DATA_DIR):
    """Load the four raw CSV files (they are never modified)."""
    traffic = pd.read_csv(data_dir / "traffic.csv", parse_dates=["timestamp"])
    sensors = pd.read_csv(data_dir / "sensors.csv")
    weather = pd.read_csv(data_dir / "weather.csv", parse_dates=["timestamp"])
    incidents = pd.read_csv(data_dir / "incidents.csv", parse_dates=["timestamp"])
    return traffic, sensors, weather, incidents


def integrate_data(traffic, sensors, weather, incidents, verbose=True):
    """Left-join everything onto traffic. Returns (integrated, merge_report)."""
    # Key checks: every right-hand table must be unique on its join key.
    assert not traffic.duplicated(["timestamp", "sensor_id"]).any()
    assert sensors["sensor_id"].is_unique
    assert not weather.duplicated(["timestamp", "district"]).any()
    assert not incidents.duplicated(["timestamp", "sensor_id"]).any()

    report = {"traffic_rows": len(traffic)}

    step1 = traffic.merge(sensors, on="sensor_id", how="left",
                          validate="many_to_one", indicator="sensor_match")
    step2 = step1.merge(weather, on=["timestamp", "district"], how="left",
                        validate="many_to_one", indicator="weather_match")
    step3 = step2.merge(incidents, on=["timestamp", "sensor_id"], how="left",
                        validate="one_to_one", indicator="incident_match")

    report["after_sensors"] = len(step1)
    report["after_weather"] = len(step2)
    report["after_incidents"] = len(step3)
    report["sensor_match"] = step1["sensor_match"].value_counts().to_dict()
    report["weather_match"] = step2["weather_match"].value_counts().to_dict()
    report["incident_match"] = step3["incident_match"].value_counts().to_dict()

    # Anti-joins: records that could not be attached to a traffic row.
    expected = traffic[["timestamp"]].drop_duplicates().merge(
        sensors[["district"]].drop_duplicates(), how="cross")
    missing_weather = expected.merge(weather, on=["timestamp", "district"],
                                     how="left", indicator=True)
    report["missing_weather_hours"] = missing_weather.loc[
        missing_weather["_merge"] == "left_only", ["timestamp", "district"]
    ].reset_index(drop=True)
    report["unknown_sensor_incidents"] = incidents[
        ~incidents["sensor_id"].isin(sensors["sensor_id"])].reset_index(drop=True)

    # No row explosion allowed: every step keeps exactly one row per traffic reading.
    assert len(step3) == len(traffic), "row count changed during integration"

    if verbose:
        print(f"traffic rows before:        {report['traffic_rows']}")
        print(f"after + sensors:            {report['after_sensors']}")
        print(f"after + weather:            {report['after_weather']}")
        print(f"after + incidents:          {report['after_incidents']}")
        print(f"weather hours missing:      {len(report['missing_weather_hours'])}")
        print(f"incidents, unknown sensor:  {len(report['unknown_sensor_incidents'])}")

    data = step3.sort_values(["timestamp", "sensor_id"]).reset_index(drop=True)
    data["date"] = data["timestamp"].dt.normalize()
    data["hour"] = data["timestamp"].dt.hour
    data["is_weekend"] = data["timestamp"].dt.day_of_week >= 5
    data["is_peak"] = data["hour"].isin(PEAK_HOURS)
    data["severity_score"] = data["severity"].map(SEVERITY_SCORE)
    return data, report


def city_dashboard(traffic, sensors, weather, incidents):
    """Return a dict of tidy, sorted DataFrames for the final briefing."""
    data, _ = integrate_data(traffic, sensors, weather, incidents, verbose=False)

    by_district = (data.groupby("district")
                   .agg(total_vehicles=("vehicle_count", "sum"),
                        avg_vehicles_per_hour=("vehicle_count", "mean"),
                        avg_speed_kmh=("avg_speed_kmh", "mean"),
                        observations=("sensor_id", "size"),
                        incidents=("incident_id", "count"))
                   .sort_values("total_vehicles", ascending=False)
                   .round(1).reset_index())

    by_road = (data.groupby(["road_name", "district", "road_type"])
               .agg(avg_vehicles=("vehicle_count", "mean"),
                    avg_speed_kmh=("avg_speed_kmh", "mean"),
                    speed_limit_kmh=("speed_limit_kmh", "first"),
                    incident_count=("incident_id", "count"),
                    avg_severity=("severity_score", "mean"))
               .sort_values("avg_vehicles", ascending=False)
               .round(2).reset_index())

    by_hour = (data.groupby("hour")
               .agg(total_vehicles=("vehicle_count", "sum"),
                    avg_speed_kmh=("avg_speed_kmh", "mean"))
               .round(1).reset_index())

    daily = data.set_index("timestamp").resample("D").agg(
        {"vehicle_count": "sum", "avg_speed_kmh": "mean"})
    daily_trend = pd.DataFrame({
        "daily_vehicles": daily["vehicle_count"],
        "avg_speed_kmh": daily["avg_speed_kmh"].round(2),
        "vehicles_3day_ma": daily["vehicle_count"].rolling(3).mean().round(0),
        "change_vs_prev_day": daily["vehicle_count"].diff(),
        "pct_change_vs_prev_day": (daily["vehicle_count"].pct_change() * 100).round(1),
    }).rename_axis("date").reset_index()

    # Use the raw incidents table so incidents on unknown sensors are still counted.
    incident_summary = (incidents.groupby(["incident_type", "severity"])
                        .size().unstack(fill_value=0)
                        .reindex(columns=list(SEVERITY_SCORE), fill_value=0))
    incident_summary["total"] = incident_summary.sum(axis=1)
    incident_summary = incident_summary.sort_values("total", ascending=False).reset_index()

    rain_band = pd.cut(data["rainfall_mm"], [-0.1, 0, 2, 5, float("inf")],
                       labels=["dry (0)", "light (0-2]", "moderate (2-5]", "heavy (>5)"])
    weather_comparison = (data.assign(rain_band=rain_band.astype(str))
                          .fillna({"weather_condition": "missing", "rain_band": "missing"})
                          .groupby(["weather_condition", "rain_band"])
                          .agg(observations=("sensor_id", "size"),
                               avg_vehicles=("vehicle_count", "mean"),
                               avg_speed_kmh=("avg_speed_kmh", "mean"))
                          .round(1).reset_index()
                          .sort_values("avg_speed_kmh", ascending=False))
    weather_comparison.loc[weather_comparison["weather_condition"] == "missing",
                           "rain_band"] = "missing"

    return {
        "by_district": by_district,
        "by_road": by_road,
        "by_hour": by_hour,
        "daily_trend": daily_trend,
        "incident_summary": incident_summary,
        "weather_comparison": weather_comparison,
    }


if __name__ == "__main__":
    tables = city_dashboard(*load_data())
    pd.set_option("display.width", 160)
    for name, table in tables.items():
        print(f"\n=== {name} ===")
        print(table.to_string(index=False))
