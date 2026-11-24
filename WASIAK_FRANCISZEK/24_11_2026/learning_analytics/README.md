# Personal Learning Analytics

## Method
The Librus converter extracts the grade table. Pandas reshapes current grades to one row per numeric grade. Only the later grade in each correction group is counted. Plain grades 1–6 are unweighted. Status marks and plus/minus variants without an agreed numeric conversion are excluded, not counted as zero. Regular grade dates are unavailable, so the dashboard shows counts by subject instead of inventing a time trend.

## Three findings
1. Highest observed subject mean: 6.00 — Informatyka (n=3).
2. Lowest observed subject mean: 2.00 — Projektowanie oprogramowania (n=1), Programowanie aplikacji internetowych (n=3).
3. Most frequent grade(s): 5, with 22 occurrences each out of 58 numeric grades.

## Limitation
Subject means with few grades can change quickly; these are not official averages.
