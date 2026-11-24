"""Personal Learning Analytics: analyse Librus grades and build a 2x2 dashboard.

Works with any student's export: subjects, periods and grade counts are read
from the data, not hard-coded.

Input:  a cleaned CSV made by pdf_to_csv.py (one row per subject, grade columns
        "Okres N - Oceny bieżące" hold only grades like "5 4 6", corrected
        grades already reduced to the newest one, no np/nb/bz)
Output: grades_raw.csv                    one row per grade (private, not for git)
        charts/my_academic_dashboard.png  the 2x2 dashboard
        my_academic_dashboard.html        one-file web page: dashboard + tables
        printed: validation checks, subject summary, grade alerts

Usage:
    python analyse_grades.py                          # synergia.csv -> files above
    python analyse_grades.py --csv other.csv --out-dir report
    python analyse_grades.py --plus 0.5 --minus 0.25  # count "4+" as 4.5, "4-" as 3.75

To go straight from a PDF to the website, use make_report.py.
"""

import argparse
import base64
import html
import re
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

SUBJECT_COLUMN = "Przedmiot"
PERIOD_COLUMN = re.compile(r"Okres (\d+) - Oceny bieżące")  # -> period number
NOT_A_SUBJECT = ["Zachowanie"]  # behaviour has no numeric grades
GRADE_TEXT = re.compile(r"^([1-6])([+-]?)$")

# Thresholds for charts and the alert system
MIN_GRADES = 3              # fewer numeric grades than this = not enough data
TREND_MIN_GRADES = 4        # subjects shown on the "progress" line chart
TREND_MAX_SUBJECTS = 5      # more lines than this would be unreadable
REVIEW_THRESHOLD = 3.0      # subject average below this -> REVIEW AVERAGE
DECLINE_MIN_GRADES = 6      # without 2 periods: grades needed to compare halves
DECLINE_MIN_PER_PERIOD = 2  # with 2 periods: grades needed in each period
DECLINE_DROP = 0.5          # newer part this much lower -> RECENT DECLINE
VARIABILITY_STD = 1.5       # standard deviation above this -> HIGH VARIABILITY
VARIABILITY_MIN_GRADES = 4  # a spread of 3 grades is too small to judge


# ---------------------------------------------------------------------------
# STEP 3: one row per grade
# ---------------------------------------------------------------------------
def load_wide(csv_path):
    """Read the cleaned CSV; works with "," and with ";" (Polish Excel) separators."""
    with open(csv_path, encoding="utf-8-sig") as f:
        header = f.readline()
    sep = ";" if header.count(";") > header.count(",") else ","
    return pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig", sep=sep)


def to_long(wide):
    """One row per subject -> one row per grade. Returns (df, all_subjects)."""
    period_cols = {c: int(m.group(1)) for c in wide.columns
                   if (m := PERIOD_COLUMN.fullmatch(c))}
    if SUBJECT_COLUMN not in wide.columns or not period_cols:
        raise ValueError(
            f"The CSV needs a '{SUBJECT_COLUMN}' column and at least one "
            "'Okres N - Oceny bieżące' column (make it with pdf_to_csv.py)."
        )

    wide = wide.rename(columns={SUBJECT_COLUMN: "subject"})
    wide["subject"] = wide["subject"].str.strip()
    wide = wide[~wide["subject"].isin(NOT_A_SUBJECT)]
    all_subjects = wide["subject"].tolist()

    df = wide.melt(id_vars="subject", value_vars=list(period_cols),
                   var_name="period", value_name="grade_raw")
    df["period"] = df["period"].map(period_cols)
    df = df.dropna(subset=["grade_raw"])              # empty cell = no grades
    df["grade_raw"] = df["grade_raw"].str.split()     # "5 4 2" -> ["5", "4", "2"]
    df = df.explode("grade_raw", ignore_index=True).dropna(subset=["grade_raw"])
    df = df.sort_values(["subject", "period"], kind="stable")

    # Librus lists current grades in the order they were added, so the position
    # inside a subject is the only "time" information the export gives us.
    df["grade_no"] = df.groupby("subject").cumcount() + 1

    # The export has no date or category per grade: keep the columns, leave them empty.
    df["date"] = pd.NaT
    df["category"] = pd.NA
    df = df[["subject", "grade_raw", "date", "category", "period", "grade_no"]]
    return df.reset_index(drop=True), all_subjects


# ---------------------------------------------------------------------------
# STEP 4: clean & validate
# ---------------------------------------------------------------------------
def grade_to_number(raw, plus=None, minus=None):
    """'5' -> 5.0. '4+' / '4-' only get a number if a plus/minus value is given."""
    m = GRADE_TEXT.match(str(raw))
    if not m:
        return float("nan")
    base, sign = float(m.group(1)), m.group(2)
    if not sign:
        return base
    step = plus if sign == "+" else minus
    if step is None:
        return float("nan")                 # don't guess: report it instead
    value = base + step if sign == "+" else base - step
    return min(max(value, 1.0), 6.0)


def add_grade_values(df, plus=None, minus=None):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
    df["grade_value"] = df["grade_raw"].map(lambda g: grade_to_number(g, plus, minus))
    return df


def print_validation(df, all_subjects):
    print("=== Validation ===")
    print(f"Grade records: {len(df)} in {df['subject'].nunique()} subjects "
          f"(of {len(all_subjects)} subjects in the export)")
    print("\nColumn types:")
    print(df.dtypes.to_string())
    print("\nMissing values per column:")
    print(df.isna().sum().to_string())
    unknown = df.loc[df["grade_value"].isna(), "grade_raw"]
    print("\nGrades that could not be mapped to a number:", "none" if unknown.empty else "")
    if not unknown.empty:
        print(unknown.value_counts().to_string())
        print("(left out of the analysis; use --plus/--minus to count 4+ / 4-)")
    print("\nFirst rows (compare with the PDF):")
    print(df.head(8).to_string(index=False))


# ---------------------------------------------------------------------------
# STEP 5: analysis
# ---------------------------------------------------------------------------
def summarise(graded):
    subject_summary = (
        graded.groupby("subject")["grade_value"]
        .agg(grade_count="count", average="mean", median="median",
             minimum="min", maximum="max", std="std")
        .sort_values("average", ascending=False)
    )
    # Count whole grades 1..6 in order (4+ counts as a 4 here), zeros included.
    grade_counts = (
        graded["grade_raw"].str[0].astype(int).value_counts()
        .reindex(range(1, 7), fill_value=0)
    )
    return subject_summary, grade_counts


def print_summary(graded, subject_summary, grade_counts):
    print("\n=== Subject summary (sorted by average) ===")
    print(subject_summary.round(2).to_string())
    print(f"\nOverall average: {graded['grade_value'].mean():.2f} from {len(graded)} grades")
    print(f"Overall median:  {graded['grade_value'].median():.1f}")
    print("\n=== How often each grade occurs ===")
    print(grade_counts.to_string())
    print(f"Most frequent grade: {grade_counts.idxmax()} ({grade_counts.max()} times)")
    for period, n in graded["period"].value_counts().sort_index().items():
        print(f"Grades in period {period}: {n}")
    print(f"Grades with a date: {graded['date'].notna().sum()}"
          + (" -> no monthly trend possible" if graded["date"].isna().all() else ""))


def periods_label(graded):
    periods = sorted(graded["period"].unique())
    if len(periods) == 1:
        return f"period {periods[0]}"
    return "periods " + ", ".join(str(p) for p in periods)


# ---------------------------------------------------------------------------
# STEP 6: 2x2 dashboard
# ---------------------------------------------------------------------------
def empty_chart(ax, title, message):
    ax.set_title(title, fontsize=13, loc="left")
    ax.text(0.5, 0.5, message, ha="center", va="center", color="gray",
            fontsize=11, transform=ax.transAxes, wrap=True)
    ax.set_xticks([])
    ax.set_yticks([])


def trend_subjects(graded, subject_summary):
    """Subjects for the progress chart: enough grades, at most TREND_MAX_SUBJECTS."""
    counts = subject_summary["grade_count"].sort_values(ascending=False, kind="stable")
    chosen = counts[counts >= TREND_MIN_GRADES]
    if chosen.empty:
        chosen = counts[counts >= 2]
    return list(chosen.index[:TREND_MAX_SUBJECTS])


def build_dashboard(graded, subject_summary, grade_counts, png_path):
    overall_mean = graded["grade_value"].mean()
    n_subjects = len(subject_summary)
    fig, axes = plt.subplots(2, 2, figsize=(17, max(12, 6 + n_subjects * 0.35)),
                             layout="constrained")
    fig.suptitle(f"My academic dashboard - {periods_label(graded)}, current grades",
                 fontsize=18, fontweight="bold")

    # 1. Average grade by subject (sorted horizontal bar)
    ax = axes[0, 0]
    by_avg = subject_summary.sort_values("average")
    enough = by_avg["grade_count"] >= MIN_GRADES
    colors = ["tab:blue" if ok else "lightgray" for ok in enough]
    bars = ax.barh(by_avg.index, by_avg["average"], color=colors, edgecolor="gray")
    for bar, n in zip(bars, by_avg["grade_count"]):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f"n={n}", va="center", fontsize=8)
    ax.axvline(overall_mean, color="red", linestyle="--",
               label=f"Overall average = {overall_mean:.2f}")
    ax.set_xlim(0, 6.6)
    ax.set_title("1. Average grade by subject", fontsize=13, loc="left")
    ax.set_xlabel("Average grade (1-6)")
    ax.set_ylabel("Subject")
    ax.tick_params(axis="y", labelsize=8)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(plt.Rectangle((0, 0), 1, 1, color="lightgray"))
    labels.append(f"Fewer than {MIN_GRADES} grades - compare with care")
    ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.09),
              ncol=2, fontsize=8, frameon=False)

    # 2. Grade distribution (ordered bar)
    ax = axes[0, 1]
    bars = ax.bar(grade_counts.index.astype(str), grade_counts.values,
                  color="tab:green", edgecolor="white")
    ax.bar_label(bars, padding=2)
    ax.set_title("2. How often each grade occurs", fontsize=13, loc="left")
    ax.set_xlabel("Grade")
    ax.set_ylabel("Number of grades")
    ax.set_ylim(0, max(grade_counts.max(), 1) * 1.15)

    # 3. Progress - no dates in the export, so use the order grades were added.
    ax = axes[1, 0]
    title = "3. Progress in order of entry (export has no dates)"
    subjects = trend_subjects(graded, subject_summary)
    if not subjects:
        empty_chart(ax, title, "Not enough grades per subject to show progress yet.")
    else:
        for subject in subjects:
            s = graded[graded["subject"] == subject].sort_values("grade_no")
            running = s["grade_value"].expanding().mean()
            line, = ax.plot(s["grade_no"], running, marker="o",
                            label=f"{subject} (running average)")
            ax.scatter(s["grade_no"], s["grade_value"], color=line.get_color(),
                       alpha=0.25, s=40)
        ax.set_title(title, fontsize=13, loc="left")
        ax.set_xlabel("Grade number in the subject (1 = first grade)")
        ax.set_ylabel("Grade")
        ax.set_ylim(0.5, 6.5)
        ax.xaxis.get_major_locator().set_params(integer=True)
        ax.grid(alpha=0.3)
        min_n = int(subject_summary.loc[subjects, "grade_count"].min())
        ax.legend(fontsize=8, title=f"Subjects with the most grades ({min_n}+) - "
                  "faint dots = single grades", title_fontsize=8)

    # 4. Grade consistency (box plot), only subjects with enough grades
    ax = axes[1, 1]
    title = f"4. Spread of grades per subject ({MIN_GRADES}+ grades)"
    box_subjects = (subject_summary[subject_summary["grade_count"] >= MIN_GRADES]
                    .sort_values("median").index)
    if box_subjects.empty:
        empty_chart(ax, title, f"No subject has {MIN_GRADES} or more grades yet.")
    else:
        plot_data = [graded.loc[graded["subject"] == s, "grade_value"].values
                     for s in box_subjects]
        ax.boxplot(plot_data, tick_labels=box_subjects, orientation="horizontal")
        ax.set_title(title, fontsize=13, loc="left")
        ax.set_xlabel("Grade")
        ax.set_xlim(0.5, 6.5)
        ax.tick_params(axis="y", labelsize=8)
        ax.grid(axis="x", alpha=0.3)

    fig.supxlabel(f"Source: own Librus export, {periods_label(graded)}. Only numeric "
                  "grades; corrected grades count once (newest). Small samples - "
                  "see n= labels.", fontsize=9, color="dimgray")
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# EXTENSION: Grade Alert System (review flags, not predictions)
# ---------------------------------------------------------------------------
def recent_decline(s):
    """Newer grades clearly lower than older ones (periods if possible, else halves)."""
    by_period = s.groupby("period")["grade_value"]
    counts = by_period.count()
    if len(counts) >= 2 and (counts >= DECLINE_MIN_PER_PERIOD).all():
        means = by_period.mean()
        return means.iloc[-2] - means.iloc[-1] >= DECLINE_DROP
    values = s["grade_value"]
    if len(values) >= DECLINE_MIN_GRADES:
        half = len(values) // 2
        return values.iloc[:half].mean() - values.iloc[half:].mean() >= DECLINE_DROP
    return False


def alert_flags(graded, subject):
    s = graded[graded["subject"] == subject].sort_values("grade_no")
    values = s["grade_value"]
    if len(values) < MIN_GRADES:
        return ["INSUFFICIENT DATA"]  # the other rules need enough grades to mean anything
    flags = []
    if values.mean() < REVIEW_THRESHOLD:
        flags.append("REVIEW AVERAGE")
    if recent_decline(s):
        flags.append("RECENT DECLINE")
    if len(values) >= VARIABILITY_MIN_GRADES and values.std() > VARIABILITY_STD:
        flags.append("HIGH VARIABILITY")
    return flags


def grade_alerts(graded, all_subjects):
    return pd.DataFrame({
        "subject": all_subjects,
        "grade_count": [int((graded["subject"] == s).sum()) for s in all_subjects],
        "flags": [", ".join(alert_flags(graded, s)) or "-" for s in all_subjects],
    })


# ---------------------------------------------------------------------------
# HTML report: one self-contained page (image embedded, no internet needed)
# ---------------------------------------------------------------------------
def esc(value):
    return html.escape(str(value))


def fmt(value, digits=2):
    return "–" if pd.isna(value) else f"{value:.{digits}f}"


def summary_rows(subject_summary):
    rows = []
    for subject, r in subject_summary.iterrows():
        few = r["grade_count"] < MIN_GRADES
        width = r["average"] / 6 * 100
        rows.append(
            f'<tr class="{"few" if few else ""}">'
            f"<td>{esc(subject)}</td>"
            f'<td class="num">{int(r["grade_count"])}</td>'
            f'<td class="avg"><div class="bar" style="width:{width:.0f}%"></div>'
            f'<span>{fmt(r["average"])}</span></td>'
            f'<td class="num">{fmt(r["median"], 1)}</td>'
            f'<td class="num">{fmt(r["minimum"], 2 if r["minimum"] % 1 else 0)}</td>'
            f'<td class="num">{fmt(r["maximum"], 2 if r["maximum"] % 1 else 0)}</td>'
            f'<td class="num">{fmt(r["std"])}</td>'
            "</tr>"
        )
    return "\n".join(rows)


def alert_rows(alerts):
    rows = []
    for _, r in alerts.iterrows():
        flags = [f for f in r["flags"].split(", ") if f != "-"]
        chips = "".join(
            f'<span class="chip {esc(f.split()[0].lower())}">{esc(f)}</span>'
            for f in flags
        ) or '<span class="ok">no flag</span>'
        rows.append(f"<tr><td>{esc(r['subject'])}</td>"
                    f'<td class="num">{r["grade_count"]}</td><td>{chips}</td></tr>')
    return "\n".join(rows)


def plus_minus_note(unmapped, plus, minus):
    if plus is not None or minus is not None:
        return (f"<li>Grades with + or &minus; were counted as "
                f"+{plus if plus is not None else 0} / &minus;{minus if minus is not None else 0}.</li>")
    if unmapped:
        return (f"<li>{unmapped} grade(s) with + or &minus; were left out, because their "
                "value was not agreed. Run with <code>--plus</code> / <code>--minus</code> "
                "to count them.</li>")
    return ""


def build_html(graded, all_subjects, subject_summary, grade_counts, alerts,
               png_path, unmapped=0, plus=None, minus=None):
    image_b64 = base64.b64encode(Path(png_path).read_bytes()).decode("ascii")
    overall_mean = graded["grade_value"].mean()
    cards = [
        ("Grades", len(graded),
         f"in {graded['subject'].nunique()} of {len(all_subjects)} subjects"),
        ("Average", f"{overall_mean:.2f}", "all numeric grades"),
        ("Median", f"{graded['grade_value'].median():g}", "middle grade"),
        ("Most frequent", grade_counts.idxmax(), f"{grade_counts.max()} times"),
        ("4 or higher", f"{(graded['grade_value'] >= 4).mean():.0%}", "of all grades"),
    ]
    cards_html = "\n".join(
        f'<div class="card"><div class="label">{esc(label)}</div>'
        f'<div class="value">{esc(value)}</div><div class="sub">{esc(sub)}</div></div>'
        for label, value, sub in cards
    )
    label = periods_label(graded)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My academic dashboard</title>
<style>
  :root {{
    --bg: #f6f7f9; --panel: #ffffff; --text: #1d2330; --muted: #677085;
    --line: #e3e6ec; --accent: #1f77b4; --bar: #cfe0f1;
    --warn-bg: #fff1d6; --warn: #8a5a00; --info-bg: #e9ecf2; --info: #4a5468;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #14171c; --panel: #1d2128; --text: #e7e9ee; --muted: #9aa3b5;
      --line: #2e343e; --accent: #6aa9e0; --bar: #2a4560;
      --warn-bg: #4a3710; --warn: #ffd58a; --info-bg: #2b313b; --info: #c2c9d6;
    }}
    .dashboard img {{ background: #fff; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--text);
         font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  main {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px 48px; }}
  header h1 {{ margin: 0 0 4px; font-size: 28px; }}
  header p {{ margin: 0; color: var(--muted); }}
  .question {{ margin: 20px 0 24px; padding: 14px 18px; border-left: 4px solid var(--accent);
              background: var(--panel); border-radius: 6px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
           gap: 12px; margin-bottom: 24px; }}
  .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; }}
  .card .label {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: .04em; }}
  .card .value {{ font-size: 30px; font-weight: 700; margin: 2px 0; }}
  .card .sub {{ color: var(--muted); font-size: 13px; }}
  section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
            padding: 18px 20px; margin-bottom: 24px; }}
  section h2 {{ margin: 0 0 4px; font-size: 19px; }}
  section > p {{ margin: 0 0 14px; color: var(--muted); }}
  .dashboard img {{ width: 100%; height: auto; border-radius: 6px; display: block; }}
  .grid {{ display: grid; grid-template-columns: 3fr 2fr; gap: 24px; }}
  @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .grid section {{ margin-bottom: 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th, td {{ padding: 6px 8px; border-bottom: 1px solid var(--line); text-align: left; }}
  th {{ color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.avg {{ position: relative; min-width: 110px; }}
  td.avg .bar {{ position: absolute; left: 0; top: 5px; bottom: 5px; background: var(--bar); border-radius: 3px; }}
  td.avg span {{ position: relative; font-weight: 600; font-variant-numeric: tabular-nums; padding-left: 6px; }}
  tr.few td {{ color: var(--muted); }}
  tr.few td.avg .bar {{ opacity: .45; }}
  .chip {{ display: inline-block; font-size: 11px; font-weight: 700; padding: 2px 8px;
          border-radius: 999px; margin: 1px 4px 1px 0; background: var(--warn-bg); color: var(--warn);
          white-space: nowrap; }}
  .chip.insufficient {{ background: var(--info-bg); color: var(--info); }}
  .ok {{ color: var(--muted); font-size: 13px; }}
  ul {{ margin: 0; padding-left: 20px; }}
  li {{ margin: 4px 0; }}
  footer {{ color: var(--muted); font-size: 13px; text-align: center; }}
</style>
</head>
<body>
<main>
  <header>
    <h1>My academic dashboard</h1>
    <p>{esc(label.capitalize())} &middot; current grades from a Librus export &middot; generated {date.today():%d.%m.%Y}</p>
  </header>

  <div class="question"><strong>Question:</strong> What does my academic performance look like,
  how has it changed over time, and which subjects may deserve more attention?</div>

  <div class="cards">
{cards_html}
  </div>

  <section class="dashboard">
    <h2>Dashboard</h2>
    <p>Averages, grade frequency, progress in order of entry, and spread per subject.</p>
    <img src="data:image/png;base64,{image_b64}" alt="2x2 dashboard: average grade by subject,
    grade frequency, running average in order of entry, and box plot of grades per subject">
  </section>

  <div class="grid">
    <section>
      <h2>Subject summary</h2>
      <p>Sorted by average. Grey rows have fewer than {MIN_GRADES} grades, so compare them with care.</p>
      <table>
        <thead><tr><th>Subject</th><th class="num">n</th><th>Average</th><th class="num">Median</th>
        <th class="num">Min</th><th class="num">Max</th><th class="num">Std</th></tr></thead>
        <tbody>
{summary_rows(subject_summary)}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Grade alerts</h2>
      <p>A flag means "look closer". It is not a prediction or a school grade.</p>
      <table>
        <thead><tr><th>Subject</th><th class="num">n</th><th>Flags</th></tr></thead>
        <tbody>
{alert_rows(alerts)}
        </tbody>
      </table>
    </section>
  </div>

  <section style="margin-top:24px">
    <h2>How the data was prepared</h2>
    <ul>
      <li>Only grades 1&ndash;6 are counted. Marks like np, nb, bz, T and lone +/&minus; were removed, never turned into 0.</li>
      <li>A corrected grade (<code>[ old new ]</code> in Librus) counts once, as the newest grade.</li>
      {plus_minus_note(unmapped, plus, minus)}
      <li>The export has no dates, so chart 3 shows the order grades were added, not real time.</li>
      <li>Alert rules: fewer than {MIN_GRADES} grades &rarr; INSUFFICIENT DATA; average below {REVIEW_THRESHOLD}
          &rarr; REVIEW AVERAGE; newer grades (later period, or newer half with {DECLINE_MIN_GRADES}+ grades)
          {DECLINE_DROP}+ lower &rarr; RECENT DECLINE; {VARIABILITY_MIN_GRADES}+ grades and std above
          {VARIABILITY_STD} &rarr; HIGH VARIABILITY.</li>
    </ul>
  </section>

  <footer>No name, student ID or teacher comments are included on this page.</footer>
</main>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Whole pipeline
# ---------------------------------------------------------------------------
def analyse(wide, long_path, png_path, html_path, plus=None, minus=None):
    """Run steps 3-6 on a cleaned wide table and write all output files."""
    df, all_subjects = to_long(wide)
    df = add_grade_values(df, plus, minus)
    Path(long_path).parent.mkdir(parents=True, exist_ok=True)
    df.drop(columns="grade_value").to_csv(long_path, index=False, encoding="utf-8-sig")
    print_validation(df, all_subjects)

    graded = df.dropna(subset=["grade_value"])
    if graded.empty:
        raise ValueError("No numeric grades found, so there is nothing to analyse yet.")
    unmapped = len(df) - len(graded)

    subject_summary, grade_counts = summarise(graded)
    print_summary(graded, subject_summary, grade_counts)

    build_dashboard(graded, subject_summary, grade_counts, png_path)
    print(f"\nSaved dashboard to {png_path}")

    alerts = grade_alerts(graded, all_subjects)
    print("\n=== Grade alerts (a reason to look closer, not a judgement) ===")
    print(alerts.to_string(index=False))

    page = build_html(graded, all_subjects, subject_summary, grade_counts, alerts,
                      png_path, unmapped, plus, minus)
    Path(html_path).parent.mkdir(parents=True, exist_ok=True)
    Path(html_path).write_text(page, encoding="utf-8")
    print(f"\nSaved HTML report to {html_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyse a cleaned Librus grades CSV.")
    parser.add_argument("--csv", default="synergia.csv", help="input CSV (default: synergia.csv)")
    parser.add_argument("--out-dir", type=Path, default=Path("."),
                        help="folder for the output files (default: this folder)")
    parser.add_argument("--plus", type=float, help='value added for "+", e.g. 0.5 (default: "4+" is left out)')
    parser.add_argument("--minus", type=float, help='value taken for "-", e.g. 0.25 (default: "4-" is left out)')
    args = parser.parse_args()

    out = args.out_dir
    try:
        analyse(load_wide(args.csv),
                long_path=out / "grades_raw.csv",
                png_path=out / "charts" / "my_academic_dashboard.png",
                html_path=out / "my_academic_dashboard.html",
                plus=args.plus, minus=args.minus)
    except ValueError as err:
        raise SystemExit(f"Error: {err}")


if __name__ == "__main__":
    main()
