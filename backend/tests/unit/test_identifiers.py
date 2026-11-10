from app.domain.services.identifiers import is_uuid


def test_is_uuid_accepts_valid() -> None:
    assert is_uuid("0e67ef66-fde7-44d8-b2b5-e62908f7fd29")
    assert is_uuid("E857FA80-1678-4B27-B80F-C38F471A8931")


def test_is_uuid_rejects_commercial_codes() -> None:
    assert not is_uuid("LOT-2026-090")
    assert not is_uuid("")
    assert not is_uuid(None)
    assert not is_uuid("not-a-uuid")
