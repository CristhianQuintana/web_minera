from typing import Any

import httpx

from app.infrastructure.configuration.settings import Settings


class MLServiceAdapter:
    def __init__(self, settings: Settings) -> None:
        self._url = (settings.ml_service_url or "").rstrip("/")

    @property
    def is_configured(self) -> bool:
        return bool(self._url)

    def estimate(self, features: dict[str, Any]) -> dict[str, Any]:
        """Llama al servicio ML. Solo usa fallback si no hay URL o la llamada falla."""
        if self._url:
            try:
                response = httpx.post(
                    f"{self._url}/inference/estimate",
                    json=features,
                    timeout=10.0,
                )
                response.raise_for_status()
                payload = response.json()
                payload["source"] = "ml_service"
                payload.setdefault("features", features)
                if isinstance(payload.get("features"), dict):
                    merged = dict(features)
                    merged.update(payload["features"])
                    payload["features"] = merged
                return payload
            except Exception:
                pass
        return self._fallback(features)

    def _fallback(self, features: dict[str, Any]) -> dict[str, Any]:
        origin = float(features.get("origin_quantity") or 0)
        mineral = str(features.get("mineral") or "").lower()
        factor = 0.985
        if "oro" in mineral:
            factor = 0.978
        elif "plata" in mineral:
            factor = 0.982
        elif "cobre" in mineral:
            factor = 0.985
        return {
            "expected_quantity": round(origin * factor, 4),
            "model_version": "1.0.0-fallback",
            "source": "fallback",
            "features": {
                **features,
                "mineral_factor": factor,
                "fallback_reason": "ml_service_unavailable" if self._url else "ml_service_not_configured",
            },
        }
