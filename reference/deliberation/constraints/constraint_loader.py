"""
Load and manage user-defined constraints.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Optional
from ..models.schemas import ConstraintDefinition


class ConstraintLoader:
    """
    Load constraints from YAML or JSON files.
    """
    
    def __init__(self):
        """Initialize constraint loader."""
        pass
    
    def load_from_file(self, filepath: str) -> ConstraintDefinition:
        """
        Load constraints from a file.
        
        Args:
            filepath: Path to constraint file (.yaml or .json)
            
        Returns:
            ConstraintDefinition object
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Constraint file not found: {filepath}")
        
        # Load based on extension
        if path.suffix in ['.yaml', '.yml']:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
        elif path.suffix == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        # Parse constraints section
        constraints_data = data.get('constraints', {})
        
        return ConstraintDefinition(
            max_rounds=constraints_data.get('max_rounds'),
            disallowed_patterns=constraints_data.get('disallowed_patterns', []),
            required_validators=constraints_data.get('required_validators', []),
            custom_rules=constraints_data.get('custom_rules', {})
        )
    
    def load_from_dict(self, data: Dict) -> ConstraintDefinition:
        """
        Load constraints from a dictionary.
        
        Args:
            data: Constraint data
            
        Returns:
            ConstraintDefinition object
        """
        return ConstraintDefinition(**data)
    
    def create_default_constraints(self) -> ConstraintDefinition:
        """
        Create default constraint definition.
        
        Returns:
            Default ConstraintDefinition
        """
        return ConstraintDefinition(
            max_rounds=10,
            disallowed_patterns=[],
            required_validators=[],
            custom_rules={}
        )
