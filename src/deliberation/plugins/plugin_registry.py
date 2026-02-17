"""
Plugin registry for community agents and extensions.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class PluginMetadata(BaseModel):
    """Metadata for a plugin."""
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    author: str = Field(..., description="Plugin author")
    description: str = Field(..., description="Plugin description")
    agent_type: str = Field(..., description="Agent type (specialist, reviewer, etc.)")
    skills: List[str] = Field(default_factory=list, description="Agent skills")
    requires: List[str] = Field(default_factory=list, description="Required dependencies")


class PluginRegistry:
    """
    Central registry for agent plugins.
    """
    
    def __init__(self, registry_path: str = ".parliament-plugins"):
        """
        Initialize plugin registry.
        
        Args:
            registry_path: Path to plugin registry
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.registry_path / "registry.json"
        self._load_registry()
    
    def _load_registry(self):
        """Load plugin registry index."""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                data = json.load(f)
                self.plugins = {
                    name: PluginMetadata(**meta) 
                    for name, meta in data.get("plugins", {}).items()
                }
        else:
            self.plugins = {}
            self._save_registry()
    
    def _save_registry(self):
        """Save plugin registry index."""
        data = {
            "version": "1.0",
            "plugins": {
                name: plugin.model_dump() 
                for name, plugin in self.plugins.items()
            }
        }
        with open(self.index_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_plugin(self, plugin: PluginMetadata) -> bool:
        """
        Register a new plugin.
        
        Args:
            plugin: Plugin metadata
            
        Returns:
            True if registered successfully
        """
        if plugin.name in self.plugins:
            return False
        
        self.plugins[plugin.name] = plugin
        self._save_registry()
        return True
    
    def get_plugin(self, name: str) -> Optional[PluginMetadata]:
        """
        Get plugin metadata by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin metadata or None
        """
        return self.plugins.get(name)
    
    def list_plugins(self, agent_type: Optional[str] = None) -> List[PluginMetadata]:
        """
        List available plugins.
        
        Args:
            agent_type: Optional filter by agent type
            
        Returns:
            List of plugin metadata
        """
        plugins = list(self.plugins.values())
        
        if agent_type:
            plugins = [p for p in plugins if p.agent_type == agent_type]
        
        return plugins
    
    def search_plugins(self, query: str) -> List[PluginMetadata]:
        """
        Search plugins by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching plugins
        """
        query_lower = query.lower()
        return [
            plugin for plugin in self.plugins.values()
            if query_lower in plugin.name.lower() or 
               query_lower in plugin.description.lower()
        ]
