from app.adapters.outbound.ml.client import MLServiceAdapter
from app.infrastructure.configuration.settings import Settings


def test_fallback_when_ml_url_missing() -> None:
    adapter = MLServiceAdapter(Settings(ml_service_url=""))
    result = adapter.estimate({"origin_quantity": 100, "mineral": "Oro"})
    assert result["source"] == "fallback"
    assert result["model_version"].endswith("fallback")
    assert result["expected_quantity"] == 97.8


def test_fallback_marks_reason_when_service_configured_but_down() -> None:
    adapter = MLServiceAdapter(Settings(ml_service_url="http://127.0.0.1:9"))
    result = adapter.estimate({"origin_quantity": 200, "mineral": "Cobre"})
    assert result["source"] == "fallback"
    assert result["features"]["fallback_reason"] == "ml_service_unavailable"
