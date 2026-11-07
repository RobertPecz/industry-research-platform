import httpx
import pytest

from industry_research import collect as module
from industry_research.db import connect


@pytest.mark.parametrize("status", [403, 429, 500, 404])
def test_http_failures(tmp_path, monkeypatch, status):
    real_client = httpx.Client

    def handle(request):
        return (
            httpx.Response(200, text="User-agent: *\nAllow: /")
            if request.url.path == "/robots.txt"
            else httpx.Response(status)
        )

    monkeypatch.setattr(
        module.httpx,
        "Client",
        lambda **kw: real_client(transport=httpx.MockTransport(handle), **kw),
    )
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    db = connect(str(tmp_path / "db"))
    assert module.collect(
        db,
        [{"name": "test", "status": "allowed", "urls": ["https://example.org/a"]}],
        1,
    ) == {"error": 1}
    assert db.execute("SELECT count(*) FROM documents").fetchone()[0] == 0


@pytest.mark.parametrize("policy", ["manual_review", "allowed"])
def test_denied_never_fetches_article(tmp_path, monkeypatch, policy):
    calls = []
    real_client = httpx.Client

    def handle(request):
        calls.append(request.url.path)
        return httpx.Response(200, text="User-agent: *\nDisallow: /")

    monkeypatch.setattr(
        module.httpx,
        "Client",
        lambda **kw: real_client(transport=httpx.MockTransport(handle), **kw),
    )
    db = connect(str(tmp_path / "db"))
    assert module.collect(
        db, [{"name": "test", "status": policy, "urls": ["https://example.org/a"]}], 1
    ) == {"blocked": 1}
    assert "/a" not in calls


def test_empty_and_bad_pdf():
    assert module.extract(b"<html><script>bad</script></html>", "text/html")[1] == ""
    with pytest.raises(Exception):
        module.extract(b"broken", "application/pdf")


def test_rate_limit_stops_host(tmp_path, monkeypatch):
    calls = []
    real_client = httpx.Client

    def handle(request):
        calls.append(request.url.path)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(429)

    monkeypatch.setattr(
        module.httpx,
        "Client",
        lambda **kw: real_client(transport=httpx.MockTransport(handle), **kw),
    )
    db = connect(str(tmp_path / "db"))
    counts = module.collect(
        db,
        [
            {
                "name": "test",
                "status": "allowed",
                "urls": ["https://example.org/a", "https://example.org/b"],
            }
        ],
        2,
        sleep=lambda _: None,
    )
    assert counts == {"error": 1, "blocked": 1}
    assert calls == ["/robots.txt", "/a"]
