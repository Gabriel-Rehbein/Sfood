# backend/routes/__init__.py

from .cliente import cliente_bp
from .intranet import intranet_bp
from .ceo import ceo_bp
from .ia_routes import ia_bp

__all__ = ["cliente_bp", "intranet_bp", "ceo_bp", "ia_bp"]
