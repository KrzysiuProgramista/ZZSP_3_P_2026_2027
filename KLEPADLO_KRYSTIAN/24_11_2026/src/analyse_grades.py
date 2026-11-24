from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

GRADE_MAP = {
    "1": 1.0,
    "2": 2.0,
    "3": 3.0,
    "4": 4.0,
    "5": 5.0,
    "6": 6.0,
}


def load_and_clean(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype={"grade_raw": "string"})
    df["subject"] = df["subject"].astype("string").str.strip()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
    else:
        df["date"] = pd.NaT
    df["grade_value"] = df["grade_raw"].str.strip().map(GRADE_MAP)
    return df


def summarise_subjects(
    df: pd.DataFrame, review_threshold: float = 3.0, std_threshold: float = 1.5
) -> pd.DataFrame:
    numeric = df.dropna(subset=["grade_value"])
    summary = (
        numeric.groupby("subject")["grade_value"]
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

    def assign_flag(row):
        if row["grade_count"] < 3:
            return "INSUFFICIENT DATA"
        flags = []
        if row["average"] < review_threshold:
            flags.append("REVIEW AVERAGE")
        if pd.notna(row["std"]) and row["std"] >= std_threshold:
            flags.append("HIGH VARIABILITY")
        return ", ".join(flags) if flags else "NO FLAG"

    summary["flag"] = summary.apply(assign_flag, axis=1)
    return summary


def make_dashboard(df: pd.DataFrame, summary: pd.DataFrame, output_path: Path) -> None:
    numeric = df.dropna(subset=["grade_value"])
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    ax1 = axes[0, 0]
    s_sorted = summary.sort_values("average", ascending=True)
    y_labels = [
        f"{subj} (n={int(cnt)})"
        for subj, cnt in
        zip(s_sorted.index, s_sorted["grade_count"])
    ]
    ax1.barh(y_labels, s_sorted["average"], color="#2B6CB0", edgecolor="#1A365D", linewidth=0.5)
    ax1.set_xlim(0, 6.5)
    ax1.set_title("Average grade varies across subjects")
    ax1.set_xlabel("Average grade (1–6 scale)")
    ax1.set_ylabel("Subject (numeric grade count)")
    ax1.tick_params(axis="y", labelsize=8)

    ax2 = axes[0, 1]
    grade_order = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    counts = numeric["grade_value"].value_counts().reindex(grade_order, fill_value=0)
    ax2.bar(
        [str(int(g)) for g in counts.index],
        counts.values,
        color="#4A5568",
        edgecolor="black",
        linewidth=0.6,
    )
    ax2.set_ylim(0, counts.max() + 2)
    ax2.set_title("Distribution of numeric grades")
    ax2.set_xlabel("Grade (1–6 scale)")
    ax2.set_ylabel("Number of records")
    for idx, val in enumerate(counts.values):
        ax2.text(idx, val + 0.3, str(int(val)), ha="center", va="bottom", fontsize=9)
        ax3 = axes[1, 0]
    dated = numeric.dropna(subset=["date"])
    if len(dated) >= 3 and dated["date"].dt.to_period("M").nunique() >= 2:
        monthly = dated.set_index("date").sort_index().resample("ME")["grade_value"].mean()
        monthly.plot(ax=ax3, marker="o", color="#2B6CB0", label="Monthly mean")
        if len(monthly) >= 3:
            monthly.rolling(3, min_periods=1).mean().plot(
                ax=ax3, linestyle="--", color="#718096", label="3-period moving average"
            )
        ax3.set_title("Monthly average grade over time")
        ax3.set_xlabel("Month")
        ax3.set_ylabel("Average grade (1–6 scale)")
        ax3.set_ylim(0, 6.5)
        ax3.legend()
    else:
        counts_subj = summary["grade_count"].sort_values(ascending=True)
        ax3.barh(counts_subj.index, counts_subj.values, color="#718096", edgecolor="black", linewidth=0.5)
        ax3.axvline(3, color="black", linestyle="--", linewidth=1.2, label="Min. 3 grades threshold")
        ax3.set_title("Dates unavailable: numeric grade count per subject")
        ax3.set_xlabel("Number of numeric grades")
        ax3.set_ylabel("Subject")
        ax3.tick_params(axis="y", labelsize=8)
        ax3.legend()

    ax4 = axes[1, 1]
    eligible = summary[summary["grade_count"] >= 3].sort_values("average", ascending=False).index.tolist()
    plot_data = [numeric.loc[numeric["subject"] == subj, "grade_value"].values for subj in eligible]
    ax4.boxplot(
        plot_data,
        tick_labels=eligible,
        patch_artist=True,
        boxprops=dict(facecolor="#CBD5E0", color="black"),
        medianprops=dict(color="black", linewidth=2),
    )
    ax4.set_ylim(0.5, 6.5)
    ax4.set_title("Grade spread for subjects with at least 3 numeric grades")
    ax4.set_xlabel("Subject")
    ax4.set_ylabel("Grade (1–6 scale)")
    ax4.tick_params(axis="x", rotation=35, labelsize=8)
    for label in ax4.get_xticklabels():
        label.set_ha("right")

    fig.suptitle("Personal Learning Analytics Dashboard", fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    df = load_and_clean(base_dir / "work" / "grades_raw.csv")
    summary = summarise_subjects(df)
    print(summary.to_string())
    make_dashboard(df, summary, base_dir / "output" / "my_academic_dashboard.png")