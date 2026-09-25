class DomainError(Exception):
    code = "domain_error"
    status_code = 400

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class InvalidLotState(DomainError):
    code = "invalid_lot_state"
    status_code = 422


class InvalidCustodyTransfer(DomainError):
    code = "invalid_custody_transfer"
    status_code = 422


class InvalidQuantity(DomainError):
    code = "invalid_quantity"
    status_code = 422


class InvalidMassBalance(DomainError):
    code = "invalid_mass_balance"
    status_code = 422


class InvalidEvidence(DomainError):
    code = "invalid_evidence"
    status_code = 422


class UnauthorizedError(DomainError):
    code = "unauthorized"
    status_code = 401


class ForbiddenError(DomainError):
    code = "forbidden"
    status_code = 403


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404


class ConflictError(DomainError):
    code = "conflict"
    status_code = 409


class InactiveAccountError(DomainError):
    code = "inactive_account"
    status_code = 403


class InvitationInvalidError(DomainError):
    code = "invitation_invalid"
    status_code = 400
