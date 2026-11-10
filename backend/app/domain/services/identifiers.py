from __future__ import annotations

import re
from uuid import UUID

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def is_uuid(value: str | None) -> bool:
    if not value:
        return False
    text = str(value).strip()
    if not _UUID_RE.match(text):
        return False
    try:
        UUID(text)
        return True
    except ValueError:
        return False
