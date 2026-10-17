import time

from fastapi.testclient import TestClient

from app.composition.application_factory.factory import create_app

client = TestClient(create_app())


def test_health_responds_under_500_ms() -> None:
    started = time.perf_counter()
    response = client.get("/health")
    elapsed_ms = (time.perf_counter() - started) * 1000
    assert response.status_code == 200
    assert elapsed_ms < 500
