CYBERSECURITY INTELLIGENCE — SOC ANALYST PROJECT
Module: Pandas — GroupBy and Aggregation
Project type: Team lab
Suggested team size: 3–4 students
Suggested duration: 2–3 × 45-minute lessons (adjust to your class)

Scenario
You are a small Security Operations Centre (SOC) analysis team. Your company has collected security event records during September 2026. Management wants to understand which attack types are most common, which assets are most exposed, how quickly incidents are handled, and where the SOC should focus its attention.

Your job is to turn raw event records into an evidence-based intelligence report. You are analysts, not incident responders: do not attempt to attack, scan, or access any system. This project is entirely offline and uses synthetic data.

Files
soc_incidents.csv — 720 synthetic security events.
starter.py — function skeletons to complete.
requirements.txt — Python dependencies.
All source IP addresses are from documentation-only address ranges. Countries, events, assets, and outcomes are fictional. No real people, organisations, or systems are represented.

Setup
`python -m pip install -r requirements.txt`
Open starter.py in your editor or notebook. Keep the CSV in the same folder.

Part 1 — Understand the evidence (10–15 min)
Load the CSV into a DataFrame.
Inspect head(), shape, dtypes, and describe().
Parse timestamp as a datetime.
Create event_date, hour, and weekday columns.
Check missing values and duplicate incident_id values.
Deliverable: a short data profile (row count, date range, number of attack types, countries, assets, and unique source IPs).

Part 2 — GroupBy investigation (25–30 min)
Answer each question with a Pandas expression and a short interpretation.

Mission A: Attack landscape
How many incidents belong to each attack_type? Sort descending.
What is the average and median response time per attack type?
What is the percentage of incidents blocked per attack type?
How many distinct source IPs are associated with each attack type?
Which attack type has the highest compromise rate?
Mission B: Geographic and asset exposure
Which countries generate the most incidents?
Which target assets receive the most incidents?
For each asset, calculate incident count, critical/emergency count, and average response time.
Which country–attack-type combination has the highest incident count? Show both a MultiIndex result and a flattened result using reset_index().
Mission C: Time patterns
How many incidents occur in each hour of the day?
Which weekday has the highest average severity score?
Calculate daily incident totals and identify the busiest day.
Part 3 — Go beyond aggregation (20–25 min)
Use transform() to add each row's attack-type average response time (attack_avg_response).
Add response_vs_attack_avg as the difference between the incident response time and its attack-type average.
Add above_attack_avg_severity, a Boolean showing whether the event severity is above its attack-type average.
Use groupby().filter() to keep only target assets with at least 80 incidents.
Rank attack types by incident count within each source country. Show the top two attack types for each country.
Explain in a comment why agg() and transform() return different shapes.
Part 4 — Build the SOC dashboard (25–30 min)
Complete soc_dashboard(df) in starter.py. It must return a dictionary containing tidy DataFrames with meaningful column names:

by_attack: incident count, unique source IPs, average response time, blocked rate, compromise rate.
by_country: incident count, critical/emergency count, unique target assets, blocked rate.
by_asset: incident count, compromised count, average severity score, average response time.
by_hour: incident count, average severity score, average response time, sorted by hour.
top_sources: five source IPs with the most incidents, including unique targets and compromised incidents.
daily_trend: daily incident count and daily compromise count, sorted chronologically.
Your function must not modify the input DataFrame. Handle an empty DataFrame clearly.

Part 5 — Management briefing (10 min)
Prepare a 3-minute briefing with:

Three findings supported by numbers.
One asset or attack type that deserves further investigation, and why.
One operational recommendation for the SOC.
One limitation of the dataset or your analysis.
Do not claim that a country or group is responsible for an attack simply because its events appear in the dataset. The country field is synthetic event metadata, not attribution evidence.

Stretch goals
Add a by_attack_and_asset report using named aggregation.
Calculate the 90th percentile of response time per attack type with a custom aggregation function.
Compare blocked rate and compromise rate per severity level.
Write at least six pytest tests for soc_dashboard().
Create a simple chart from one returned dashboard DataFrame.
Rules
Use groupby(), agg(), transform(), filter(), and sorting/ranking where appropriate.
Avoid loops over rows and avoid iterrows().
Use vectorised operations for derived columns.
Every conclusion must be supported by a reproducible calculation.