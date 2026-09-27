from fastapi.testclient import TestClient


def test_liveness_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Pik Nirnay"


def test_readiness_degrades_without_crashing_when_db_unavailable(client: TestClient) -> None:
    # No Postgres is guaranteed to be running in the test environment; the
    # endpoint must still respond, per graceful-degradation requirements.
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert isinstance(body["database"], bool)
