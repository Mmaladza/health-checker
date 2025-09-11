from alerting import AlertManager, Alert

class FakeAlerter:
    def __init__(self): self.sent = []
    def send(self, alert): self.sent.append(alert)

def make_result(name, status):
    return {"name": name, "url": "https://x.com", "status": status,
            "code": 200 if status=="up" else 503, "error": None, "latency_ms": 12}

def test_fires_on_status_change():
    alerter = FakeAlerter()
    mgr     = AlertManager([alerter])
    mgr.process(make_result("API", "up"))      # first — no alert
    assert len(alerter.sent) == 0
    mgr.process(make_result("API", "down"))    # change: up -> down
    assert len(alerter.sent) == 1
    mgr.process(make_result("API", "down"))    # same — no alert
    assert len(alerter.sent) == 1
    mgr.process(make_result("API", "up"))      # recovery alert
    assert len(alerter.sent) == 2
