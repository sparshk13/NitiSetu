"""
Application configuration module.
Re-exports settings from backend.app.core.config for backward compatibility.
"""
from backend.app.core.config import Settings, settings

__all__ = ["Settings", "settings"]
