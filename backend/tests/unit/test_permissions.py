from app.domain.value_objects import Permission, UserRole, allows


def test_admin_can_manage_users() -> None:
    assert allows(UserRole.ADMIN, Permission.MANAGE_USERS)
    assert allows(UserRole.ADMIN, Permission.REGISTER_LOT)


def test_auditor_can_review_alerts_but_not_register_lots() -> None:
    assert allows(UserRole.AUDITOR, Permission.REVIEW_ALERT)
    assert allows(UserRole.AUDITOR, Permission.VIEW_AUDIT)
    assert not allows(UserRole.AUDITOR, Permission.REGISTER_LOT)
    assert not allows(UserRole.AUDITOR, Permission.MANAGE_USERS)


def test_producer_can_register_lot_but_not_manage_users() -> None:
    assert allows(UserRole.PRODUCER, Permission.REGISTER_LOT)
    assert allows(UserRole.PRODUCER, Permission.TRANSFER_CUSTODY)
    assert not allows(UserRole.PRODUCER, Permission.MANAGE_USERS)


def test_carrier_can_register_transport_only() -> None:
    assert allows(UserRole.CARRIER, Permission.REGISTER_TRANSPORT)
    assert not allows(UserRole.CARRIER, Permission.REGISTER_RECEPTION)


def test_receiver_can_register_reception_and_weighing() -> None:
    assert allows(UserRole.RECEIVER, Permission.REGISTER_RECEPTION)
    assert allows(UserRole.RECEIVER, Permission.REGISTER_WEIGHING)
    assert not allows(UserRole.RECEIVER, Permission.TRANSFER_CUSTODY)
