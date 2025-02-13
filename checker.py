import json, time, argparse, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

CONFIG_EXAMPLE = {
    "checks": [
        {"name": "My API",    "url": "https://example.com/health", "interval": 60, "timeout": 5},
        {"name": "Google",    "url": "https://www.google.com",      "interval": 120},
    ]
}


def check_url(url: str, timeout: float = 5.0) -> dict:
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "health-checker/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = round((time.monotonic() - start) * 1000, 1)
            return {"status": "up", "code": resp.status, "latency_ms": latency}
    except urllib.error.HTTPError as e:
        latency = round((time.monotonic() - start) * 1000, 1)
        return {"status": "down", "code": e.code, "latency_ms": latency, "error": str(e)}
    except Exception as e:
        latency = round((time.monotonic() - start) * 1000, 1)
        return {"status": "down", "code": None, "latency_ms": latency, "error": str(e)}


def run_checks(config: dict) -> list:
    results = []
    for check in config.get("checks", []):
        result = check_url(check["url"], check.get("timeout", 5))
        result.update({"name": check["name"], "url": check["url"],
                       "checked_at": datetime.now().isoformat()})
        icon = "OK" if result["status"] == "up" else "!!"
        print(f"  [{icon}] {check['name']:25s} {result['status']:5s}  {result['latency_ms']}ms")
        results.append(result)
    return results


def load_config(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    if path.endswith(".json"):
        return json.loads(p.read_text())
    # minimal YAML-ish parser for simple list configs
    return json.loads(p.read_text())


def main():
    p = argparse.ArgumentParser(description="HTTP health checker")
    p.add_argument("--config", "-c", default="checks.json")
    p.add_argument("--once", action="store_true", help="Run once and exit")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    config = load_config(args.config)
    print(f"
Health check — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
")
    results = run_checks(config)
    if args.json:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
