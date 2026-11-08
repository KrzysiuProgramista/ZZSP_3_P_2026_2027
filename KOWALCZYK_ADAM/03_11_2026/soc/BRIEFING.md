# SOC briefing - September 2026 (720 synthetic events)

Numbers come from `python starter.py` (tables, `*.csv`) and `python investigation.py`.

**Findings**
1. DDoS is the riskiest attack type in the dataset: 20.0% of its 95 events led to compromise (the next is SQL Injection at 13.5%), and only 49.5% were blocked (others 59-70%).
2. Brute Force is the most frequent attack type (170 events, 23.6%) and has the slowest response besides Port Scan (36.9 min avg vs 27.2 min for Malware), but only 6.5% compromised.
3. Web Server receives the most incidents (179) and the most compromises (30, 16.8% of its events); VPN Gateway has 117 events but only 4 compromises.

**Investigate further:** Web Server - highest volume and highest compromise count; check which attack types hit it (DDoS and SQL Injection are likely candidates).

**Recommendation:** add stronger DDoS and Web Server protection (rate limiting / WAF rules) and set a response-time target for Brute Force and Port Scan alerts.

**Limitation:** the data is synthetic and covers one month, with small groups (e.g. File Server has 21 events), so differences of a few percentage points are not reliable. Country labels are metadata, not attribution.
