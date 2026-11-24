from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)

df = pd.read_csv("sales-selected-columns.csv")
quantity = df["Units Sold"]
mean = quantity.mean()
median = quantity.median()

# 1 + 2. Histogram with 10 and 50 bins, with mean and median lines
fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

for ax, bins in zip(axes, [10, 50]):
    ax.hist(quantity, bins=bins, edgecolor="white")
    ax.axvline(mean, color="red", linestyle="--", label=f"Mean = {mean:,.0f}")
    ax.axvline(median, color="black", linestyle="-", label=f"Median = {median:,.0f}")
    ax.set_title(f"Order quantity, {bins} bins")
    ax.set_xlabel("Units sold per order")
    ax.set_ylabel("Number of orders")
    ax.legend()

fig.suptitle("Distribution of order quantity")
fig.tight_layout()
fig.savefig(CHARTS_DIR / "ex2_1_quantity_histograms.png", dpi=150)
plt.close(fig)

# Comparison of 10 vs 50 bins:
# - With 10 bins every bar holds about 10 orders, so the shape is easy to read:
#   the quantities are spread fairly evenly from ~100 to ~10,000 (close to a
#   uniform distribution), with no clear peak.
# - With 50 bins each bar holds only 0-5 orders. With just 100 orders the chart
#   becomes noisy: the gaps and spikes are random, not a real pattern.
#   More bins show more detail, but only when there is enough data to fill them.

# 3. Box plot of the same data
fig, ax = plt.subplots(figsize=(8, 5))
ax.boxplot(quantity, orientation="horizontal", tick_labels=["Units sold"])
ax.axvline(mean, color="red", linestyle="--", label=f"Mean = {mean:,.0f}")
ax.set_title("Order quantity (box plot)")
ax.set_xlabel("Units sold per order")
ax.legend()
fig.tight_layout()
fig.savefig(CHARTS_DIR / "ex2_3_quantity_boxplot.png", dpi=150)
plt.close(fig)

# 4. What each chart tells you
#
# What the box plot shows that the histogram does not:
# - Exact summary numbers at a glance: the median (~5,380), the quartiles
#   (Q1 ~2,840, Q3 ~7,370), so the middle 50% of orders sits between them.
# - Outliers are marked as separate points. Here there are none, because the
#   whiskers reach the min (124) and max (9,925).
# - It is compact, so many groups can be compared side by side
#   (like the per-category box plot in ex1).
#
# What the histogram shows that the box plot does not:
# - The actual shape of the distribution. The histogram shows the orders are
#   spread almost evenly (flat, uniform-like). A box plot of a bell-shaped
#   distribution could look almost the same, so the box plot hides this.
# - Whether there are several peaks (bimodal data) or gaps, and how many
#   orders fall in each range.
# - The histogram depends on the bin count, the box plot does not.
#
# Mean (~5,130) is slightly below the median (~5,380): a few small orders pull
# the mean down a little, but the difference is small, so the data is close to
# symmetric.
