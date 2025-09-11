import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import patch, MagicMock
import urllib.error
from checker import check_url

def test_check_url_success():
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__  = MagicMock(return_value=False)
    mock_resp.status    = 200
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = check_url("https://example.com")
    assert r["status"] == "up"
    assert r["code"]   == 200

def test_check_url_http_error():
    with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("", 503, "Service Unavailable", {}, None)):
        r = check_url("https://example.com")
    assert r["status"] == "down"
    assert r["code"]   == 503

def test_check_url_timeout():
    with patch("urllib.request.urlopen", side_effect=Exception("timed out")):
        r = check_url("https://example.com")
    assert r["status"] == "down"
    assert "timed out" in r["error"]
