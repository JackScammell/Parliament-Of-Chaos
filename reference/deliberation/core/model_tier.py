"""
Model tiering system for Parliament of Chaos.
Separates responsibilities by reasoning complexity.
"""

from typing import Dict, Literal, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Model role types
ModelRole = Literal["chair", "agent", "summariser", "validator"]


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: str = "anthropic"  # anthropic, openai, etc.
    max_tokens: int = 4096
    temperature: float = 0.7


class ModelRegistry:
    """
    Registry for model tiers.
    Never use top-tier model for summarisation or validation.
    """
    
    def __init__(self):
        self._registry: Dict[ModelRole, ModelConfig] = {}
        self._default_registry()
    
    def _default_registry(self):
        """Set up default model tiers."""
        # Most capable model for Chair/Arbiter (high reasoning)
        self._registry["chair"] = ModelConfig(
            name="claude-3-5-sonnet-20241022",
            provider="anthropic",
            max_tokens=8192,
            temperature=0.7
        )
        
        # Mid-tier for debate agents
        self._registry["agent"] = ModelConfig(
            name="claude-3-5-haiku-20241022",
            provider="anthropic", 
            max_tokens=4096,
            temperature=0.8
        )
        
        # Small/fast for summariser
        self._registry["summariser"] = ModelConfig(
            name="claude-3-5-haiku-20241022",
            provider="anthropic",
            max_tokens=2048,
            temperature=0.5
        )
        
        # Small/fast for validator
        self._registry["validator"] = ModelConfig(
            name="claude-3-5-haiku-20241022",
            provider="anthropic",
            max_tokens=1024,
            temperature=0.3
        )
    
    def get_model(self, role: ModelRole) -> ModelConfig:
        """Get model configuration for a specific role."""
        if role not in self._registry:
            raise ValueError(f"Unknown model role: {role}")
        return self._registry[role]
    
    def register_model(self, role: ModelRole, config: ModelConfig):
        """Register or update a model for a specific role."""
        self._registry[role] = config
        logger.info(f"Registered model '{config.name}' for role '{role}'")
    
    def get_all_models(self) -> Dict[ModelRole, ModelConfig]:
        """Get all registered models."""
        return self._registry.copy()


# Global registry instance
_global_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """Get the global model registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ModelRegistry()
    return _global_registry


def configure_models(
    chair_model: Optional[str] = None,
    agent_model: Optional[str] = None,
    summariser_model: Optional[str] = None,
    validator_model: Optional[str] = None
):
    """
    Configure models for different roles.
    
    Args:
        chair_model: Model name for chair/arbiter role
        agent_model: Model name for debate agents
        summariser_model: Model name for summarisation
        validator_model: Model name for validation
    """
    registry = get_registry()
    
    if chair_model:
        registry.register_model("chair", ModelConfig(name=chair_model))
    if agent_model:
        registry.register_model("agent", ModelConfig(name=agent_model))
    if summariser_model:
        registry.register_model("summariser", ModelConfig(name=summariser_model))
    if validator_model:
        registry.register_model("validator", ModelConfig(name=validator_model))


class ModelCaller:
    """
    Abstract interface for calling models.
    Actual implementation would integrate with Anthropic/OpenAI APIs.
    """
    
    def __init__(self, registry: Optional[ModelRegistry] = None):
        self.registry = registry or get_registry()
    
    def call_model(self, role: ModelRole, prompt: str, **kwargs) -> str:
        """
        Call appropriate model for the given role.
        
        Args:
            role: Model role (chair, agent, summariser, validator)
            prompt: Prompt to send to model
            **kwargs: Additional parameters (temperature override, etc.)
            
        Returns:
            Model response as string
        """
        model_config = self.registry.get_model(role)
        
        # This is a placeholder - actual implementation would call the API
        logger.info(
            f"Calling {role} model: {model_config.name} "
            f"(temp={kwargs.get('temperature', model_config.temperature)})"
        )
        
        # In real implementation, this would:
        # 1. Get API client for provider
        # 2. Send request with prompt and config
        # 3. Return response text
        raise NotImplementedError(
            "ModelCaller.call_model must be implemented with actual API integration"
        )
    
    async def call_model_async(self, role: ModelRole, prompt: str, **kwargs) -> str:
        """
        Async version of call_model for parallel execution.
        
        Args:
            role: Model role (chair, agent, summariser, validator)
            prompt: Prompt to send to model
            **kwargs: Additional parameters
            
        Returns:
            Model response as string
        """
        model_config = self.registry.get_model(role)
        
        logger.info(
            f"Calling {role} model async: {model_config.name} "
            f"(temp={kwargs.get('temperature', model_config.temperature)})"
        )
        
        # In real implementation, this would use async API client
        raise NotImplementedError(
            "ModelCaller.call_model_async must be implemented with actual API integration"
        )
