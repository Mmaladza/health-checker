import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

HISTORY_FILE = Path("history.json")


def load() -> list:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def append(results: list):
    history = load()
    history.extend(results)
    # keep last 10 000 entries
    HISTORY_FILE.write_text(json.dumps(history[-10_000:], indent=None))


def uptime_stats(name: str, hours: int = 24) -> dict:
    history = load()
    cutoff  = (datetime.now() - timedelta(hours=hours)).isoformat()
    relevant = [e for e in history if e.get("name") == name and e.get("checked_at", "") >= cutoff]
    if not relevant:
        return {"uptime_pct": None, "total": 0, "up": 0, "down": 0, "avg_latency_ms": None}
    up   = sum(1 for e in relevant if e["status"] == "up")
    down = len(relevant) - up
    avg_lat = round(sum(e["latency_ms"] for e in relevant) / len(relevant), 1)
    return {
        "uptime_pct": round(100 * up / len(relevant), 2),
        "total": len(relevant), "up": up, "down": down,
        "avg_latency_ms": avg_lat,
    }


def summary_table(hours: int = 24):
    history = load()
    names   = sorted({e["name"] for e in history})
    print(f"
  Uptime summary (last {hours}h)
")
    print(f"  {'Name':<28} {'Uptime':>7}  {'Avg ms':>7}  {'Checks':>7}")
    print("  " + "-" * 55)
    for name in names:
        s = uptime_stats(name, hours)
        pct = f"{s['uptime_pct']:.1f}%" if s["uptime_pct"] is not None else "N/A"
        lat = str(s["avg_latency_ms"]) if s["avg_latency_ms"] else "N/A"
        print(f"  {name:<28} {pct:>7}  {lat:>7}  {s['total']:>7}")
