"""CityPulse Challenge: full reproducible analysis (Rounds 1-4, plus inputs for Round 5).

Run:  python analysis.py            (looks for ./data, then ../data)
      python analysis.py path/to/data

Every printed answer comes from a DataFrame computed below. Tables are saved to
outputs/tables/*.csv and charts to outputs/charts/*.png. The raw CSVs are only read.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"

# Documented choices -----------------------------------------------------------
SEVERITY_SCORE = {"low": 1, "moderate": 2, "high": 3, "critical": 4}  # ordinal, equal steps
PEAK_HOURS = [7, 8, 9, 16, 17, 18]          # morning and evening rush (confirmed by by_hour below)
OFF_PEAK_HOURS = [h for h in range(24) if h not in PEAK_HOURS]
MYSTERY_DATE = pd.Timestamp("2026-11-12")

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)


def find_data_dir(arg: str | None = None) -> Path:
    candidates = [Path(arg)] if arg else [HERE / "data", HERE.parent / "data"]
    for c in candidates:
        if (c / "traffic.csv").exists():
            return c
    raise FileNotFoundError(f"traffic.csv not found in {[str(c) for c in candidates]}")


def section(title: str) -> None:
    print("\n" + "=" * 100 + f"\n{title}\n" + "=" * 100)


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
def load_data(data_dir: Path):
    traffic = pd.read_csv(data_dir / "traffic.csv", parse_dates=["timestamp"])
    sensors = pd.read_csv(data_dir / "sensors.csv")
    weather = pd.read_csv(data_dir / "weather.csv", parse_dates=["timestamp"])
    incidents = pd.read_csv(data_dir / "incidents.csv", parse_dates=["timestamp"])
    return traffic, sensors, weather, incidents


# ----------------------------------------------------------------------------
# ROUND 1: Data integration
# ----------------------------------------------------------------------------
def key_report(df: pd.DataFrame, keys: list[str], name: str) -> dict:
    dupes = int(df.duplicated(keys).sum())
    return {"table": name, "key": " + ".join(keys), "rows": len(df), "duplicate_keys": dupes,
            "key_is_unique": dupes == 0}


def integrate_data(traffic, sensors, weather, incidents, verbose: bool = True):
    """Return (integrated traffic table, merge-report dict). Traffic grain is preserved."""
    log = print if verbose else (lambda *a, **k: None)
    report: dict = {}

    # 1. Key uniqueness checks before any merge
    keys = pd.DataFrame([
        key_report(traffic, ["timestamp", "sensor_id"], "traffic"),
        key_report(sensors, ["sensor_id"], "sensors"),
        key_report(weather, ["timestamp", "district"], "weather"),
        key_report(incidents, ["incident_id"], "incidents (id)"),
        key_report(incidents, ["timestamp", "sensor_id"], "incidents (join key)"),
    ])
    report["key_checks"] = keys
    log("Key uniqueness checks:\n", keys.to_string(index=False))

    # 2. traffic + sensors  (many traffic rows -> one sensor row)
    before = len(traffic)
    data = traffic.merge(sensors, on="sensor_id", how="left", validate="many_to_one",
                         indicator="sensor_match")
    log(f"\n[merge 1] traffic + sensors: before={before:,}  after={len(data):,}")
    sensor_counts = data["sensor_match"].value_counts()
    log(sensor_counts.to_string())
    assert len(data) == before, "row count changed in traffic+sensors merge"

    # 3. + weather on (timestamp, district)  (many sensors per district-hour -> one weather row)
    before = len(data)
    data = data.merge(weather, on=["timestamp", "district"], how="left", validate="many_to_one",
                      indicator="weather_match")
    log(f"\n[merge 2] + weather: before={before:,}  after={len(data):,}")
    weather_counts = data["weather_match"].value_counts()
    log(weather_counts.to_string())
    assert len(data) == before, "row count changed in weather merge"

    missing_weather = (data.loc[data["weather_match"] == "left_only", ["timestamp", "district"]]
                       .drop_duplicates().sort_values(["district", "timestamp"]))
    expected_weather = traffic["timestamp"].nunique() * sensors["district"].nunique()
    log(f"Weather grid expected {expected_weather:,} district-hours, file has {len(weather):,} "
        f"-> {expected_weather - len(weather)} missing observations "
        f"-> {int((data['weather_match'] == 'left_only').sum())} traffic rows with no weather "
        f"(3 sensors per district).")

    # 4. + incidents on (timestamp, sensor_id)  (join key checked unique above -> one_to_one)
    inc = incidents.rename(columns={"timestamp": "incident_timestamp"}).copy()
    inc["timestamp"] = inc["incident_timestamp"]
    before = len(data)
    data = data.merge(inc.drop(columns="incident_timestamp"), on=["timestamp", "sensor_id"],
                      how="left", validate="one_to_one", indicator="incident_match")
    log(f"\n[merge 3] + incidents: before={before:,}  after={len(data):,}")
    log(data["incident_match"].value_counts().to_string())
    assert len(data) == before, "row count changed in incident merge"

    # 5. Anti-joins: incidents that never reached the traffic table
    unknown_sensor = incidents.loc[~incidents["sensor_id"].isin(sensors["sensor_id"])]
    inc_check = incidents.merge(traffic[["timestamp", "sensor_id"]], on=["timestamp", "sensor_id"],
                                how="left", validate="one_to_one", indicator="traffic_match")
    unmatched_incidents = inc_check.loc[inc_check["traffic_match"] == "left_only"]
    log(f"\nIncidents with a sensor_id not in sensors.csv: {len(unknown_sensor)}")
    log(unknown_sensor.to_string(index=False))
    log(f"Incidents with no matching traffic observation: {len(unmatched_incidents)} "
        f"(same rows: {set(unmatched_incidents['incident_id']) == set(unknown_sensor['incident_id'])})")

    for c in ["sensor_match", "weather_match", "incident_match"]:
        data[c] = data[c].astype(str)
    data["has_incident"] = data["incident_match"].eq("both")
    data["severity_score"] = data["severity"].map(SEVERITY_SCORE)
    data["date"] = data["timestamp"].dt.normalize()
    data["hour"] = data["timestamp"].dt.hour
    data["day_name"] = data["timestamp"].dt.day_name()
    data["is_weekend"] = data["timestamp"].dt.day_of_week >= 5
    data["period"] = data["hour"].isin(PEAK_HOURS).map({True: "peak", False: "off_peak"})

    report.update({
        "merge_row_counts": pd.DataFrame([
            {"step": "traffic (raw)", "rows": len(traffic)},
            {"step": "+ sensors (left, many_to_one)", "rows": len(traffic)},
            {"step": "+ weather (left, many_to_one)", "rows": len(traffic)},
            {"step": "+ incidents (left, one_to_one)", "rows": len(data)},
        ]),
        "sensor_match": sensor_counts.rename_axis("sensor_match").reset_index(name="rows"),
        "weather_match": weather_counts.rename_axis("weather_match").reset_index(name="rows"),
        "missing_weather_keys": missing_weather,
        "unknown_sensor_incidents": unknown_sensor,
        "unmatched_incidents": unmatched_incidents.drop(columns="traffic_match"),
    })
    return data, report


def duplicate_key_demo(traffic, sensors) -> pd.DataFrame:
    """Round 1 Q4: what a duplicated right-hand key does to a merge."""
    bad = pd.concat([sensors, sensors[sensors["sensor_id"] == "S-001"]], ignore_index=True)
    no_validate = traffic.merge(bad, on="sensor_id", how="left")
    try:
        traffic.merge(bad, on="sensor_id", how="left", validate="many_to_one")
        caught = "not caught"
    except pd.errors.MergeError as e:
        caught = f"MergeError: {str(e).splitlines()[0]}"
    return pd.DataFrame([
        {"scenario": "clean sensors table", "rows_after_merge": len(traffic)},
        {"scenario": "S-001 duplicated, no validate=", "rows_after_merge": len(no_validate)},
        {"scenario": "S-001 duplicated, validate='many_to_one'", "rows_after_merge": caught},
    ])


# ----------------------------------------------------------------------------
# ROUND 2: Hotspots
# ----------------------------------------------------------------------------
def traffic_hotspots(data: pd.DataFrame, incidents: pd.DataFrame, sensors: pd.DataFrame) -> dict:
    # Speed as % of the posted limit: separates "slow because the limit is low" from congestion
    data = data.assign(speed_pct_of_limit=data["avg_speed_kmh"] / data["speed_limit_kmh"] * 100)
    by_district = (data.groupby("district")
                   .agg(avg_hourly_vehicles=("vehicle_count", "mean"),
                        avg_speed_kmh=("avg_speed_kmh", "mean"),
                        speed_pct_of_limit=("speed_pct_of_limit", "mean"),
                        total_vehicles=("vehicle_count", "sum"),
                        observations=("sensor_id", "size"),
                        sensors=("sensor_id", "nunique"))
                   .round(2).sort_values("avg_hourly_vehicles", ascending=False).reset_index())

    slowest_districts = by_district.sort_values("avg_speed_kmh")[["district", "avg_speed_kmh"]]

    # Incidents counted from the incidents table itself (not the traffic join) so nothing is lost;
    # the 3 unknown-sensor incidents get an explicit "Unknown sensor" label.
    inc = incidents.merge(sensors, on="sensor_id", how="left", validate="many_to_one",
                          indicator="sensor_match")
    inc["district"] = inc["district"].fillna("Unknown sensor")
    inc["road_name"] = inc["road_name"].fillna("Unknown sensor")
    inc["severity_score"] = inc["severity"].map(SEVERITY_SCORE)

    incidents_by_district = (inc.groupby("district")
                             .agg(incidents=("incident_id", "size"),
                                  avg_severity_score=("severity_score", "mean"),
                                  total_duration_min=("duration_min", "sum"))
                             .round(2).sort_values("incidents", ascending=False).reset_index())

    by_road = (data.groupby(["road_name", "district", "road_type"])
               .agg(avg_hourly_vehicles=("vehicle_count", "mean"),
                    avg_speed_kmh=("avg_speed_kmh", "mean"),
                    speed_limit_kmh=("speed_limit_kmh", "first"))
               .reset_index())
    by_road["speed_pct_of_limit"] = by_road["avg_speed_kmh"] / by_road["speed_limit_kmh"] * 100
    road_inc = (inc[inc["sensor_match"] == "both"].groupby("road_name")
                .agg(incidents=("incident_id", "size"),
                     avg_severity_score=("severity_score", "mean"),
                     max_severity_score=("severity_score", "max")))
    by_road = by_road.merge(road_inc, on="road_name", how="left", validate="one_to_one")
    by_road["incidents"] = by_road["incidents"].fillna(0).astype(int)
    by_road = by_road.round(2).sort_values("avg_hourly_vehicles", ascending=False).reset_index(drop=True)

    severity_by_road = (by_road[by_road["incidents"] > 0]
                        [["road_name", "district", "incidents", "avg_severity_score", "max_severity_score"]]
                        .sort_values(["avg_severity_score", "incidents"], ascending=[False, False])
                        .reset_index(drop=True))

    peak = (data.groupby(["district", "period"])["vehicle_count"].mean().unstack("period"))
    peak_gap = (peak.assign(peak_minus_off_peak=peak["peak"] - peak["off_peak"],
                            peak_to_off_peak_ratio=peak["peak"] / peak["off_peak"])
                .rename(columns={"peak": "avg_vehicles_peak", "off_peak": "avg_vehicles_off_peak"})
                .round(2).sort_values("peak_minus_off_peak", ascending=False).reset_index())
    peak_gap.columns.name = None

    return {"by_district": by_district, "slowest_districts": slowest_districts,
            "incidents_by_district": incidents_by_district, "by_road": by_road,
            "severity_by_road": severity_by_road, "peak_gap": peak_gap, "incidents_labelled": inc}


# ----------------------------------------------------------------------------
# ROUND 3: Time series
# ----------------------------------------------------------------------------
def time_series_report(data: pd.DataFrame) -> dict:
    ts = data.sort_values("timestamp").set_index("timestamp")

    hourly_city = ts["vehicle_count"].resample("h").sum().rename("citywide_vehicles")

    daily = pd.DataFrame({
        "total_vehicles": ts["vehicle_count"].resample("D").sum(),
        "avg_speed_kmh": ts["avg_speed_kmh"].resample("D").mean(),
    })
    daily["vehicles_3day_ma"] = daily["total_vehicles"].rolling(3).mean()
    daily["speed_3day_ma"] = daily["avg_speed_kmh"].rolling(3).mean()
    daily["vehicles_change"] = daily["total_vehicles"].diff()
    daily["vehicles_pct_change"] = daily["total_vehicles"].pct_change() * 100
    daily["speed_change_kmh"] = daily["avg_speed_kmh"].diff()
    daily["speed_pct_change"] = daily["avg_speed_kmh"].pct_change() * 100
    daily["prev_day_vehicles"] = daily["total_vehicles"].shift(1)
    daily["day_name"] = daily.index.day_name()
    daily["is_weekend"] = daily.index.day_of_week >= 5
    daily = daily.round(2)

    daily_speed_by_district = (data.groupby(["date", "district"])["avg_speed_kmh"].mean()
                               .unstack("district").round(2))
    # day-on-day % change per district: the biggest single-district drop points to the mystery
    district_speed_pct = daily_speed_by_district.pct_change() * 100

    by_hour = (data.groupby("hour")
               .agg(total_vehicles=("vehicle_count", "sum"),
                    avg_vehicles_per_sensor=("vehicle_count", "mean"),
                    avg_speed_kmh=("avg_speed_kmh", "mean"))
               .round(2).reset_index())
    busiest_hour = by_hour.loc[by_hour["total_vehicles"].idxmax()]

    slowest_day = daily["avg_speed_kmh"].idxmin()
    # Same question with the 12 Nov disruption excluded, to see whether one event drives the answer
    slowest_day_excl = daily.drop(index=MYSTERY_DATE)["avg_speed_kmh"].idxmin()

    weekday_weekend = (data.groupby("is_weekend")
                       .agg(avg_vehicles_per_sensor_hour=("vehicle_count", "mean"),
                            avg_speed_kmh=("avg_speed_kmh", "mean"),
                            days=("date", "nunique"),
                            total_vehicles=("vehicle_count", "sum"))
                       .rename(index={False: "weekday", True: "weekend"}))
    weekday_weekend["avg_daily_vehicles"] = weekday_weekend["total_vehicles"] / weekday_weekend["days"]
    weekday_weekend = weekday_weekend.round(2).rename_axis("day_type").reset_index()

    # Hour-controlled weekday/weekend comparison (same hour of day)
    hour_profile = (data.groupby(["hour", "is_weekend"])["vehicle_count"].mean()
                    .unstack("is_weekend").rename(columns={False: "weekday", True: "weekend"}).round(1))
    hour_profile.columns.name = None

    return {"hourly_city": hourly_city, "daily": daily,
            "daily_speed_by_district": daily_speed_by_district,
            "district_speed_pct_change": district_speed_pct.round(2),
            "by_hour": by_hour, "busiest_hour": busiest_hour,
            "slowest_day": slowest_day, "slowest_day_excl_event": slowest_day_excl,
            "weekday_weekend": weekday_weekend, "weekday_weekend_by_hour": hour_profile.reset_index()}


# ----------------------------------------------------------------------------
# ROUND 4: The traffic mystery
# ----------------------------------------------------------------------------
def baseline_days(data: pd.DataFrame, event_date: pd.Timestamp, window_days: int = 7) -> list:
    """Nearby non-event days of the same type (weekday vs weekend) within +/- window_days."""
    dates = pd.Series(sorted(data["date"].unique()))
    same_type = (dates.dt.day_of_week >= 5) == (event_date.day_of_week >= 5)
    near = (dates - event_date).abs() <= pd.Timedelta(days=window_days)
    return list(dates[same_type & near & (dates != event_date)])


def investigate_mystery(data: pd.DataFrame, incidents_labelled: pd.DataFrame,
                        event_date: pd.Timestamp = MYSTERY_DATE) -> dict:
    base_days = baseline_days(data, event_date)

    def hour_profile(frame):
        return frame.groupby(["district", "hour"])["avg_speed_kmh"].mean()

    event = data[data["date"] == event_date]
    base = data[data["date"].isin(base_days)]
    cmp = pd.DataFrame({"event_speed": hour_profile(event), "baseline_speed": hour_profile(base)})
    cmp["speed_drop_pct"] = (cmp["baseline_speed"] - cmp["event_speed"]) / cmp["baseline_speed"] * 100
    cmp = cmp.round(2).reset_index()

    # Step 1: district = largest drop in any hour; window = consecutive hours with drop > 20%
    district = cmp.loc[cmp["speed_drop_pct"].idxmax(), "district"]
    d_hours = cmp[cmp["district"] == district].set_index("hour")
    flagged = d_hours.index[d_hours["speed_drop_pct"] > 20].tolist()
    start_h, end_h = min(flagged), max(flagged)
    window_hours = list(range(start_h, end_h + 1))

    district_scan = (cmp[cmp["hour"].isin(window_hours)].groupby("district")
                     [["event_speed", "baseline_speed"]].mean())
    district_scan["speed_drop_pct"] = ((district_scan["baseline_speed"] - district_scan["event_speed"])
                                       / district_scan["baseline_speed"] * 100)
    district_scan = district_scan.round(2).sort_values("speed_drop_pct", ascending=False).reset_index()

    # Step 2/3: roads in the district, same hours, event vs baseline (speed and volume)
    def road_window(frame):
        f = frame[(frame["district"] == district) & frame["hour"].isin(window_hours)]
        return f.groupby(["road_name", "sensor_id", "road_type"]).agg(
            speed=("avg_speed_kmh", "mean"), vehicles=("vehicle_count", "mean"))

    ev, bs = road_window(event), road_window(base)
    roads = pd.DataFrame({"event_speed_kmh": ev["speed"], "baseline_speed_kmh": bs["speed"],
                          "event_vehicles": ev["vehicles"], "baseline_vehicles": bs["vehicles"]})
    roads["speed_drop_pct"] = (roads["baseline_speed_kmh"] - roads["event_speed_kmh"]) / roads["baseline_speed_kmh"] * 100
    roads["vehicle_change_pct"] = (roads["event_vehicles"] - roads["baseline_vehicles"]) / roads["baseline_vehicles"] * 100
    roads = roads.round(1).sort_values("speed_drop_pct", ascending=False).reset_index()

    overall = pd.DataFrame([{
        "district": district,
        "window": f"{event_date:%d %b %Y} {start_h:02d}:00-{end_h + 1:02d}:00",
        "baseline_days": ", ".join(d.strftime("%a %d %b") for d in base_days),
        "event_speed_kmh": round(event.loc[(event.district == district) & event.hour.isin(window_hours), "avg_speed_kmh"].mean(), 1),
        "baseline_speed_kmh": round(base.loc[(base.district == district) & base.hour.isin(window_hours), "avg_speed_kmh"].mean(), 1),
    }])
    overall["speed_drop_pct"] = round((overall["baseline_speed_kmh"] - overall["event_speed_kmh"])
                                      / overall["baseline_speed_kmh"] * 100, 1)

    # Robustness: same-weekday baseline (previous Thursdays) instead of nearby weekdays
    same_dow = [d for d in data["date"].unique() if pd.Timestamp(d).day_of_week == event_date.day_of_week
                and d != event_date]
    sd = data[data["date"].isin(same_dow) & (data["district"] == district) & data["hour"].isin(window_hours)]
    robustness = pd.DataFrame([
        {"baseline": "nearby weekdays (+/-7 days)", "days": len(base_days),
         "baseline_speed_kmh": overall.loc[0, "baseline_speed_kmh"]},
        {"baseline": f"all other {event_date:%A}s", "days": len(same_dow),
         "baseline_speed_kmh": round(sd["avg_speed_kmh"].mean(), 1)},
    ])
    robustness["event_speed_kmh"] = overall.loc[0, "event_speed_kmh"]
    robustness["speed_drop_pct"] = ((robustness["baseline_speed_kmh"] - robustness["event_speed_kmh"])
                                    / robustness["baseline_speed_kmh"] * 100).round(1)

    # Hour-by-hour timeline for the district
    timeline = (d_hours.loc[range(start_h - 3, min(end_h + 4, 24))].reset_index()
                [["hour", "baseline_speed", "event_speed", "speed_drop_pct"]])
    timeline["in_window"] = timeline["hour"].isin(window_hours)

    # Step 4: weather in the same district and window, vs baseline days
    w_cols = ["temperature_c", "rainfall_mm", "wind_speed_kmh"]
    wx_event = event[(event.district == district) & event.hour.isin(window_hours)].drop_duplicates("timestamp")
    wx_base = base[(base.district == district) & base.hour.isin(window_hours)].drop_duplicates("timestamp")
    weather_check = pd.DataFrame({
        "event_window_mean": wx_event[w_cols].mean(),
        "baseline_window_mean": wx_base[w_cols].mean(),
    }).round(2)
    weather_check.loc["hours_with_rain_or_drizzle", :] = [
        int(wx_event["weather_condition"].isin(["Rain", "Drizzle"]).sum()),
        round(wx_base["weather_condition"].isin(["Rain", "Drizzle"]).sum() / len(base_days), 2)]
    weather_check.loc["weather_observations_present", :] = [
        int((wx_event["weather_match"] == "both").sum()), round(len(wx_base) / len(base_days), 2)]
    weather_check = weather_check.rename_axis("measure").reset_index()
    weather_rows = (event[event.district == district].drop_duplicates("timestamp")
                    [["timestamp", "weather_condition", "rainfall_mm", "wind_speed_kmh", "temperature_c", "weather_match"]])
    wind_unique_on_event_day = weather_rows["wind_speed_kmh"].nunique()

    # Step 5: incidents on the affected roads, event day
    day_inc = incidents_labelled[incidents_labelled["timestamp"].dt.normalize() == event_date]
    incident_check = (day_inc[["incident_id", "timestamp", "road_name", "district", "incident_type",
                               "severity", "duration_min", "lanes_blocked"]]
                      .sort_values("timestamp").reset_index(drop=True))
    in_district = incident_check[incident_check["district"] == district].copy()
    in_district["clears_at"] = in_district["timestamp"] + pd.to_timedelta(in_district["duration_min"], unit="m")

    # Context: how unusual are these incidents for this district?
    dist_hist = incidents_labelled[incidents_labelled["district"] == district]
    district_incident_context = pd.DataFrame([{
        "district": district,
        "incidents_whole_month": len(dist_hist),
        "incidents_on_event_morning": len(in_district),
        "critical_incidents_whole_month": int((dist_hist["severity"] == "critical").sum()),
        "other_days_with_3plus_incidents": int((dist_hist.groupby(dist_hist["timestamp"].dt.normalize()).size() >= 3)
                                               .drop(index=event_date, errors="ignore").sum()),
    }])

    return {"district": district, "window_hours": window_hours, "base_days": base_days,
            "hour_comparison": cmp, "district_scan": district_scan, "overall": overall,
            "robustness": robustness, "timeline": timeline, "roads": roads,
            "weather_check": weather_check, "weather_rows": weather_rows,
            "wind_unique_on_event_day": wind_unique_on_event_day,
            "incident_check": incident_check, "incidents_in_district": in_district,
            "district_incident_context": district_incident_context}


# ----------------------------------------------------------------------------
# Weather vs traffic (hour-controlled) for the dashboard / findings
# ----------------------------------------------------------------------------
def weather_comparison(data: pd.DataFrame) -> pd.DataFrame:
    d = data[data["weather_match"] == "both"].copy()
    # Expected speed for this sensor at this hour of day; compare each reading with it
    d["expected_speed"] = d.groupby(["sensor_id", "hour"])["avg_speed_kmh"].transform("mean")
    d["speed_vs_expected_kmh"] = d["avg_speed_kmh"] - d["expected_speed"]
    d["rain_band"] = pd.cut(d["rainfall_mm"], [-0.01, 0, 2, 5, float("inf")],
                            labels=["0 mm (dry)", "0-2 mm", "2-5 mm", "> 5 mm"])
    out = []
    for col, label in [("weather_condition", "condition"), ("rain_band", "rainfall_band")]:
        g = (d.groupby(col, observed=True)
             .agg(observations=("sensor_id", "size"),
                  avg_vehicles=("vehicle_count", "mean"),
                  avg_speed_kmh=("avg_speed_kmh", "mean"),
                  speed_vs_same_sensor_hour_kmh=("speed_vs_expected_kmh", "mean"))
             .round(2).reset_index().rename(columns={col: "group"}))
        g.insert(0, "grouping", label)
        g["group"] = g["group"].astype(str)
        out.append(g)
    return pd.concat(out, ignore_index=True)


# ----------------------------------------------------------------------------
# Charts
# ----------------------------------------------------------------------------
def make_charts(hot, ts, mys, outdir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    outdir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 4))
    d = ts["daily"]
    ax.plot(d.index, d["total_vehicles"], marker="o", lw=1, label="Daily vehicles")
    ax.plot(d.index, d["vehicles_3day_ma"], lw=2.5, label="3-day moving average")
    ax.set_title("Citywide daily vehicle count"); ax.legend(); ax.grid(alpha=.3)
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(outdir / "daily_trend.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(ts["by_hour"]["hour"], ts["by_hour"]["total_vehicles"])
    ax.set_xticks(range(24)); ax.set_xlabel("Hour of day"); ax.set_ylabel("Vehicles (31 days)")
    ax.set_title("Citywide traffic volume by hour"); ax.grid(axis="y", alpha=.3)
    fig.tight_layout(); fig.savefig(outdir / "by_hour.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4))
    t = mys["hour_comparison"]; t = t[t["district"] == mys["district"]]
    ax.plot(t["hour"], t["baseline_speed"], marker="o", label="Baseline (nearby weekdays)")
    ax.plot(t["hour"], t["event_speed"], marker="o", label=f"{MYSTERY_DATE:%d %b}")
    w = mys["window_hours"]; ax.axvspan(min(w) - .5, max(w) + .5, alpha=.15, color="red")
    ax.set_xticks(range(24)); ax.set_xlabel("Hour of day"); ax.set_ylabel("Avg speed (km/h)")
    ax.set_title(f"{mys['district']}: speed on {MYSTERY_DATE:%d %b} vs baseline"); ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(outdir / "mystery_timeline.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    b = hot["by_district"].sort_values("avg_hourly_vehicles")
    ax.barh(b["district"], b["avg_hourly_vehicles"]); ax.set_xlabel("Average vehicles per sensor-hour")
    ax.set_title("Traffic volume by district"); ax.grid(axis="x", alpha=.3)
    fig.tight_layout(); fig.savefig(outdir / "by_district.png", dpi=150); plt.close(fig)


# ----------------------------------------------------------------------------
def main(argv: list[str]) -> None:
    data_dir = find_data_dir(argv[1] if len(argv) > 1 else None)
    traffic, sensors, weather, incidents = load_data(data_dir)
    print(f"Data folder: {data_dir}")
    print("Raw row counts:", {n: len(f) for n, f in
                              zip(["traffic", "sensors", "weather", "incidents"], [traffic, sensors, weather, incidents])})

    section("ROUND 1: DATA INTEGRATION")
    data, rep = integrate_data(traffic, sensors, weather, incidents)
    print("\nRow counts through the pipeline:\n", rep["merge_row_counts"].to_string(index=False))
    print("\nMissing weather observations (district-hours):\n", rep["missing_weather_keys"].to_string(index=False))
    demo = duplicate_key_demo(traffic, sensors)
    print("\nWhat a duplicated right-hand key does:\n", demo.to_string(index=False))

    section("ROUND 2: TRAFFIC HOTSPOTS")
    hot = traffic_hotspots(data, incidents, sensors)
    print("District summary (sorted by avg hourly vehicles):\n", hot["by_district"].to_string(index=False))
    print("\nDistricts by average speed (slowest first):\n", hot["slowest_districts"].to_string(index=False))
    print("\nRoads (sorted by avg hourly vehicles):\n", hot["by_road"].to_string(index=False))
    print("\nIncidents by district:\n", hot["incidents_by_district"].to_string(index=False))
    print(f"\nSeverity mapping used: {SEVERITY_SCORE}")
    print("Roads by average incident severity:\n", hot["severity_by_road"].to_string(index=False))
    print(f"\nPeak hours = {PEAK_HOURS}; all other hours = off-peak")
    print("Peak vs off-peak gap by district:\n", hot["peak_gap"].to_string(index=False))

    section("ROUND 3: TIME SERIES")
    ts = time_series_report(data)
    print("Daily citywide series (3-day MA, diff, pct_change):\n",
          ts["daily"].drop(columns=["prev_day_vehicles"]).to_string())
    print("\nDaily average speed by district (last 7 days shown):\n", ts["daily_speed_by_district"].tail(7).to_string())
    print("\nVolume by hour of day:\n", ts["by_hour"].to_string(index=False))
    bh = ts["busiest_hour"]
    print(f"\nBusiest hour: {int(bh['hour']):02d}:00 ({int(bh['total_vehicles']):,} vehicles over 31 days)")
    print(f"Lowest average-speed day: {ts['slowest_day']:%a %d %b %Y} "
          f"({ts['daily'].loc[ts['slowest_day'], 'avg_speed_kmh']} km/h)")
    print(f"Lowest excluding 12 Nov: {ts['slowest_day_excl_event']:%a %d %b %Y} "
          f"({ts['daily'].loc[ts['slowest_day_excl_event'], 'avg_speed_kmh']} km/h)")
    print("\nWeekday vs weekend:\n", ts["weekday_weekend"].to_string(index=False))
    print("\nWeekday vs weekend, same hour of day (avg vehicles per sensor):\n",
          ts["weekday_weekend_by_hour"].to_string(index=False))

    section("ROUND 4: THE TRAFFIC MYSTERY")
    mys = investigate_mystery(data, hot["incidents_labelled"])
    print("Baseline days:", ", ".join(d.strftime("%a %d %b") for d in mys["base_days"]))
    print("\nAll districts, same window, event vs baseline:\n", mys["district_scan"].to_string(index=False))
    print("\nFinding:\n", mys["overall"].to_string(index=False))
    print("\nBaseline robustness:\n", mys["robustness"].to_string(index=False))
    print("\nHour-by-hour timeline:\n", mys["timeline"].to_string(index=False))
    print("\nRoads ranked by speed drop (window hours):\n", mys["roads"].to_string(index=False))
    print("\nWeather check (same district & window):\n", mys["weather_check"].to_string(index=False))
    print(f"Distinct wind_speed values in {mys['district']} on {MYSTERY_DATE:%d %b}: "
          f"{mys['wind_unique_on_event_day']} (a constant value suggests filled/imputed readings)")
    print("\nAll incidents on the event day:\n", mys["incident_check"].to_string(index=False))
    print("\nIncidents in the affected district with estimated clear time:\n",
          mys["incidents_in_district"].to_string(index=False))
    print("\nContext:\n", mys["district_incident_context"].to_string(index=False))

    section("WEATHER VS TRAFFIC (controlled for sensor and hour of day)")
    wc = weather_comparison(data)
    print(wc.to_string(index=False))

    # ---- save outputs ----
    tables = OUT / "tables"; tables.mkdir(parents=True, exist_ok=True)
    to_save = {
        "r1_key_checks": rep["key_checks"], "r1_merge_row_counts": rep["merge_row_counts"],
        "r1_missing_weather_keys": rep["missing_weather_keys"],
        "r1_unknown_sensor_incidents": rep["unknown_sensor_incidents"], "r1_duplicate_key_demo": demo,
        "r2_by_district": hot["by_district"], "r2_by_road": hot["by_road"],
        "r2_incidents_by_district": hot["incidents_by_district"], "r2_severity_by_road": hot["severity_by_road"],
        "r2_peak_gap": hot["peak_gap"],
        "r3_daily": ts["daily"].reset_index(), "r3_by_hour": ts["by_hour"],
        "r3_daily_speed_by_district": ts["daily_speed_by_district"].reset_index(),
        "r3_weekday_weekend": ts["weekday_weekend"],
        "r4_district_scan": mys["district_scan"], "r4_overall": mys["overall"],
        "r4_robustness": mys["robustness"], "r4_timeline": mys["timeline"], "r4_roads": mys["roads"],
        "r4_weather_check": mys["weather_check"], "r4_incidents": mys["incident_check"],
        "weather_comparison": wc,
    }
    for name, df in to_save.items():
        df.to_csv(tables / f"{name}.csv", index=False)
    try:
        make_charts(hot, ts, mys, OUT / "charts")
        print(f"\nCharts saved to {OUT / 'charts'}")
    except ImportError:
        print("\nmatplotlib not installed: charts skipped (tables still saved)")

    # Key numbers for the briefing deck
    key = {
        "traffic_rows": len(traffic), "integrated_rows": len(data),
        "weather_missing_keys": len(rep["missing_weather_keys"]),
        "traffic_rows_without_weather": int((data["weather_match"] == "left_only").sum()),
        "unknown_sensor_incidents": rep["unknown_sensor_incidents"]["incident_id"].tolist(),
        "incidents_matched": int(data["has_incident"].sum()),
        "busiest_hour": int(bh["hour"]),
        "slowest_day": f"{ts['slowest_day']:%Y-%m-%d}",
    }
    (OUT / "key_numbers.json").write_text(json.dumps(key, indent=2))
    print(f"Tables saved to {tables}")


if __name__ == "__main__":
    main(sys.argv)
