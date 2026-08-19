"""
Plugin system for extensible agent marketplace.
"""

from .plugin_manager import PluginManager
from .plugin_registry import PluginRegistry

__all__ = ["PluginManager", "PluginRegistry"]
