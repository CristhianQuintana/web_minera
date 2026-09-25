from application.use_cases.estimate import EstimateExpectedQuantity
from domain.services.estimator import ExpectedQuantityEstimator


def estimate_use_case() -> EstimateExpectedQuantity:
    return EstimateExpectedQuantity(ExpectedQuantityEstimator())
