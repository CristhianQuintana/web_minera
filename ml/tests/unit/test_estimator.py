from domain.services.estimator import ExpectedQuantityEstimator


def test_estimate_is_review_signal_not_verdict() -> None:
    result = ExpectedQuantityEstimator().estimate({"origin_quantity": 100, "mineral": "Oro"})
    assert result["expected_quantity"] == 97.8
    assert result["model_version"] == "1.0.0"
    assert "fraude" not in str(result).lower()
