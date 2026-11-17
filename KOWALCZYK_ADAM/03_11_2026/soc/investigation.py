"""Parts 1-3: data profile and the 18 questions, each as a reproducible expression."""
import sys
from pathlib import Path
import pandas as pd
from starter import load_data, add_group_context, attack_summary

# Print to the terminal and save the same text to output/investigation_output.txt.
OUT_FILE = Path(__file__).with_name("output") / "investigation_output.txt"
OUT_FILE.parent.mkdir(exist_ok=True)


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)

    def flush(self):
        for s in self.streams:
            s.flush()


sys.stdout = Tee(sys.__stdout__, open(OUT_FILE, "w", encoding="utf-8"))

df = load_data()


def show(title, obj):
    print(f"\n--- {title} ---")
    print(obj.to_string() if hasattr(obj, "to_string") else obj)


# Part 1: data profile
show("shape / dtypes", f"{df.shape}\n{df.dtypes}")
show("missing values", df.isna().sum())
show("duplicate incident_id", df["incident_id"].duplicated().sum())
show("profile", {
    "rows": len(df), "from": df.timestamp.min(), "to": df.timestamp.max(),
    "attack_types": df.attack_type.nunique(), "countries": df.source_country.nunique(),
    "assets": df.target_asset.nunique(), "unique_ips": df.source_ip.nunique(),
})

# Mission A (Q1-5): attack_summary covers counts, avg/median response, rates, unique IPs
summary = attack_summary(df)
show("Q1-4 attack summary", summary)
show("Q5 highest compromise rate", summary.loc[summary.compromise_rate_pct.idxmax(), ["attack_type", "compromise_rate_pct"]])

# Mission B (Q6-9)
show("Q6 countries", df.source_country.value_counts())
show("Q7 assets", df.target_asset.value_counts())
show("Q8 asset exposure", df.groupby("target_asset").agg(
    incidents=("incident_id", "count"),
    critical_emergency=("severity", lambda s: s.isin(["Critical", "Emergency"]).sum()),
    avg_response_min=("response_time_min", "mean")).round(1))
multi = df.groupby(["source_country", "attack_type"]).size().sort_values(ascending=False)
show("Q9 MultiIndex (top 5)", multi.head())
show("Q9 flattened (top 5)", multi.reset_index(name="incidents").head())

# Mission C (Q10-12)
show("Q10 by hour", df.groupby("hour").size())
show("Q11 avg severity by weekday", df.groupby("weekday")["severity_score"].mean().sort_values(ascending=False).round(3))
daily = df.groupby("event_date").size()
show("Q12 busiest day", f"{daily.idxmax()} with {daily.max()} incidents")

# Part 3 (Q13-17)
ctx = add_group_context(df)
show("Q13-15 context columns", ctx[["incident_id", "attack_type", "attack_avg_response", "response_vs_attack_avg", "above_attack_avg_severity"]].head())
busy = df.groupby("target_asset").filter(lambda g: len(g) >= 80)
show("Q16 filter >=80", f"rows {len(df)} -> {len(busy)}; assets kept: {sorted(busy.target_asset.unique())}")
counts = df.groupby(["source_country", "attack_type"]).size().reset_index(name="incidents")
counts["rank"] = counts.groupby("source_country")["incidents"].rank(method="first", ascending=False)
show("Q17 top 2 attack types per country", counts[counts["rank"] <= 2].sort_values(["source_country", "rank"]).to_string(index=False))

# Q18: agg() collapses each group to ONE row (output has one row per group), while
# transform() must return a result aligned to the original index (one value per input row),
# so every group's summary is broadcast back onto its rows and the row count is unchanged.
# filter() also keeps original rows, but drops whole groups when the group-level predicate fails.
