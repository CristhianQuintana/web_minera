"""Reexportación de compatibilidad.

AuthContext pertenece a la capa de aplicación. Este módulo se conserva
para no romper importaciones históricas de infraestructura.
"""

from app.application.auth_context import AuthContext

__all__ = ["AuthContext"]
