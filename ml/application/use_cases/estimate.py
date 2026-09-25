from typing import Any

from domain.services.estimator import ExpectedQuantityEstimator


class EstimateExpectedQuantity:
    def __init__(self, estimator: ExpectedQuantityEstimator) -> None:
        self._estimator = estimator

    def execute(self, features: dict[str, Any]) -> dict[str, Any]:
        return self._estimator.estimate(features)
