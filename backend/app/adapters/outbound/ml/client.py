from typing import Any

import httpx

from app.infrastructure.configuration.settings import Settings


class MLServiceAdapter:
    def __init__(self, settings: Settings) -> None:
        self._url = settings.ml_service_url.rstrip("/")

    def estimate(self, features: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.post(f"{self._url}/inference/estimate", json=features, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            origin = float(features.get("origin_quantity") or 0)
            return {
                "expected_quantity": round(origin * 0.985, 4),
                "model_version": "1.0.0-fallback",
                "features": features,
            }
