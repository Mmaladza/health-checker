import json, urllib.request, urllib.error
from dataclasses import dataclass, asdict
from typing import Callable, List, Optional


@dataclass
class Alert:
    name:    str
    url:     str
    status:  str
    code:    Optional[int]
    error:   Optional[str]
    latency: float


class WebhookAlerter:
    """Send alerts to a Slack/Discord/custom webhook."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, alert: Alert) -> bool:
        icon    = ":red_circle:" if alert.status == "down" else ":green_circle:"
        payload = {
            "text": f"{icon} *{alert.name}* is {alert.status.upper()}",
            "attachments": [{
                "color": "danger" if alert.status == "down" else "good",
                "fields": [
                    {"title": "URL",     "value": alert.url, "short": True},
                    {"title": "Status",  "value": str(alert.code or alert.error), "short": True},
                    {"title": "Latency", "value": f"{alert.latency}ms", "short": True},
                ]
            }]
        }
        try:
            data = json.dumps(payload).encode()
            req  = urllib.request.Request(self.webhook_url, data=data,
                                          headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False


class AlertManager:
    """Tracks state changes and fires alerts only when status changes."""

    def __init__(self, alerters: List):
        self._state:    dict = {}
        self.alerters        = alerters

    def process(self, result: dict) -> bool:
        name  = result["name"]
        prev  = self._state.get(name)
        curr  = result["status"]
        self._state[name] = curr
        if prev is None or prev == curr:
            return False
        alert = Alert(name=name, url=result["url"], status=curr,
                      code=result.get("code"), error=result.get("error"),
                      latency=result.get("latency_ms", 0))
        for alerter in self.alerters:
            alerter.send(alert)
        return True
