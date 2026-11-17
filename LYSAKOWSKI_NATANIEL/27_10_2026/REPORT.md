# Data Rescue: quality report, management answers, verdict
Source: `dirty_sales.csv` (120 rows, 8 columns). Everything below is produced by `python analysis.py`.

## 1. Damage found (Mission 1)
| # | Issue | Where |
|---|-------|-------|
| 1 | Inconsistent labels (case/whitespace) | region (`north`, `NORTH`, ` north `, `south`), category (`electronics`, `Accessories `), product (`WIRELESS MOUSE`, `desk LAMP`, ` laptop pro 14 `) |
| 2 | Missing prices: 4 blank + 2 written as `unknown` (5% of rows) | ORD-0004, 0008, 0018, 0045, 0052, 0089 |
| 3 | Mixed price formats | `$1,299.99` (x2), `€ 349,00` |
| 4 | Bad quantities: 2 blank, `five`, `0`, `-3` | ORD-0013, 0073, 0032, 0022, 0094 |
| 5 | Impossible / suspicious dates | `31.02.2026` (x2), `05.12.2027` (after the 27.10.2026 report date) |
| 6 | 1 exact duplicate row, 1 repeated id with different date | ORD-0026 / ORD-0040 |
| 7 | Prices that don't fit the product | USB-C Hub at 1,299.99 and 349.00 (normal ≈ 125-143); `WIRELESS MOUSE` at 331.55 (normal ≈ 40) |

## 2. Cleaning decisions (Mission 2)
| Decision | Why |
|---|---|
| Missing/invalid price, quantity, date stay **NaN/NA**, never 0 | Zero looks like real data and silently lowers totals. |
| Rows with bad values are **kept and flagged**, not dropped | Dropping hides revenue; a human should decide. |
| `five` → 5; `0`, `-3`, blank → `<NA>` | A word is unambiguous. Zero = nothing sold; -3 could be a return or a sign typo, and guessing would invent revenue. |
| `$`/`€` symbols stripped, no currency conversion, rows flagged | The file never states a currency, so 349,00 EUR cannot be converted honestly. |
| Dates parsed with explicit `%d.%m.%Y` | Prevents day/month guessing; `31.02` → NaT. |
| Exact duplicate dropped | Pure double export, no information lost. |
| Repeated id, different content (ORD-0040: 09.10 vs 27.10) → **keep newest date, flag `id_conflict`** | Newest is the usual "latest correction" rule, but it is an assumption, so it's flagged. |

Pipeline report: 120 rows in → **118 out** (1 exact duplicate + 1 id conflict removed). Remaining missing: price 6, quantity 4, date 2. 10 orders have no total.

## 3. Answers for management (Mission 4)
1. **Highest category: Electronics, 498,177** (Furniture 125,258; Accessories 25,018; Stationery 5,845).
2. **Top 5 orders:** ORD-0086 (120,978; 20 laptops), ORD-0044 (65,988), ORD-0099 (41,792), ORD-0077 (32,500; flagged), ORD-0036 (30,245).
3. **Most orders: East and South tie at 32**, North 31, West 23.
4. **10 orders lack a usable price or quantity** (6 price only, 4 quantity only, 0 both).
5. **Total sales: 654,298.12** from 108 orders. The 10 orders without a total are **excluded, not zero-filled**, so this is a lower bound. Those 6 missing-price orders alone would be worth roughly 45,800 at median product prices (indicative only, not in the headline). Counting only orders with *no* review flag, the total is 555,384.55.
6. **20 of 118 orders need manual review** (full list with reasons in `review_queue.csv`): 6 missing price, 4 invalid quantity, 2 invalid date, 1 future date, 3 suspicious quantity (≥25 units), 3 price outliers, 1 id conflict (some orders have several reasons).

## 4. Verdict
**Can management trust this dataset? Partly.** The structure is now clean and repeatable, and 98 of 118 orders (83%) pass every check. But the headline total is not final: 8.5% of orders have no value, and about 87,500 of the 654,298 total sits on orders flagged for a suspicious quantity or price (ORD-0069, 0077, 0120, 0024, 0058, 0067).

**Needs human review before the report goes out:**
- Prices for the 6 missing-price orders, and quantities for the 4 invalid ones (0, -3, blank): were -3/0 returns or typos?
- The 3 orders of 25 units (two monitors, one office chair) and the mispriced USB-C Hub / mouse rows.
- The `$`/`€` prices: confirm the currency.
- ORD-0040: confirm 27.10.2026 is the correct date; fix ORD-0014, ORD-0062 (31.02) and ORD-0091 (year 2027).
- ORD-0086 (20 laptops, 18% of all sales) is **not** flagged by the rules but deserves a sanity check.

Assumptions you may want to change are in the config block at the top of `analysis.py` (`SUSPICIOUS_QTY`, `PRICE_OUTLIER_RATIO`, `REPORT_DATE`).
