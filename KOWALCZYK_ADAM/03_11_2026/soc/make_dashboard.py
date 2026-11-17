"""Build dashboard.html from the SOC data (run: python make_dashboard.py)."""
from pathlib import Path
import pandas as pd
from starter import load_data, soc_dashboard

HTML_FILE = Path(__file__).with_name("output") / "dashboard.html"


def _bars(labels, values) -> str:
    """Pure-CSS horizontal bar chart."""
    top = max(values, default=0) or 1
    rows = "".join(
        f'<div class="row"><span>{l}</span><div class="bar" style="width:{v / top * 100:.1f}%"></div>'
        f"<b>{v}</b></div>"
        for l, v in zip(labels, values)
    )
    return f'<div class="chart">{rows}</div>'


def build_html(df: pd.DataFrame, dash: dict[str, pd.DataFrame]) -> str:
    """Render the dashboard as one self-contained HTML string."""
    n = len(df)
    kpis = [
        ("Incidents", n),
        ("Blocked", f"{df['blocked'].mean() * 100:.1f}%" if n else "-"),
        ("Compromised", int(df["compromised"].sum())),
        ("Avg response (min)", f"{df['response_time_min'].mean():.1f}" if n else "-"),
        ("Unique source IPs", df["source_ip"].nunique()),
    ]
    cards = "".join(f'<div class="card"><small>{k}</small><h2>{v}</h2></div>' for k, v in kpis)
    a, h, t = dash["by_attack"], dash["by_hour"], dash["daily_trend"]
    charts = (
        "<h3>Incidents by attack type</h3>" + _bars(a["attack_type"], a["incidents"])
        + "<h3>Incidents by hour</h3>" + _bars(h["hour"], h["incidents"])
        + "<h3>Daily incidents</h3>" + _bars(t["event_date"].astype(str), t["incidents"])
    )
    tables = "".join(
        f"<h3>{name}</h3>{tbl.to_html(index=False, classes='t')}" for name, tbl in dash.items()
    )
    css = """body{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#f5f6f8;color:#1b1f24}
main{max-width:1000px;margin:auto}.cards{display:flex;flex-wrap:wrap;gap:12px}
.card{flex:1 1 150px;background:#fff;padding:12px 16px;border-radius:8px}.card h2{margin:4px 0 0}
.chart .row{display:flex;align-items:center;gap:8px;margin:2px 0;font-size:13px}
.chart span{width:120px;flex:none}.bar{background:#2b6cb0;height:14px;border-radius:3px}
.t{border-collapse:collapse;background:#fff;font-size:13px;width:100%}
.t th,.t td{padding:4px 8px;border-bottom:1px solid #e3e6ea;text-align:right}
.t th:first-child,.t td:first-child{text-align:left}
@media(prefers-color-scheme:dark){body{background:#14171a;color:#e6e8ea}.card,.t{background:#1e2227}.t th,.t td{border-color:#2d333a}}"""
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>SOC Dashboard</title><style>{css}</style></head><body><main>"
        f"<h1>SOC Dashboard - September 2026</h1><p>Synthetic data. Country labels are "
        f'metadata, not attribution.</p><div class="cards">{cards}</div>{charts}{tables}'
        "</main></body></html>"
    )


if __name__ == "__main__":
    events = load_data()
    HTML_FILE.parent.mkdir(exist_ok=True)
    HTML_FILE.write_text(build_html(events, soc_dashboard(events)), encoding="utf-8")
    print(f"Wrote {HTML_FILE.name}")
