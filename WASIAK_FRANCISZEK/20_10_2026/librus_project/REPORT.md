# Librus Intelligence report

The application reads a locally cleaned CSV and uses Pandas for below-grade, subject, inclusive date-range and multiple exact-match queries. It groups records by subject to count rows and calculate mean base grades. All demonstration records are fictional.

The base-grade mean is not an official term grade: plus/minus modifiers are removed, weights are not supplied, and no school or teacher grading policy is implemented. Invalid dates and unrecognized grades become missing values. Missing numeric grades are excluded from the mean but included in record counts.

The PDF inspector processes files locally and exports candidate tables, not a guaranteed clean CSV. The user must verify alignment and create grades.csv locally. No code uploads grade data. Keep PDFs, grades.csv and private_work private. Submit code and this nonpersonal report only.
