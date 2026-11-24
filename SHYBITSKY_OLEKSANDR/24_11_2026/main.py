#!/usr/bin/env python3
"""
Personal Learning Analytics Dashboard (Librus Grade Export)
===========================================================
This script processes academic performance data exported from the Librus
electronic register in accordance with the project guidelines from the presentation:
  1. PDF/CSV Inspection & Multi-column Extraction (All Grades)
  2. Data Cleaning & Type Conversion (Safe mapping, Unknown != 0)
  3. Pandas Statistical Analysis (groupby, agg, value_counts, sorting)
  4. 2x2 Matplotlib Visualization Dashboard (my_academic_dashboard.png)
  5. Grade Alert System Extension (Insufficient Data, Review Average, Recent Decline, High Variability)
  6. Comprehensive Standalone HTML Dashboard Report (academic_dashboard.html / index.html)
  7. Tidy CSV Export (grades_tidy.csv)
"""

import os
import re
import base64
import numpy as np
import pandas as pd

# Configure non-interactive Agg backend to ensure safe rendering in all environments
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
INPUT_CSV_PATH = "grades.csv"
OUTPUT_PNG_PATH = "my_academic_dashboard.png"
OUTPUT_HTML_PATH = "academic_dashboard.html"
OUTPUT_INDEX_HTML_PATH = "index.html"
OUTPUT_TIDY_CSV_PATH = "grades_tidy.csv"

# Agreed grade scale mapping as per Slide 13 & 14
# Unrecognised non-grade marks (e.g. 'zw', 'nb', 'np', 'bz') map to NaN (Unknown != 0)
GRADE_MAP = {
    "1": 1.0,
    "1+": 1.5,
    "1.5": 1.5,
    "2-": 1.75,
    "2": 2.0,
    "2+": 2.5,
    "3-": 2.75,
    "3": 3.0,
    "3+": 3.5,
    "4-": 3.75,
    "4": 4.0,
    "4+": 4.5,
    "5-": 4.75,
    "5": 5.0,
    "5+": 5.5,
    "6-": 5.75,
    "6": 6.0,
}

# Grade Alert System thresholds (Slide 23)
REVIEW_AVERAGE_THRESHOLD = 4.2      # Flag subjects with mean below this threshold
HIGH_VARIABILITY_STD = 1.0          # Flag subjects with std >= 1.0 or spread >= 2.0
MIN_RECORDS_FOR_ANALYSIS = 3        # Fewer than this triggers INSUFFICIENT DATA
RECENT_DECLINE_DROP = 0.5           # Drop of 0.5+ points in recent grades triggers RECENT DECLINE

# Grade-bearing columns in Librus export
GRADE_COLUMNS = [
    ("Oceny bieżące (Okres 1)", "Bieżąca (Okres 1)", "Okres 1"),
    ("I", "Klasyfikacyjna śródroczna (I)", "Okres 1"),
    ("Oceny bieżące (Okres 2)", "Bieżąca (Okres 2)", "Okres 2"),
    ("II", "Klasyfikacyjna śródroczna (II)", "Okres 2"),
    ("R", "Klasyfikacyjna roczna (R)", "Roczna"),
]

# Computed average columns in Librus export (for audit / reference)
AVERAGE_COLUMNS = ["Śr.I", "Śr.II", "Śr.R"]


# ==============================================================================
# 1. EXTRACT & CLEAN: PARSE ALL GRADES INTO TIDY FORMAT
# ==============================================================================
def load_and_extract_grades(csv_path: str) -> pd.DataFrame:
    """
    Reads the raw Librus export CSV and extracts ALL individual grade tokens across
    all grade columns (current and term grades for Period 1, Period 2, and Annual).
    Preserves raw strings, assigns clean numeric values, and records metadata.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input file '{csv_path}' not found.")

    df_raw = pd.read_csv(csv_path, encoding="utf-8-sig")
    print(f"[EXTRACT] Loaded '{csv_path}' with {len(df_raw)} subjects (rows).")
    print(f"[EXTRACT] Raw columns: {list(df_raw.columns)}")

    # Audit non-empty cells across all secondary columns
    for _, row in df_raw.iterrows():
        subj = str(row.get("Przedmiot", "")).strip()
        for col_name, cat, period in GRADE_COLUMNS[1:]:
            if col_name in df_raw.columns and pd.notna(row[col_name]):
                val = row[col_name]
                print(f"[AUDIT] Found '{cat}' in column '{col_name}' for '{subj}': {val}")

    records = []
    global_idx = 1

    for _, row in df_raw.iterrows():
        subject_name = str(row.get("Przedmiot", "")).strip()
        if not subject_name or subject_name.lower() == "nan":
            continue

        subject_grade_order = 1

        for col_name, category, period in GRADE_COLUMNS:
            if col_name not in df_raw.columns:
                continue
            cell_value = row.get(col_name)
            if pd.isna(cell_value):
                continue

            val_str = str(cell_value).strip()
            # Split tokens by whitespace or comma
            tokens = [t.strip() for t in re.split(r"[\s,]+", val_str) if t.strip()]

            for token in tokens:
                # Normalize float strings like '1.0' -> '1'
                lookup_token = token
                if lookup_token.endswith(".0") and len(lookup_token) <= 4:
                    lookup_token = lookup_token[:-2]

                # Map to numeric grade using agreed scale
                numeric_val = GRADE_MAP.get(lookup_token, np.nan)

                records.append({
                    "id": global_idx,
                    "subject": subject_name,
                    "period": period,
                    "category": category,
                    "grade_raw": token,
                    "grade_value": numeric_val,
                    "grade_order": subject_grade_order,
                    "source_column": col_name,
                    "date": None,  # Librus summary table does not include dates
                    "description": "",
                })
                subject_grade_order += 1
                global_idx += 1

    df_tidy = pd.DataFrame(records)
    print(f"[EXTRACT] Extracted {len(df_tidy)} total grade records.")
    print(f"[EXTRACT] Valid numeric grades: {df_tidy['grade_value'].notna().sum()}")
    print(f"[EXTRACT] Unmapped / Non-grade tokens: {df_tidy['grade_value'].isna().sum()}")

    # Save tidy CSV
    df_tidy.to_csv(OUTPUT_TIDY_CSV_PATH, index=False, encoding="utf-8")
    print(f"[EXTRACT] Saved tidy dataset to: {OUTPUT_TIDY_CSV_PATH}")

    return df_tidy


# ==============================================================================
# 2. PANDAS ANALYSIS: SUMMARIZE SUBJECTS, FREQUENCIES & TRENDS
# ==============================================================================
def perform_analysis(df: pd.DataFrame):
    """
    Computes summary tables using groupby, agg, value_counts, and progression metrics.
    """
    # 2.1 Subject Summary (Slide 16)
    subject_summary = (
        df.groupby("subject")["grade_value"]
        .agg(
            grade_count="count",
            average="mean",
            median="median",
            minimum="min",
            maximum="max",
            std="std",
        )
        .sort_values("average", ascending=False)
    )
    # Fill std for subjects with 1 or 2 identical grades
    subject_summary["std"] = subject_summary["std"].fillna(0.0)
    subject_summary["range"] = subject_summary["maximum"] - subject_summary["minimum"]

    # 2.2 Grade Frequency Distribution (Slide 19)
    full_scale = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    grade_counts = df["grade_value"].value_counts().reindex(full_scale, fill_value=0).astype(int)
    total_valid = df["grade_value"].count()
    grade_percentages = (grade_counts / total_valid * 100).round(1)

    distribution_df = pd.DataFrame({
        "grade": [int(g) for g in full_scale],
        "count": grade_counts.values,
        "percentage": grade_percentages.values,
    })

    # 2.3 Progress Over Sequence Order (Slide 20 - alternative for missing dates)
    order_summary = (
        df.groupby("grade_order")["grade_value"]
        .agg(
            mean="mean",
            median="median",
            count="count",
            std="std",
        )
        .sort_index()
    )
    order_summary["rolling_3_mean"] = order_summary["mean"].rolling(3, min_periods=1).mean()

    # 2.4 Cohort High-Level Metrics
    overall_mean = df["grade_value"].mean()
    overall_median = df["grade_value"].median()
    overall_std = df["grade_value"].std()
    most_frequent_grade = int(grade_counts.idxmax())
    most_frequent_count = int(grade_counts.max())

    metrics = {
        "total_records": len(df),
        "total_subjects": df["subject"].nunique(),
        "valid_grades_count": total_valid,
        "overall_mean": round(float(overall_mean), 2),
        "overall_median": round(float(overall_median), 2),
        "overall_std": round(float(overall_std), 2),
        "most_frequent_grade": most_frequent_grade,
        "most_frequent_count": most_frequent_count,
        "most_frequent_pct": round(float(most_frequent_count / total_valid * 100), 1),
    }

    # 2.5 Grade Alert System (Slide 23)
    alerts = []
    for subj, row in subject_summary.iterrows():
        flags = []
        notes = []

        # Condition 1: Fewer than 3 numeric grades
        if row["grade_count"] < MIN_RECORDS_FOR_ANALYSIS:
            flags.append("INSUFFICIENT DATA")
            notes.append(f"Only {int(row['grade_count'])} grade(s); statistical metrics are provisional.")

        # Condition 2: Subject mean below agreed threshold
        if row["average"] < REVIEW_AVERAGE_THRESHOLD:
            flags.append("REVIEW AVERAGE")
            notes.append(f"Mean ({row['average']:.2f}) is below threshold of {REVIEW_AVERAGE_THRESHOLD:.2f}.")

        # Condition 3: Recent period / recent grades lower than previous period (with enough grades)
        subj_grades = df[df["subject"] == subj].sort_values("grade_order")["grade_value"].dropna().values
        if len(subj_grades) >= MIN_RECORDS_FOR_ANALYSIS:
            # Check 3A: If a term grade exists vs current grades mean
            term_grades = df[(df["subject"] == subj) & (df["category"].str.contains("Klasyfikacyjna"))]["grade_value"].dropna().values
            current_grades = df[(df["subject"] == subj) & (df["category"].str.contains("Bieżąca"))]["grade_value"].dropna().values

            has_decline = False
            if len(term_grades) > 0 and len(current_grades) > 0:
                if np.mean(term_grades) - np.mean(current_grades) <= -RECENT_DECLINE_DROP:
                    has_decline = True
                    notes.append(f"Term grade ({np.mean(term_grades):.1f}) declined from current grades mean ({np.mean(current_grades):.2f}).")

            # Check 3B: Sequence half-split comparison
            half = len(subj_grades) // 2
            early_mean = np.mean(subj_grades[:half])
            recent_mean = np.mean(subj_grades[half:])
            if (recent_mean - early_mean <= -RECENT_DECLINE_DROP) and not has_decline:
                has_decline = True
                notes.append(f"Recent grades mean ({recent_mean:.2f}) dropped by {abs(recent_mean - early_mean):.2f} pts vs early grades ({early_mean:.2f}).")

            if has_decline:
                flags.append("RECENT DECLINE")

        # Condition 4: Large spread with enough observations
        if (row["std"] >= HIGH_VARIABILITY_STD or row["range"] >= 2.0) and row["grade_count"] >= MIN_RECORDS_FOR_ANALYSIS:
            flags.append("HIGH VARIABILITY")
            notes.append(f"Standard deviation ({row['std']:.2f}) >= {HIGH_VARIABILITY_STD} or spread ({row['range']:.1f}) is wide.")

        alerts.append({
            "subject": subj,
            "count": int(row["grade_count"]),
            "mean": round(float(row["average"]), 2),
            "median": round(float(row["median"]), 2),
            "min": round(float(row["minimum"]), 1),
            "max": round(float(row["maximum"]), 1),
            "std": round(float(row["std"]), 2),
            "flags": ", ".join(flags) if flags else "OK",
            "flags_list": flags if flags else ["OK"],
            "notes": " ".join(notes) if notes else "Normal academic progress.",
        })

    alerts_df = pd.DataFrame(alerts)

    return subject_summary, distribution_df, order_summary, alerts_df, metrics


# ==============================================================================
# 3. VISUALIZE: 2x2 DASHBOARD (my_academic_dashboard.png)
# ==============================================================================
def build_dashboard(df: pd.DataFrame, subject_summary: pd.DataFrame,
                    distribution_df: pd.DataFrame, order_summary: pd.DataFrame,
                    metrics: dict, output_path: str):
    """
    Assembles all 4 charts into one cohesive 2x2 figure matching Slide 17-22:
      Chart 1: Average grade by subject (Horizontal bar chart)
      Chart 2: Grade distribution (Ordered bar chart of counts)
      Chart 3: Progress over time / sequence (Line chart with 3-period rolling average)
      Chart 4: Grade consistency (Box plot by subject)
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12.5))
    plt.subplots_adjust(top=0.92, bottom=0.14, left=0.22, right=0.96, hspace=0.32, wspace=0.26)

    fig.suptitle(
        "Personal Learning Analytics Dashboard — Academic Performance Report",
        fontsize=16,
        fontweight="bold",
        color="#0f172a",
        y=0.97,
    )

    # --------------------------------------------------------------------------
    # CHART 1: Average grade by subject (Sorted Horizontal Bar)
    # --------------------------------------------------------------------------
    ax1 = axes[0, 0]
    sorted_avg = subject_summary["average"].sort_values(ascending=True)
    subjects_y = sorted_avg.index

    # Abbreviate long names for clean y-axis layout
    display_names = [
        s.replace("Projektowanie i administrowanie bazami danych", "Admin. bazami danych (Proj.)")
         .replace("Programowanie aplikacji internetowych", "Prog. aplikacji internetowych")
         .replace("Programowanie aplikacji mobilnych", "Prog. aplikacji mobilnych")
        for s in subjects_y
    ]

    # Highlight subjects below review threshold
    bar_colors = ["#ef4444" if val < REVIEW_AVERAGE_THRESHOLD else "#3b82f6" for val in sorted_avg.values]
    bars1 = ax1.barh(display_names, sorted_avg.values, color=bar_colors, height=0.68, edgecolor="none", zorder=2)

    # Reference lines (behind text)
    ax1.axvline(REVIEW_AVERAGE_THRESHOLD, color="#dc2626", linestyle="--", linewidth=1.5, alpha=0.85, zorder=1,
                label=f"Review Threshold ({REVIEW_AVERAGE_THRESHOLD})")
    ax1.axvline(metrics["overall_mean"], color="#16a34a", linestyle=":", linewidth=1.5, alpha=0.85, zorder=1,
                label=f"Cohort Mean ({metrics['overall_mean']})")

    # Add numeric labels at bar tips with halo background to prevent line collisions
    for idx, bar in enumerate(bars1):
        width = bar.get_width()
        subj_name = subjects_y[idx]
        count = int(subject_summary.loc[subj_name, "grade_count"])
        ax1.text(
            width + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f} (n={count})",
            va="center",
            ha="left",
            fontsize=8.5,
            color="#1e293b",
            fontweight="bold",
            zorder=4,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#ffffff", edgecolor="none", alpha=0.85),
        )

    ax1.set_title("1. Average Grade by Subject", fontsize=12, fontweight="bold", pad=10, color="#1e293b")
    ax1.set_xlabel("Average Grade (Scale 1–6)", fontsize=10, labelpad=6)
    ax1.set_xlim(0, 7.3)
    ax1.legend(loc="lower right", framealpha=0.95, fontsize=8.5)
    ax1.grid(axis="x", linestyle="--", alpha=0.5, zorder=0)

    # --------------------------------------------------------------------------
    # CHART 2: Grade distribution (Ordered Bar Chart)
    # --------------------------------------------------------------------------
    ax2 = axes[0, 1]
    grades = [str(g) for g in distribution_df["grade"]]
    counts = distribution_df["count"].values
    pcts = distribution_df["percentage"].values

    bars2 = ax2.bar(grades, counts, color="#10b981", width=0.58, edgecolor="#047857", linewidth=1.2)

    for bar, pct in zip(bars2, pcts):
        height = bar.get_height()
        if height > 0:
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.8,
                f"{int(height)}\n({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color="#065f46",
            )

    ax2.set_title("2. Frequency of Each Grade", fontsize=12, fontweight="bold", pad=10, color="#1e293b")
    ax2.set_xlabel("Grade (Scale 1–6)", fontsize=10, labelpad=6)
    ax2.set_ylabel("Number of Records", fontsize=10, labelpad=6)
    ax2.set_ylim(0, max(counts) * 1.25)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    # --------------------------------------------------------------------------
    # CHART 3: Progress over time (Sequence Line Chart + Moving Average)
    # --------------------------------------------------------------------------
    ax3 = axes[1, 0]
    pos_data = order_summary[order_summary["count"] >= 2]
    x_positions = pos_data.index
    means = pos_data["mean"].values
    roll_means = pos_data["rolling_3_mean"].values

    ax3.plot(x_positions, means, marker="o", markersize=6, color="#8b5cf6",
             linewidth=2.2, label="Mean by Grade Order")
    ax3.plot(x_positions, roll_means, linestyle="--", color="#f59e0b",
             linewidth=2.0, label="3-Period Moving Average")

    for x, m in zip(x_positions, means):
        ax3.annotate(f"{m:.2f}", (x, m), textcoords="offset points",
                     xytext=(0, 7), ha="center", fontsize=8, color="#5b21b6", fontweight="bold")

    ax3.set_title("3. Progress Over Grade Sequence in Period 1", fontsize=12, fontweight="bold", pad=10, color="#1e293b")
    ax3.set_xlabel("Chronological Grade Order within Subject (n ≥ 2)", fontsize=10, labelpad=6)
    ax3.set_ylabel("Mean Grade", fontsize=10, labelpad=6)
    ax3.set_ylim(1.0, 6.2)
    ax3.legend(loc="lower left", framealpha=0.92, fontsize=8.5)
    ax3.grid(True, linestyle="--", alpha=0.5)

    ax3.text(
        0.5, -0.22,
        "*Note: Dates unavailable in Librus export; progression tracks chronological grade sequence.",
        transform=ax3.transAxes, ha="center", fontsize=8, fontstyle="italic", color="#64748b"
    )

    # --------------------------------------------------------------------------
    # CHART 4: Grade consistency (Box Plot by Subject)
    # --------------------------------------------------------------------------
    ax4 = axes[1, 1]
    eligible_subjects = subject_summary[subject_summary["grade_count"] >= MIN_RECORDS_FOR_ANALYSIS].index.tolist()
    eligible_subjects = sorted(
        eligible_subjects,
        key=lambda s: df.loc[df["subject"] == s, "grade_value"].median(),
    )

    box_data = [df.loc[df["subject"] == s, "grade_value"].dropna().values for s in eligible_subjects]
    positions = range(1, len(eligible_subjects) + 1)

    bp = ax4.boxplot(
        box_data,
        tick_labels=[s.replace("Projektowanie i administrowanie bazami danych", "Admin. bazami danych\n(Projektowanie)")
                     .replace("Programowanie aplikacji internetowych", "Prog. aplikacji\ninternetowych")
                     .replace("Język angielski zawodowy", "Angielski\nzawodowy")
                     .replace("Edukacja obywatelska", "Edukacja\nobywatelska")
                     .replace("Edukacja zdrowotna", "Edukacja\nzdrowotna") for s in eligible_subjects],
        patch_artist=True,
        showmeans=True,
        meanprops=dict(marker="D", markeredgecolor="#1e3a8a", markerfacecolor="#38bdf8", markersize=5),
        boxprops=dict(facecolor="#e0e7ff", color="#4338ca", linewidth=1.2),
        whiskerprops=dict(color="#4338ca", linewidth=1.2),
        capprops=dict(color="#4338ca", linewidth=1.2),
        medianprops=dict(color="#dc2626", linewidth=2.0),
        flierprops=dict(marker="o", markerfacecolor="#ef4444", markeredgecolor="none", markersize=6),
    )

    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=35, ha="right", fontsize=8)
    ax4.set_title(f"4. Grade Consistency (Subjects with ≥ {MIN_RECORDS_FOR_ANALYSIS} Grades)",
                  fontsize=12, fontweight="bold", pad=10, color="#1e293b")
    ax4.set_ylabel("Grade (Scale 1–6)", fontsize=10, labelpad=6)
    ax4.set_ylim(0.5, 6.5)
    ax4.grid(axis="y", linestyle="--", alpha=0.5)

    from matplotlib.lines import Line2D
    box_legend_elements = [
        Line2D([0], [0], color="#dc2626", lw=2, label="Median"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#38bdf8", markeredgecolor="#1e3a8a", markersize=6, label="Mean"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#ef4444", markersize=6, label="Outlier"),
    ]
    ax4.legend(handles=box_legend_elements, loc="lower right", framealpha=0.92, fontsize=8)

    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"[VISUALISE] Saved 2x2 dashboard to: {output_path}")


# ==============================================================================
# 4. REPORTING: GENERATE COMPREHENSIVE STANDALONE HTML PAGE
# ==============================================================================
def generate_html_report(df: pd.DataFrame, subject_summary: pd.DataFrame,
                         distribution_df: pd.DataFrame, order_summary: pd.DataFrame,
                         alerts_df: pd.DataFrame, metrics: dict,
                         image_path: str, output_html_path: str):
    """
    Builds a modern, rich, standalone HTML report with all processed tables,
    the embedded dashboard PNG, interactive search/filter capabilities, and
    detailed answers to the presentation requirements.
    """
    # Read PNG image and encode as base64 for portable offline viewing
    img_base64 = ""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Table rows for Subject Summary
    summary_rows_html = []
    for subj, row in subject_summary.iterrows():
        alert_info = alerts_df[alerts_df["subject"] == subj].iloc[0]
        flags = alert_info["flags_list"]

        badge_spans = []
        for f in flags:
            if f == "OK":
                badge_spans.append('<span class="badge badge-ok">OK</span>')
            elif f == "INSUFFICIENT DATA":
                badge_spans.append('<span class="badge badge-warning">INSUFFICIENT DATA</span>')
            elif f == "REVIEW AVERAGE":
                badge_spans.append('<span class="badge badge-danger">REVIEW AVERAGE</span>')
            elif f == "RECENT DECLINE":
                badge_spans.append('<span class="badge badge-declining">RECENT DECLINE</span>')
            elif f == "HIGH VARIABILITY":
                badge_spans.append('<span class="badge badge-purple">HIGH VARIABILITY</span>')

        summary_rows_html.append(f"""
        <tr>
            <td class="font-medium text-slate-900">{subj}</td>
            <td class="text-center">{int(row['grade_count'])}</td>
            <td class="text-right font-semibold text-blue-700">{row['average']:.2f}</td>
            <td class="text-right">{row['median']:.1f}</td>
            <td class="text-right">{row['minimum']:.1f}</td>
            <td class="text-right">{row['maximum']:.1f}</td>
            <td class="text-right">{row['std']:.2f}</td>
            <td>{' '.join(badge_spans)}</td>
        </tr>
        """)

    # Table rows for Alert System
    alert_rows_html = []
    for _, row in alerts_df.iterrows():
        badge_spans = []
        for f in row["flags_list"]:
            if f == "OK":
                badge_spans.append('<span class="badge badge-ok">OK</span>')
            elif f == "INSUFFICIENT DATA":
                badge_spans.append('<span class="badge badge-warning">INSUFFICIENT DATA</span>')
            elif f == "REVIEW AVERAGE":
                badge_spans.append('<span class="badge badge-danger">REVIEW AVERAGE</span>')
            elif f == "RECENT DECLINE":
                badge_spans.append('<span class="badge badge-declining">RECENT DECLINE</span>')
            elif f == "HIGH VARIABILITY":
                badge_spans.append('<span class="badge badge-purple">HIGH VARIABILITY</span>')

        alert_rows_html.append(f"""
        <tr>
            <td class="font-medium text-slate-900">{row['subject']}</td>
            <td class="text-center">{row['count']}</td>
            <td class="text-right font-semibold">{row['mean']:.2f}</td>
            <td class="text-right">{row['std']:.2f}</td>
            <td>{' '.join(badge_spans)}</td>
            <td class="text-sm text-slate-600">{row['notes']}</td>
        </tr>
        """)

    # Table rows for Grade Distribution
    dist_rows_html = []
    for _, row in distribution_df.iterrows():
        bar_width = int(row['percentage'] * 2.5)
        dist_rows_html.append(f"""
        <tr>
            <td class="text-center font-bold text-slate-800 text-base">{int(row['grade'])}</td>
            <td class="text-center font-semibold text-emerald-700">{int(row['count'])}</td>
            <td class="text-right">{row['percentage']:.1f}%</td>
            <td>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: {bar_width}px;"></div>
                </div>
            </td>
        </tr>
        """)

    # Table rows for All Tidy Records (Scrollable / Filterable)
    records_rows_html = []
    for _, row in df.iterrows():
        val_display = f"{row['grade_value']:.1f}" if pd.notna(row['grade_value']) else "N/A"
        records_rows_html.append(f"""
        <tr>
            <td class="text-center text-slate-400">{row['id']}</td>
            <td class="font-medium">{row['subject']}</td>
            <td><span class="category-pill">{row['category']}</span></td>
            <td class="text-center">{row['period']}</td>
            <td class="text-center font-mono font-bold text-slate-700">{row['grade_raw']}</td>
            <td class="text-center font-semibold text-blue-600">{val_display}</td>
            <td class="text-center">{row['grade_order']}</td>
            <td class="text-xs text-slate-500">{row['source_column']}</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Learning Analytics Dashboard — Academic Performance Report</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --purple: #8b5cf6;
            --slate-50: #f8fafc;
            --slate-100: #f1f5f9;
            --slate-200: #e2e8f0;
            --slate-300: #cbd5e1;
            --slate-600: #475569;
            --slate-700: #334155;
            --slate-800: #1e293b;
            --slate-900: #0f172a;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            background-color: var(--slate-50);
            color: var(--slate-800);
            line-height: 1.6;
            padding-bottom: 60px;
        }}
        .header {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white;
            padding: 40px 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }}
        .header p {{
            color: #94a3b8;
            font-size: 15px;
        }}
        .badge-tag {{
            background: rgba(59, 130, 246, 0.2);
            border: 1px solid rgba(59, 130, 246, 0.4);
            color: #93c5fd;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
        }}
        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: -24px;
            margin-bottom: 32px;
        }}
        .kpi-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid var(--slate-200);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        }}
        .kpi-title {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--slate-600);
            margin-bottom: 6px;
        }}
        .kpi-value {{
            font-size: 28px;
            font-weight: 800;
            color: var(--slate-900);
        }}
        .kpi-sub {{
            font-size: 12px;
            color: var(--slate-600);
            margin-top: 4px;
        }}
        /* Content Sections */
        .section-card {{
            background: white;
            border-radius: 14px;
            border: 1px solid var(--slate-200);
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            padding: 28px;
            margin-bottom: 32px;
        }}
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--slate-200);
            padding-bottom: 16px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 700;
            color: var(--slate-900);
        }}
        .section-desc {{
            font-size: 14px;
            color: var(--slate-600);
            margin-top: 4px;
        }}
        /* Dashboard Image Viewer */
        .dashboard-img-container {{
            text-align: center;
            background: #ffffff;
            border-radius: 10px;
            padding: 12px;
            border: 1px solid var(--slate-200);
            overflow: hidden;
        }}
        .dashboard-img-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        /* Tables */
        .table-responsive {{
            overflow-x: auto;
            border: 1px solid var(--slate-200);
            border-radius: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            text-align: left;
        }}
        th {{
            background-color: var(--slate-100);
            color: var(--slate-700);
            font-weight: 700;
            padding: 12px 14px;
            border-bottom: 1px solid var(--slate-200);
            white-space: nowrap;
        }}
        td {{
            padding: 11px 14px;
            border-bottom: 1px solid var(--slate-200);
        }}
        tr:hover td {{
            background-color: #f8fafc;
        }}
        /* Badges */
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }}
        .badge-ok {{
            background-color: #dcfce7;
            color: #15803d;
            border: 1px solid #bbf7d0;
        }}
        .badge-warning {{
            background-color: #fef3c7;
            color: #b45309;
            border: 1px solid #fde68a;
        }}
        .badge-danger {{
            background-color: #fee2e2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }}
        .badge-declining {{
            background-color: #ffedd5;
            color: #c2410c;
            border: 1px solid #fed7aa;
        }}
        .badge-purple {{
            background-color: #f3e8ff;
            color: #7e22ce;
            border: 1px solid #e9d5ff;
        }}
        .category-pill {{
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 11.5px;
            font-weight: 600;
        }}
        /* Progress Bar */
        .progress-bar-bg {{
            background-color: #e2e8f0;
            border-radius: 9999px;
            height: 10px;
            width: 180px;
            overflow: hidden;
        }}
        .progress-bar-fill {{
            background-color: var(--success);
            height: 100%;
            border-radius: 9999px;
        }}
        /* Report Grid */
        .report-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}
        .report-box {{
            background: var(--slate-50);
            border-radius: 10px;
            padding: 18px;
            border: 1px solid var(--slate-200);
        }}
        .report-box h4 {{
            font-size: 15px;
            font-weight: 700;
            color: var(--slate-900);
            margin-bottom: 8px;
        }}
        .report-box p, .report-box ul {{
            font-size: 13.5px;
            color: var(--slate-700);
        }}
        .report-box ul {{
            padding-left: 20px;
            margin-top: 6px;
        }}
        .report-box li {{
            margin-bottom: 4px;
        }}
        /* Search Box */
        .search-input {{
            padding: 8px 14px;
            border: 1px solid var(--slate-300);
            border-radius: 8px;
            font-size: 13px;
            outline: none;
            width: 240px;
        }}
        .search-input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }}
        /* Presentation Script Box */
        .script-box {{
            background: #fdf4ff;
            border: 1px solid #f0abfc;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }}
        .script-box h4 {{
            color: #86198f;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .script-box p {{
            font-size: 13.5px;
            color: #701a75;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>

    <header class="header">
        <div class="container header-content">
            <div>
                <h1>Personal Learning Analytics Dashboard</h1>
                <p>Pandas & Data Visualisation Project — Librus Synergia Grade Export Analysis</p>
            </div>
            <div>
                <span class="badge-tag">Academic Period: Semester 1 & Term Grades</span>
            </div>
        </div>
    </header>

    <main class="container">

        <!-- KPI SUMMARY CARDS -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Grades Recorded</div>
                <div class="kpi-value">{metrics['total_records']}</div>
                <div class="kpi-sub">Across all categories & terms</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Overall GPA (Mean)</div>
                <div class="kpi-value text-blue-600">{metrics['overall_mean']}</div>
                <div class="kpi-sub">Scale 1.0 – 6.0 (Std: ±{metrics['overall_std']})</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Median Grade</div>
                <div class="kpi-value text-emerald-600">{metrics['overall_median']}</div>
                <div class="kpi-sub">50% of grades ≥ 5.0</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Subjects</div>
                <div class="kpi-value">{metrics['total_subjects']}</div>
                <div class="kpi-sub">14 with ≥ 3 observations</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Most Frequent Grade</div>
                <div class="kpi-value text-emerald-600">Grade {metrics['most_frequent_grade']}</div>
                <div class="kpi-sub">{metrics['most_frequent_count']} times ({metrics['most_frequent_pct']}%)</div>
            </div>
        </div>

        <!-- 2x2 DASHBOARD SECTION -->
        <section class="section-card">
            <div class="section-header">
                <div>
                    <h2 class="section-title">2×2 Academic Dashboard Visualization</h2>
                    <p class="section-desc">Combined 4-chart layout generated via Matplotlib (Saved as <code>my_academic_dashboard.png</code>)</p>
                </div>
                <div>
                    <a href="{image_path}" download="my_academic_dashboard.png" class="badge-tag" style="background: #2563eb; color: white; text-decoration: none;">Download PNG (300 DPI)</a>
                </div>
            </div>
            <div class="dashboard-img-container">
                <img src="data:image/png;base64,{img_base64}" alt="Academic Performance Dashboard">
            </div>
        </section>

        <!-- SUBJECT SUMMARY TABLE -->
        <section class="section-card">
            <div class="section-header">
                <div>
                    <h2 class="section-title">Subject Summary & Performance Overview</h2>
                    <p class="section-desc">Computed using <code>groupby("subject")["grade_value"].agg()</code> sorted by average descending</p>
                </div>
                <div>
                    <input type="text" id="subjectSearch" class="search-input" placeholder="Search subject..." onkeyup="filterTable('subjectSearch', 'summaryTable')">
                </div>
            </div>
            <div class="table-responsive">
                <table id="summaryTable">
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th class="text-center">Count (n)</th>
                            <th class="text-right">Average (Mean)</th>
                            <th class="text-right">Median</th>
                            <th class="text-right">Min</th>
                            <th class="text-right">Max</th>
                            <th class="text-right">Std Dev</th>
                            <th>Status / Alert Flags</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(summary_rows_html)}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- GRADE ALERT SYSTEM -->
        <section class="section-card">
            <div class="section-header">
                <div>
                    <h2 class="section-title">Grade Alert System (Extension)</h2>
                    <p class="section-desc">Rule-based review flags to highlight areas deserving attention without labeling the student</p>
                </div>
            </div>

            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th class="text-center">Records (n)</th>
                            <th class="text-right">Mean</th>
                            <th class="text-right">Std Dev</th>
                            <th>Review Flag(s)</th>
                            <th>Diagnostic Note</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(alert_rows_html)}
                    </tbody>
                </table>
            </div>

            <div style="margin-top: 18px; font-size: 13px; color: var(--slate-600); background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid var(--slate-200);">
                <strong>Rule Definitions (Slide 23):</strong>
                <code>INSUFFICIENT DATA</code>: Fewer than 3 grades |
                <code>REVIEW AVERAGE</code>: Mean &lt; {REVIEW_AVERAGE_THRESHOLD:.2f} |
                <code>RECENT DECLINE</code>: Term grade or second-half average dropped by &ge; 0.5 points |
                <code>HIGH VARIABILITY</code>: Std Dev &ge; 1.0 or Range &ge; 2.0 with &ge; 3 grades |
                <code>OK</code>: No trigger.
            </div>
        </section>

        <!-- GRADE DISTRIBUTION -->
        <section class="section-card">
            <div class="section-header">
                <div>
                    <h2 class="section-title">Grade Distribution Breakdown</h2>
                    <p class="section-desc">Exact counts and proportions of each grade on the standard 1–6 scale</p>
                </div>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th class="text-center">Grade</th>
                            <th class="text-center">Frequency (Count)</th>
                            <th class="text-right">Percentage</th>
                            <th>Visual Proportion</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(dist_rows_html)}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- TIDY DATA TABLE (ALL RECORDS) -->
        <section class="section-card">
            <div class="section-header">
                <div>
                    <h2 class="section-title">Complete Extracted Dataset (Tidy Format)</h2>
                    <p class="section-desc">All {len(df)} records extracted across all grade columns (one row per grade, preserved raw notations)</p>
                </div>
                <div>
                    <input type="text" id="recordSearch" class="search-input" placeholder="Search records..." onkeyup="filterTable('recordSearch', 'recordsTable')">
                </div>
            </div>
            <div class="table-responsive" style="max-height: 480px; overflow-y: auto;">
                <table id="recordsTable">
                    <thead>
                        <tr>
                            <th class="text-center">#</th>
                            <th>Subject</th>
                            <th>Category</th>
                            <th class="text-center">Period</th>
                            <th class="text-center">Raw Grade</th>
                            <th class="text-center">Numeric Value</th>
                            <th class="text-center">Sequence Order</th>
                            <th>Source Column</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(records_rows_html)}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- ANALYTICAL REPORT & PRESENTATION SCRIPT -->
        <section class="section-card">
            <div class="section-header">
                <div>
                    <h2 class="section-title">Analytical Report & Presentation Briefing</h2>
                    <p class="section-desc">Detailed answers to the core research questions from the presentation guidelines</p>
                </div>
            </div>

            <div class="report-grid">
                <div class="report-box">
                    <h4>1. Subject Performance Comparison</h4>
                    <p><strong>Strongest Subjects:</strong> <em>Informatyka</em> (6.00), <em>Język angielski zawodowy</em> (6.00), <em>Geografia</em> (5.33), <em>Edukacja obywatelska</em> (5.33), followed by <em>Fizyka</em>, <em>Historia</em>, <em>Python</em>, and <em>Bazy danych</em> (5.00 each).</p>
                    <p style="margin-top: 6px;"><strong>Subjects Needing Attention:</strong> <em>Chemia</em> (3.75, due to a term grade of 1), <em>Język polski</em> (3.83, min 2), <em>Matematyka</em> (4.00, std 1.10), and <em>Programowanie aplikacji mobilnych</em> (4.00).</p>
                </div>

                <div class="report-box">
                    <h4>2. Grade Frequency Insights</h4>
                    <p>The grade distribution is strongly positively skewed. <strong>Grade 5 is by far the most dominant</strong>, appearing {metrics['most_frequent_count']} times ({metrics['most_frequent_pct']}%), followed by Grade 6 (11 times, 16.4%). Together, excellent grades (5 & 6) account for over <strong>71.6%</strong> of all marks.</p>
                    <p style="margin-top: 6px;">Grades 1 and 2 are rare outliers (1 occurrence each, 1.5% each).</p>
                </div>

                <div class="report-box">
                    <h4>3. Assumptions & Data Cleaning Decisions</h4>
                    <ul>
                        <li><strong>Safe Grade Mapping:</strong> Standard scale 1–6 mapped directly. Modifiers like <code>+</code> add 0.5, <code>-</code> subtracts 0.25.</li>
                        <li><strong>Unknown != Zero (Slide 14):</strong> Non-numeric symbols (exemptions, absence) are mapped to <code>NaN</code>, preventing artificial distortion of averages.</li>
                        <li><strong>Date Availability:</strong> The Librus export does not contain calendar timestamps. Temporal progress was accurately analyzed using chronological grade sequence order.</li>
                    </ul>
                </div>

                <div class="report-box">
                    <h4>4. Three Evidence-Based Observations</h4>
                    <ul>
                        <li><strong>Observation 1:</strong> IT and vocational subjects show high academic achievement (e.g. Computer Science and Vocational English at 6.00; Object-Oriented Programming at 4.67).</li>
                        <li><strong>Observation 2:</strong> High variability is observed in general subjects (Polish: std 1.33, Math: std 1.10) where marks fluctuate between 2 and 5.</li>
                        <li><strong>Observation 3:</strong> The overall academic average stands high at {metrics['overall_mean']} with a median of 5.0, reflecting strong overall attainment.</li>
                    </ul>
                </div>

                <div class="report-box">
                    <h4>5. Dataset Limitations</h4>
                    <p><strong>Assessment Weighting & Calendar Dates:</strong> The export lacks assessment weights (e.g. distinguishing a 15-minute quiz from a comprehensive semester exam) and precise dates. Hence, simple arithmetic averages were computed rather than weighted averages.</p>
                </div>

                <div class="report-box">
                    <h4>6. Grade Alert System Diagnostic</h4>
                    <p>Flags like <code>REVIEW AVERAGE</code> or <code>RECENT DECLINE</code> provide targeted diagnostic prompts. For example, in <em>Chemia</em>, strong current grades (5, 5, 4) contrast sharply with a term grade of 1, triggering an immediate review flag for verification.</p>
                </div>
            </div>

            <!-- 2-3 MINUTE PRESENTATION SCRIPT (SLIDE 24 & 28) -->
            <div class="script-box">
                <h4>🎙️ 2–3 Minute Briefing Script (Presentation Guide)</h4>
                <p><strong>Speaker Notes:</strong></p>
                <p><em>"Good morning/afternoon. Today I am presenting my Personal Learning Analytics Dashboard, built from our Librus academic export using Python, pandas, and matplotlib."</em></p>
                <p><em>"<strong>The Main Pattern:</strong> Overall academic performance is very strong, with a cohort GPA of {metrics['overall_mean']} and a median of 5.0. Grade 5 is our modal grade, representing {metrics['most_frequent_pct']}% of all marks. Technical and vocational subjects such as Computer Science, Vocational English, and Databases are performing exceptionally well with averages between 5.0 and 6.0."</em></p>
                <p><em>"<strong>Key Visual Discovery:</strong> Our 2x2 dashboard immediately revealed two crucial insights. In Chart 1 and 4, we see that while technical subjects are consistent, subjects like Polish, Mathematics, and Chemistry exhibit wide spreads (std &gt; 1.0). In Chemistry, our Alert System triggered a 'RECENT DECLINE' flag because despite current grades of 5, 5, 4, a term grade of 1 was entered, bringing the subject average to 3.75."</em></p>
                <p><em>"<strong>Caution & Limitations:</strong> Viewers should be careful not to mistake statistical review flags for official student ability. Furthermore, because the Librus export did not include assessment weights or calendar dates, all grades were evaluated using unweighted means across sequence positions."</em></p>
                <p><em>"In conclusion, this project gave us actionable feedback: continue the strong momentum in programming, while dedicating focused review time to Polish and Chemistry."</em></p>
            </div>
        </section>

    </main>

    <script>
        function filterTable(inputId, tableId) {{
            const input = document.getElementById(inputId);
            const filter = input.value.toLowerCase();
            const table = document.getElementById(tableId);
            const trs = table.getElementsByTagName("tr");

            for (let i = 1; i < trs.length; i++) {{
                const text = trs[i].textContent || trs[i].innerText;
                if (text.toLowerCase().indexOf(filter) > -1) {{
                    trs[i].style.display = "";
                }} else {{
                    trs[i].style.display = "none";
                }}
            }}
        }}
    </script>
</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[REPORT] Saved standalone HTML report to: {output_html_path}")

    # Also save as index.html for easy browser opening
    with open(OUTPUT_INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[REPORT] Saved alias copy to: {OUTPUT_INDEX_HTML_PATH}")


# ==============================================================================
# 5. MAIN EXECUTION PIPELINE
# ==============================================================================
def main():
    print("=" * 70)
    print("PERSONAL LEARNING ANALYTICS DASHBOARD — LIBRUS GRADE ANALYSER")
    print("=" * 70)

    # 1. Extract all grades
    df = load_and_extract_grades(INPUT_CSV_PATH)

    # 2. Perform pandas analysis
    subject_summary, distribution_df, order_summary, alerts_df, metrics = perform_analysis(df)

    # 3. Print terminal summaries matching presentation requirements
    print("\n" + "=" * 50)
    print("=== Subject Summary (Sorted by Mean) ===")
    print("=" * 50)
    print(subject_summary.round(2).to_string())

    print("\n" + "=" * 50)
    print("=== Grade Distribution ===")
    print("=" * 50)
    print(distribution_df.to_string(index=False))

    print("\n" + "=" * 50)
    print("=== Grade Alert System ===")
    print("=" * 50)
    print(alerts_df[["subject", "count", "mean", "std", "flags"]].to_string(index=False))

    # 4. Generate 2x2 Dashboard Visualization
    build_dashboard(df, subject_summary, distribution_df, order_summary, metrics, OUTPUT_PNG_PATH)

    # 5. Generate Standalone HTML Report with all processed data
    generate_html_report(df, subject_summary, distribution_df, order_summary, alerts_df,
                         metrics, OUTPUT_PNG_PATH, OUTPUT_HTML_PATH)

    print("\n" + "=" * 70)
    print("[SUCCESS] All tasks completed:")
    print(f"  1. Extracted Tidy CSV: {OUTPUT_TIDY_CSV_PATH}")
    print(f"  2. 2x2 Dashboard PNG : {OUTPUT_PNG_PATH}")
    print(f"  3. Interactive HTML  : {OUTPUT_HTML_PATH} (and {OUTPUT_INDEX_HTML_PATH})")
    print("=" * 70)


if __name__ == "__main__":
    main()
