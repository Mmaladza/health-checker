# health-checker

Monitor HTTP endpoints for uptime, response time and status changes — with alerting and history.

## Usage

```bash
# Run once
python checker.py --config checks.json --once

# Continuous monitoring (every 60s)
python checker.py --config checks.json --interval 60

# With Slack/Discord alerts on status change
python checker.py --config checks.json --webhook https://hooks.slack.com/...

# Uptime stats
python checker.py --stats
```

## Config (`checks.json`)

```json
{
  "checks": [
    {"name": "My API",   "url": "https://api.example.com/health", "timeout": 5},
    {"name": "Frontend", "url": "https://example.com",             "timeout": 10}
  ]
}
```

## Features
- HTTP status and latency tracking
- State-change alerting (webhook: Slack / Discord / custom)
- Uptime history (`history.json`, last 10 000 results)
- Uptime % summary per endpoint
- Exit code 1 if any endpoint is down (CI-friendly)
- GitHub Actions workflow included

## Tests

```bash
pip install pytest
pytest tests/ -v
```
