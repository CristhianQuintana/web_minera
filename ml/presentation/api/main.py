"""Compatibilidad: el adaptador canónico vive en adapters.inbound.http."""

from adapters.inbound.http.main import app

__all__ = ["app"]
