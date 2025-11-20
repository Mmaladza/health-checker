import json, time, argparse, urllib.request, urllib.error, sys
from datetime import datetime
from pathlib import Path
from history import append as hist_append, summary_table
from alerting import AlertManager, WebhookAlerter


def check_url(url: str, timeout: float = 5.0) -> dict:
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "health-checker/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"status": "up",   "code": resp.status,
                    "latency_ms": round((time.monotonic()-start)*1000, 1)}
    except urllib.error.HTTPError as e:
        return {"status": "down", "code": e.code,
                "latency_ms": round((time.monotonic()-start)*1000, 1), "error": str(e)}
    except Exception as e:
        return {"status": "down", "code": None,
                "latency_ms": round((time.monotonic()-start)*1000, 1), "error": str(e)}


def run_checks(config: dict, alert_mgr=None) -> list:
    results = []
    for check in config.get("checks", []):
        result = check_url(check["url"], check.get("timeout", 5))
        result.update({"name": check["name"], "url": check["url"],
                       "checked_at": datetime.now().isoformat()})
        icon = "UP" if result["status"] == "up" else "DOWN"
        lat  = result["latency_ms"]
        print(f"  [{icon:4s}] {check['name']:28s} {lat:6.1f}ms  HTTP {result.get('code','?')}")
        if alert_mgr:
            alert_mgr.process(result)
        results.append(result)
    return results


def main():
    p = argparse.ArgumentParser(description="HTTP endpoint health checker")
    p.add_argument("--config", "-c", default="checks.json")
    p.add_argument("--once",  action="store_true", help="Run once then exit")
    p.add_argument("--stats", action="store_true", help="Show uptime stats")
    p.add_argument("--webhook", help="Slack/Discord webhook URL for alerts")
    p.add_argument("--interval", type=int, default=60, help="Check interval seconds")
    args = p.parse_args()

    if args.stats:
        summary_table(); return

    config    = json.loads(Path(args.config).read_text())
    alerters  = [WebhookAlerter(args.webhook)] if args.webhook else []
    alert_mgr = AlertManager(alerters)

    if args.once:
        print(f"
Running checks — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
")
        results = run_checks(config, alert_mgr)
        hist_append(results)
        up   = sum(1 for r in results if r["status"] == "up")
        down = len(results) - up
        print(f"
  {up} up  {down} down")
        sys.exit(0 if down == 0 else 1)

    print(f"Monitoring {len(config['checks'])} endpoint(s) every {args.interval}s. Ctrl+C to stop.
")
    try:
        while True:
            print(f"
-- {datetime.now().strftime('%H:%M:%S')} --")
            results = run_checks(config, alert_mgr)
            hist_append(results)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("
Stopped.")


if __name__ == "__main__":
    main()
