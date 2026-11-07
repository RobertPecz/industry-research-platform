import json

import httpx
import pytest

from industry_research.db import connect, store
from industry_research.gemini import SDKClient, analyze, load_config, validate_result
from industry_research.maintenance import review

TEXT = "A késedelmes fizetés nehezíti a munkát."
ITEM = {
    "summary": "Késedelmes fizetés",
    "workflow": "Elszámolás",
    "actor": "contractor",
    "category": "finance",
    "evidence_excerpt": TEXT,
    "evidence_type": "first_hand",
    "confidence": "high",
    "requires_review": True,
}


class FakeClient:
    def __init__(self, outcomes=None, model_error=None):
        self.outcomes = list(outcomes or [])
        self.model_error = model_error
        self.calls = 0
        self.closed = False

    def check_model(self, model):
        if self.model_error:
            raise self.model_error

    def generate(self, model, text):
        self.calls += 1
        value = (
            self.outcomes.pop(0) if self.outcomes else json.dumps({"problems": [ITEM]})
        )
        if isinstance(value, Exception):
            raise value
        return value, {"input_tokens": 12, "output_tokens": 20, "total_tokens": 32}

    def close(self):
        self.closed = True


class APIError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__("SECRET_CONTENT_MUST_NOT_BE_LOGGED")


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "SECRET_KEY_MUST_NOT_BE_LOGGED")
    db = connect(str(tmp_path / "db"))
    store(db, "https://example.org", "fixture", "Teszt", TEXT)
    with db:
        db.execute("INSERT INTO source_audits(name,status) VALUES('fixture','allowed')")
    yield db, load_config()
    db.close()


def run(db, config, client, **kwargs):
    return analyze(
        db,
        config,
        [1],
        allow_external=True,
        confirm_free_tier=True,
        confirm_public_data=True,
        client_factory=lambda *args: client,
        sleep=lambda _: None,
        **kwargs,
    )


def test_default_never_constructs_client(setup):
    db, config = setup

    def forbidden(*args):
        pytest.fail("No client may be constructed")

    for flags in (
        {},
        {"allow_external": True},
        {"allow_external": True, "confirm_free_tier": True},
    ):
        with pytest.raises(ValueError):
            analyze(db, config, [1], client_factory=forbidden, **flags)


def test_success_cache_and_manual_label(setup):
    db, config = setup
    client = FakeClient()
    result = run(db, config, client)
    assert result["requests"] == 2 and result["success"] == 1
    assert client.closed
    row = db.execute("SELECT * FROM evidence").fetchone()
    assert row["kind"] == "unknown" and row["actor"] == "unknown"
    review(db, row["id"], "verified", "Kézzel ellenőrizve", "kézi téma")
    second = FakeClient()
    assert run(db, config, second)["cached"] == 1
    assert second.calls == 0
    assert db.execute("SELECT topic FROM evidence").fetchone()[0] == "kézi téma"
    assert db.execute("SELECT SUM(total_tokens) FROM ai_attempts").fetchone()[0] == 32


@pytest.mark.parametrize(
    "code,status,calls",
    [
        (503, "deferred_service_unavailable", 3),
        (429, "deferred_quota", 1),
        (400, "configuration_error", 1),
        (404, "configuration_error", 1),
        (401, "configuration_error", 1),
    ],
)
def test_error_policy_and_secret_redaction(setup, code, status, calls):
    db, config = setup
    client = FakeClient([APIError(code)] * 3)
    result = run(db, config, client)
    assert result["status"] == status and client.calls == calls
    assert db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0] == 0
    rows = [dict(r) for r in db.execute("SELECT * FROM ai_attempts")]
    assert "SECRET" not in json.dumps(rows)
    assert client.closed


@pytest.mark.parametrize(
    "payload",
    [
        "{",
        "{}",
        json.dumps({"problems": [dict(ITEM, evidence_excerpt="Kitalált idézet")]}),
        json.dumps({"problems": [dict(ITEM, requires_review=False)]}),
        json.dumps({"problems": [{"summary": "Hiányos"}]}),
    ],
)
def test_invalid_output_keeps_usage_but_no_evidence(setup, payload):
    db, config = setup
    assert run(db, config, FakeClient([payload]))["status"] == "invalid"
    assert db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0] == 0
    assert db.execute("SELECT SUM(total_tokens) FROM ai_attempts").fetchone()[0] == 32


def test_timeout_no_blind_retry_and_resume(setup):
    db, config = setup
    client = FakeClient([httpx.ReadTimeout("secret")])
    assert run(db, config, client)["status"] == "deferred_network"
    assert client.calls == 1
    assert run(db, config, FakeClient())["success"] == 1


def test_request_budget_includes_model_check(setup):
    db, config = setup
    config["max_requests"] = 2
    client = FakeClient([APIError(503)] * 3)
    result = run(db, config, client)
    assert result["requests"] == 2 and client.calls == 1


def test_reject_research_note_before_network(setup):
    db, config = setup
    db.execute("UPDATE documents SET storage_mode='research_note'")
    client = FakeClient()
    with pytest.raises(ValueError):
        run(db, config, client)
    assert client.calls == 0


def test_model_check_failure(setup):
    db, config = setup
    result = run(db, config, FakeClient(model_error=APIError(404)))
    assert result["requests"] == 1 and result["status"] == "configuration_error"


def test_negative_and_multiple_problems():
    assert validate_result({"problems": []}, "Nincs panasz.") == []
    assert (
        len(
            validate_result(
                {"problems": [ITEM, dict(ITEM, summary="Másik probléma")]}, TEXT
            )
        )
        == 2
    )


def test_sdk_wire_contract_offline(monkeypatch):
    pytest.importorskip("google.genai")
    from google import genai
    from google.genai import types

    calls = []

    def handler(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "name": "models/gemini-test",
                    "supportedGenerationMethods": ["generateContent"],
                },
            )
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": '{"problems":[]}'}],
                            "role": "model",
                        },
                        "finishReason": "STOP",
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 3,
                    "candidatesTokenCount": 4,
                    "totalTokenCount": 7,
                },
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as transport:
        actual = genai.Client(
            api_key="test-key",
            vertexai=False,
            enterprise=False,
            http_options=types.HttpOptions(
                httpx_client=transport, retry_options=types.HttpRetryOptions(attempts=1)
            ),
        )
        monkeypatch.setattr(genai, "Client", lambda **kwargs: actual)
        client = SDKClient("test-key", 30)
        client.check_model("gemini-test")
        raw, usage = client.generate("gemini-test", "Teszt szöveg")
        assert json.loads(raw) == {"problems": []}
        assert usage["total_tokens"] == 7
        assert len(calls) == 2
        body = json.loads(calls[1].content)
        assert body["generationConfig"]["responseMimeType"] == "application/json"
        assert body["contents"][0]["parts"][0]["text"] == "Teszt szöveg"
        client.close()


def test_missing_key_is_offline(setup, monkeypatch):
    db, config = setup
    monkeypatch.delenv("GEMINI_API_KEY")
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        run(db, config, FakeClient())


def test_reject_unapproved_source_and_oversize(setup):
    db, config = setup
    db.execute("UPDATE source_audits SET status='metadata_only'")
    with pytest.raises(ValueError, match="allowed"):
        run(db, config, FakeClient())
    db.execute("UPDATE source_audits SET status='allowed'")
    config["max_document_chars"] = 5
    with pytest.raises(ValueError, match="hosszú"):
        run(db, config, FakeClient())


def test_cached_chunks_resume_after_failure(setup):
    db, config = setup
    db.execute("UPDATE versions SET text=?", ("a" * 1000,))
    config["chunk_chars"] = 500
    client = FakeClient(['{"problems":[]}', APIError(429)])
    result = run(db, config, client)
    assert result["success"] == 1 and result["status"] == "deferred_quota"
    again = FakeClient(['{"problems":[]}'])
    result = run(db, config, again)
    assert result["cached"] == 1 and result["success"] == 1 and again.calls == 1
    db.execute("DELETE FROM documents")
    assert db.execute("SELECT COUNT(*) FROM ai_chunks").fetchone()[0] == 0
    assert (
        db.execute(
            "SELECT COUNT(*) FROM ai_attempts WHERE operation='generateContent'"
        ).fetchone()[0]
        == 0
    )
