"""CityPulse dashboard: city_dashboard(...) returns a dict of tidy, print-ready DataFrames.

Run:  python dashboard.py            (prints every table)
Use:  from dashboard import city_dashboard
      tables = city_dashboard(traffic, sensors, weather, incidents)
"""
from __future__ import annotations

import sys

import pandas as pd

from analysis import (SEVERITY_SCORE, find_data_dir, integrate_data, load_data,
                      time_series_report, traffic_hotspots, weather_comparison)


def city_dashboard(traffic, sensors, weather, incidents) -> dict[str, pd.DataFrame]:
    data, report = integrate_data(traffic, sensors, weather, incidents, verbose=False)
    hot = traffic_hotspots(data, incidents, sensors)
    ts = time_series_report(data)

    by_district = (hot["by_district"]
                   [["district", "total_vehicles", "avg_hourly_vehicles", "avg_speed_kmh",
                     "speed_pct_of_limit", "observations"]]
                   .merge(hot["incidents_by_district"][["district", "incidents"]],
                          on="district", how="left", validate="one_to_one")
                   .merge(hot["peak_gap"][["district", "peak_minus_off_peak"]],
                          on="district", how="left", validate="one_to_one"))

    by_road = hot["by_road"][["road_name", "district", "road_type", "avg_hourly_vehicles",
                              "avg_speed_kmh", "speed_limit_kmh", "incidents", "avg_severity_score"]]

    by_hour = ts["by_hour"].rename(columns={"total_vehicles": "citywide_vehicles"})

    daily = ts["daily"].reset_index().rename(columns={"timestamp": "date"})
    daily_trend = daily[["date", "day_name", "total_vehicles", "vehicles_3day_ma",
                         "vehicles_pct_change", "avg_speed_kmh", "speed_3day_ma"]]

    inc = hot["incidents_labelled"]
    incident_summary = (inc.pivot_table(index="incident_type", columns="severity", values="incident_id",
                                        aggfunc="size", fill_value=0)
                        .reindex(columns=list(SEVERITY_SCORE), fill_value=0))
    incident_summary["total"] = incident_summary.sum(axis=1)
    incident_summary = incident_summary.sort_values("total", ascending=False).reset_index()
    incident_summary.columns.name = None

    data_quality = pd.DataFrame([
        {"check": "traffic rows before / after integration", "value": f"{len(traffic):,} / {len(data):,}"},
        {"check": "missing weather observations (district-hours)", "value": len(report["missing_weather_keys"])},
        {"check": "traffic rows with no weather match", "value": int((data["weather_match"] == "left_only").sum())},
        {"check": "incidents matched to a traffic reading", "value": int(data["has_incident"].sum())},
        {"check": "incidents with unknown sensor_id",
         "value": ", ".join(report["unknown_sensor_incidents"]["incident_id"])},
    ])

    return {
        "by_district": by_district,
        "by_road": by_road,
        "by_hour": by_hour,
        "daily_trend": daily_trend,
        "incident_summary": incident_summary,
        "weather_comparison": weather_comparison(data),
        "data_quality": data_quality,
    }


if __name__ == "__main__":
    pd.set_option("display.width", 160)
    frames = load_data(find_data_dir(sys.argv[1] if len(sys.argv) > 1 else None))
    for name, table in city_dashboard(*frames).items():
        print(f"\n=== {name} ({len(table)} rows) ===")
        print(table.to_string(index=False))
