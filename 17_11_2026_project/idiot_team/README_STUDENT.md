# CITYPULSE CHALLENGE — THE BATTLE OF DATA TEAMS

## Your mission

You are a data intelligence team hired by the city traffic management centre. Several teams have received the same four datasets. Your job is to combine the sources, discover traffic patterns, investigate one hidden traffic anomaly, and deliver evidence-based recommendations.

**The winning team is not simply the fastest. It is the team with accurate joins, reproducible analysis, and the clearest evidence.**

All records are synthetic and created for this classroom exercise. They do not describe a real city or real incidents.

## Files

- `data/traffic.csv` — hourly traffic observations by sensor.
- `data/sensors.csv` — sensor registry and road/district metadata.
- `data/weather.csv` — hourly weather observations by district. A small number of observations are intentionally absent; a left join should preserve the traffic rows and expose missing weather matches.
- `data/incidents.csv` — incident events. A few incidents reference sensor IDs that do not exist in the sensor registry; find them during your integrity check.
- `starter.py` — starter code with suggested function signatures.

### Data dictionary

**traffic.csv**
- `timestamp`: hourly observation timestamp (`YYYY-MM-DD HH:MM:SS`)
- `sensor_id`: traffic sensor key
- `vehicle_count`: number of vehicles counted in the hour
- `avg_speed_kmh`: average speed in km/h

**sensors.csv**
- `sensor_id`: unique sensor identifier
- `road_name`: road monitored by the sensor
- `district`: city district
- `road_type`: arterial, collector, or local
- `speed_limit_kmh`: posted speed limit

**weather.csv**
- `timestamp`, `district`: composite key for the weather observation
- `temperature_c`, `rainfall_mm`, `wind_speed_kmh`, `weather_condition`: weather measurements/label

**incidents.csv**
- `incident_id`: unique event identifier
- `timestamp`, `sensor_id`: event time and nearest sensor
- `incident_type`, `severity`, `duration_min`, `lanes_blocked`: event details

## Competition rules

1. Every claim must be supported by a DataFrame result or a reproducible calculation.
2. Print `len()` before and after every merge. Explain unexpected changes.
3. Check key uniqueness before merging. Use `validate=` whenever possible.
4. Never silently discard unmatched records. Use `indicator=True` or an equivalent anti-join check. Give each indicator a distinct name (for example, `sensor_match` and `weather_match`) if you keep several merge reports in one DataFrame.
5. Keep your raw CSV files unchanged. Work with derived DataFrames.
6. Do not claim that correlation proves causation.
7. Do not share your team's code or results with other teams during the rounds.

## Suggested schedule (3 × 45 minutes)

- 0–10 min: briefing and team setup
- 10–25 min: Round 1 — Data Integration
- 25–45 min: Round 2 — Find the Traffic Hotspot
- 45–65 min: Round 3 — Time Series Investigation
- 65–90 min: Round 4 — The Traffic Mystery
- 90–105 min: build/finish your final dashboard
- 105–125 min: final team briefings
- 125–135 min: leaderboard and awards

## ROUND 1 — DATA INTEGRATION (20 points)

Build one analysis-ready table. Suggested sequence:

1. Merge `traffic` with `sensors` on `sensor_id` using a left join and `validate="many_to_one"`.
2. Merge weather on `timestamp` and `district`. The weather key should be unique; use a left join so traffic observations are not lost.
3. Join incidents on `timestamp` and `sensor_id`. Check the key cardinality first. A traffic observation with no incident is not an error; it simply has no matching event.
4. Print the row count before and after each merge.
5. Use `indicator=True` to count matches and non-matches.
6. Find incidents whose `sensor_id` does not exist in `sensors.csv`.

Questions:
- How many traffic observations are there before and after integration?
- How many weather rows failed to match?
- How many incidents refer to an unknown sensor?
- What would happen if a merge key were duplicated on the right-hand side?

## ROUND 2 — FIND THE TRAFFIC HOTSPOT (20 points)

Use `groupby()` and multiple aggregations to answer:

1. Which district has the highest average hourly vehicle count?
2. Which district has the lowest average speed?
3. Which roads have the highest average traffic volume?
4. Which district has the most recorded incidents?
5. Which road has the highest average incident severity? (Choose and document a sensible severity-to-number mapping.)
6. Which district has the largest difference between peak and off-peak traffic?

Your output must use readable column names and be sorted so the ranking is easy to interpret.

## ROUND 3 — TIME SERIES INVESTIGATION (20 points)

1. Convert `timestamp` to datetime and sort the data.
2. Set the timestamp as the index or use it as the resampling key.
3. Calculate hourly or daily citywide vehicle counts.
4. Calculate daily average speed by district.
5. Add a 3-period moving average to a daily series.
6. Calculate absolute and percentage change from the previous period.
7. Identify the busiest hour and the day with the lowest average speed.
8. Compare weekday and weekend traffic.

Use `resample()`, `rolling()`, `diff()`, `pct_change()`, `shift()`, and/or `groupby()` where appropriate.

## ROUND 4 — THE TRAFFIC MYSTERY (25 points)

**CONFIDENTIAL CITY ALERT**

> On **12 November 2026**, traffic speed suddenly dropped by approximately **45%** in one district. The city wants to know where the disruption happened, which roads were affected, and what most likely explains it.

Your investigation must:

1. Identify the district and time window with the unusual speed drop.
2. Compare the affected period with a reasonable baseline (for example, the same hours on nearby days). Do not compare rush hour with overnight traffic.
3. Identify the roads most affected.
4. Check weather conditions in the same district and time window.
5. Check incident records for the affected roads and period.
6. State a hypothesis and support it with at least three separate pieces of evidence.
7. Mention one limitation or uncertainty in your conclusion.

Do not jump to a cause based only on one chart or one row. Distinguish evidence from interpretation.

## ROUND 5 — FINAL INTELLIGENCE BRIEFING (15 points)

Present a concise report to the city (maximum 3 minutes). Include:

- Three major findings from the data.
- One visual or tidy summary table.
- Your Traffic Mystery conclusion and supporting evidence.
- Two practical recommendations for the city.
- One limitation of your analysis.

## Required final deliverables

Submit one folder containing:

1. `analysis.ipynb` or `analysis.py` — reproducible analysis.
2. `dashboard.py` — a function returning tidy DataFrames (or an equivalent notebook section).
3. `team_briefing.pdf` or a short slide deck — final findings.
4. A short `README.md` explaining how to run your work.

### Suggested dashboard function

Create `city_dashboard(traffic, sensors, weather, incidents)` returning a dictionary with at least:

- `by_district`: total vehicles, average speed, observation count
- `by_road`: average vehicles, average speed, incident count
- `by_hour`: citywide traffic volume by hour of day
- `daily_trend`: daily traffic, daily average speed, rolling average
- `incident_summary`: incident count by type and severity
- `weather_comparison`: traffic metrics by weather condition or rainfall band

The tables should have clear column names and be ready to print or plot.

## Scoring

| Round | Points |
|---|---:|
| 1 — Data Integration | 20 |
| 2 — Traffic Hotspot | 20 |
| 3 — Time Series | 20 |
| 4 — Traffic Mystery | 25 |
| 5 — Final Briefing | 15 |
| **Base score** | **100** |

Bonus/penalties are applied by the teacher:
- Speed bonus: +3 to the first team to submit a correct, reproducible round result.
- Challenge steal: +2 for identifying and demonstrating a real error in another team's public claim or code.
- Data integrity penalty: −3 for an unexplained row explosion or silent loss of unmatched records.

Good luck. Be precise, question your joins, and trust the evidence.
