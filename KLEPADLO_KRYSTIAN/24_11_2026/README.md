# Personal Learning Analytics Dashboard

## Privacy & Data Handling
The original Librus PDF export (`private_input/`) and raw CSV (`work/grades_raw.csv`) are excluded via `.gitignore` and kept strictly local. Only reusable analysis code and documentation are published in this repository.

## Data Assumptions & Cleaning
- **Source structure**: One row per grade record (`subject`, `grade_raw`, `date`, `category`, `description`, `weight`).
- **Grade mapping**: Only integer grades `1`–`6` are mapped to numeric values (`1.0`–`6.0`). Non-numeric symbols (`+`, `-`, `bz`, `np`, `T`) are preserved in `grade_raw` and excluded (`NaN`) from numeric calculations — never converted to `0`.
- **Missing dates**: The Librus PDF export does not include dates for regular grades. Dates were not invented; instead, Panel 3 automatically falls back to showing the number of numeric grades per subject (sample size) with a 3-grade reliability threshold.
- **Grade Alert System**: Subjects with `< 3` numeric grades are flagged `INSUFFICIENT DATA`; subjects with `>= 3` grades are flagged `REVIEW AVERAGE` if mean `< 3.0` and `HIGH VARIABILITY` if standard deviation `>= 1.5`.

## Key Findings (from local run)
1. **Overall distribution**: Out of 76 total records, 53 are numeric grades (mean `3.60`, median `4.00`) and 23 are non-numeric symbols. Grade `5` is the most frequent numeric grade (16 occurrences).
2. **Sample size limitation**: 10 out of 18 graded subjects have fewer than 3 numeric grades (`INSUFFICIENT DATA`), so their averages are not directly comparable to subjects with larger samples (e.g., 6–8 grades).
3. **Variability & review flags**: Among subjects with at least 3 numeric grades, the largest spread occurs in subjects with both top (`5`) and bottom (`1`) marks (std up to `2.31`), while four subjects fall below the `3.0` review threshold.

## Main Limitation
The dataset lacks grade dates and weights, preventing time-series trend analysis and weighted average calculations.
## How to Run Locally
```bash
python -m pip install pandas matplotlib
python src/analyse_grades.py