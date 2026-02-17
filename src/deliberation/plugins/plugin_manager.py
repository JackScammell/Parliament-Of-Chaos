"""
Plugin manager for installing and managing agents.
"""

import logging
from typing import Optional, List
from .plugin_registry import PluginRegistry, PluginMetadata

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugin installation and lifecycle.
    """
    
    def __init__(self, registry_path: str = ".parliament-plugins"):
        """
        Initialize plugin manager.
        
        Args:
            registry_path: Path to plugin registry
        """
        self.registry = PluginRegistry(registry_path)
        logger.info(f"Plugin manager initialized with registry at {registry_path}")
    
    def install_plugin(self, name: str, version: str, author: str, 
                      description: str, agent_type: str, 
                      skills: Optional[List[str]] = None) -> bool:
        """
        Install a new plugin agent.
        
        Args:
            name: Plugin name
            version: Plugin version
            author: Plugin author
            description: Plugin description
            agent_type: Agent type
            skills: List of skills
            
        Returns:
            True if installed successfully
        """
        plugin = PluginMetadata(
            name=name,
            version=version,
            author=author,
            description=description,
            agent_type=agent_type,
            skills=skills or []
        )
        
        if self.registry.register_plugin(plugin):
            logger.info(f"Installed plugin: {name} v{version}")
            return True
        else:
            logger.warning(f"Plugin {name} already exists")
            return False
    
    def get_plugin_info(self, name: str) -> Optional[PluginMetadata]:
        """
        Get information about an installed plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin metadata or None
        """
        return self.registry.get_plugin(name)
    
    def list_installed(self, agent_type: Optional[str] = None) -> List[PluginMetadata]:
        """
        List installed plugins.
        
        Args:
            agent_type: Optional filter by agent type
            
        Returns:
            List of installed plugins
        """
        return self.registry.list_plugins(agent_type)
    
    def search(self, query: str) -> List[PluginMetadata]:
        """
        Search for plugins.
        
        Args:
            query: Search query
            
        Returns:
            List of matching plugins
        """
        return self.registry.search_plugins(query)
    
    def get_marketplace_summary(self) -> dict:
        """
        Get summary of plugin marketplace.
        
        Returns:
            Summary dictionary
        """
        plugins = self.registry.list_plugins()
        
        by_type = {}
        for plugin in plugins:
            if plugin.agent_type not in by_type:
                by_type[plugin.agent_type] = 0
            by_type[plugin.agent_type] += 1
        
        return {
            "total_plugins": len(plugins),
            "by_type": by_type,
            "registry_path": str(self.registry.registry_path)
        }
