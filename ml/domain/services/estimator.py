from typing import Any


class ExpectedQuantityEstimator:
    """Estimador de cantidad esperada. Produce una señal revisable, nunca una sentencia."""

    version = "1.0.0"

    def estimate(self, features: dict[str, Any]) -> dict[str, Any]:
        origin = float(features.get("origin_quantity") or 0)
        mineral = (features.get("mineral") or "").lower()
        factor = 0.985
        if "oro" in mineral:
            factor = 0.978
        elif "carbón" in mineral or "carbon" in mineral:
            factor = 0.96
        expected = round(origin * factor, 4)
        return {
            "expected_quantity": expected,
            "model_version": self.version,
            "features": {
                "origin_quantity": origin,
                "mineral_factor": factor,
                "mineral": features.get("mineral"),
                "unit": features.get("unit"),
            },
        }
