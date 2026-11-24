from io import StringIO
from html import escape
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

base = Path(__file__).resolve().parent
out = base / "learning_analytics"
out.mkdir(exist_ok=True)

grades = pd.read_csv(base / "oceny.csv", sep=";", dtype=str, keep_default_na=False)
current = ["Oceny bieżące – okres 1", "Oceny bieżące – okres 2"]


def grade_tokens(text):
    def later_grade(match):
        candidates = re.findall(r"(?<!\S)[1-6][+-]?(?!\S)", match[1].replace(",", " "))
        return f" {candidates[-1]} " if candidates else " "

    text = re.sub(r"\[([^\]]*)\](?:[1-6](?!\d))?", later_grade, text)
    return [token for token in text.split() if re.fullmatch(r"[1-6]", token)]


df = grades.melt(id_vars="Przedmiot", value_vars=current, value_name="grades")
df["grade_value"] = df["grades"].map(grade_tokens)
df = df.explode("grade_value").dropna(subset=["grade_value"]).copy()
if df.empty:
    raise SystemExit("No numeric grades found in oceny.csv.")
df["grade_value"] = df["grade_value"].astype(int)

summary = (
    df.groupby("Przedmiot")["grade_value"]
    .agg(count="count", average="mean", median="median", minimum="min", maximum="max")
    .sort_values("average")
)
frequency = df["grade_value"].value_counts().reindex(range(1, 7), fill_value=0)

fig, axes = plt.subplots(
    2, 2, figsize=(17, max(10, len(summary) * 0.65)), layout="constrained"
)
a, b, c, d = axes.flat

bars = a.barh(summary.index, summary["average"], color="0.35")
a.bar_label(bars, labels=[
    f"{row.average:.2f} (n={row.count})"
    for row in summary.itertuples(index=False)
], padding=4)
a.set(title="Average grade by subject", xlabel="Mean grade (1–6)",
      ylabel="Subject", xlim=(0, 7.5))

b.bar(frequency.index, frequency.values, color="0.45")
b.set(title="Grade frequency", xlabel="Grade", ylabel="Number of grades",
      xticks=list(range(1, 7)))

counts = summary["count"].sort_values()
c.barh(counts.index, counts.values, color="0.45")
c.set(title="Grade counts by subject (dates unavailable)",
      xlabel="Number of grades", ylabel="Subject")

subjects = summary.index[summary["count"] >= 3]
if len(subjects):
    d.boxplot(
        [df.loc[df["Przedmiot"].eq(s), "grade_value"] for s in subjects],
        orientation="horizontal",
        medianprops={"color": "black", "linewidth": 2},
    )
    d.set_yticks(range(1, len(subjects) + 1), subjects)
else:
    d.text(0.5, 0.5, "No subject has at least 3 grades",
           ha="center", transform=d.transAxes)
d.set(title="Grade spread (subjects with at least 3 grades)",
      xlabel="Grade (1–6)", ylabel="Subject",
      xticks=list(range(1, 7)), xlim=(0.75, 6.25))

fig.suptitle("Personal Learning Analytics Dashboard")
with StringIO() as buffer:
    with matplotlib.rc_context({"svg.fonttype": "none"}):
        fig.savefig(buffer, format="svg")
    svg = buffer.getvalue()
    dashboard_svg = svg[svg.index("<svg"):]
plt.close(fig)


def describe_extreme(label, value):
    tied = summary[summary["average"].eq(value)]
    names = ", ".join(f"{name} (n={row['count']:.0f})" for name, row in tied.iterrows())
    return f"{label} observed subject mean: {value:.2f} — {names}."


modes = ", ".join(map(str, frequency.index[frequency.eq(frequency.max())]))
findings = [
    describe_extreme("Highest", summary["average"].max()),
    describe_extreme("Lowest", summary["average"].min()),
    f"Most frequent grade(s): {modes}, with {frequency.max()} occurrences each "
    f"out of {len(df)} numeric grades.",
]
method = (
    "The Librus converter extracts the grade table. Pandas reshapes current grades "
    "to one row per numeric grade. Only the later grade in each correction group is "
    "counted. Plain grades 1–6 are unweighted. Status marks and plus/minus variants "
    "without an agreed numeric conversion are excluded, not counted as zero. "
    "Regular grade dates are unavailable, so the dashboard shows counts by subject "
    "instead of inventing a time trend."
)
limit = "Subject means with few grades can change quickly; these are not official averages."
numbered = "\n".join(f"{i}. {text}" for i, text in enumerate(findings, 1))

(out / "README.md").write_text(
    f"# Personal Learning Analytics\n\n## Method\n{method}\n\n"
    f"## Three findings\n{numbered}\n\n## Limitation\n{limit}\n",
    encoding="utf-8",
)
(out / "presentation_notes.md").write_text(
    "# 2–3 minute presentation\n\n"
    "- 30–45 seconds: Explain how the PDF was converted and how correction groups were handled.\n"
    "- About 1 minute: Show the four charts and discuss these findings:\n\n"
    f"{numbered}\n\n"
    "- 30–45 seconds: Explain why there is no timeline and why sample sizes matter.\n",
    encoding="utf-8",
)

items = "".join(f"<li>{escape(text)}</li>" for text in findings)
(out / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Personal Learning Analytics</title>
<style>
body {{ margin: 0; font: 17px/1.6 system-ui; background: #eef2f7; color: #172033; }}
main {{ max-width: 1200px; margin: auto; padding: 20px; }}
section {{ background: white; border-radius: 12px; padding: 20px; margin: 16px 0; }}
.dashboard {{ overflow-x: auto; }}
.dashboard svg {{ display: block; width: 100%; min-width: 760px; height: auto; }}
</style>
<main>
  <h1>Personal Learning Analytics</h1>
  <section>
    <h2>Grade dashboard</h2>
    <div class="dashboard" role="img"
         aria-label="Subject averages, grade frequency, grade counts, and grade spread">
      {dashboard_svg}
    </div>
  </section>
  <section>
    <h2>Three findings</h2><ol>{items}</ol>
    <h2>Method</h2><p>{escape(method)}</p>
    <h2>Limitation</h2><p>{escape(limit)}</p>
  </section>
</main>
</html>
""", encoding="utf-8")

print(f"Analyzed {len(df)} numeric grades. Results: {out}")
