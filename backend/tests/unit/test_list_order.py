from app.application.dto import PageQuery
from app.application.services.platform import _order_for_table


def test_ml_models_orders_by_registered_at() -> None:
    query = PageQuery(page=1, page_size=50, sort="created_at", order="desc")
    assert _order_for_table("ml_models", query) == "registered_at.desc"


def test_other_tables_keep_created_at() -> None:
    query = PageQuery(page=1, page_size=20, sort="created_at", order="desc")
    assert _order_for_table("ml_inferences", query) == "created_at.desc"
