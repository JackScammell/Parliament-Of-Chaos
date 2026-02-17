"""
Validation layer for Parliament of Chaos deliberation system.
All outputs must pass validation before state mutation.
"""

import json
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ValidationResult:
    """Result of a validation attempt."""
    
    def __init__(self, success: bool, data: Optional[BaseModel] = None, 
                 errors: Optional[list] = None, raw_output: Optional[str] = None):
        self.success = success
        self.data = data
        self.errors = errors or []
        self.raw_output = raw_output


class Validator:
    """Validates agent outputs against schemas with retry logic."""
    
    def __init__(self, max_retries: int = 1):
        self.max_retries = max_retries
    
    def validate(self, raw_output: str, schema: Type[T], 
                 retry_count: int = 0) -> ValidationResult:
        """
        Validate raw output against a schema.
        
        Args:
            raw_output: Raw JSON string from agent
            schema: Pydantic model class to validate against
            retry_count: Current retry attempt
            
        Returns:
            ValidationResult with success status and parsed data or errors
        """
        try:
            # Parse JSON
            data_dict = json.loads(raw_output)
            
            # Validate against schema
            validated_data = schema(**data_dict)
            
            logger.info(f"Successfully validated {schema.__name__}")
            return ValidationResult(success=True, data=validated_data, raw_output=raw_output)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing failed: {str(e)}"
            logger.error(error_msg)
            return ValidationResult(
                success=False, 
                errors=[{"type": "json_decode", "message": error_msg}],
                raw_output=raw_output
            )
            
        except ValidationError as e:
            error_msg = f"Schema validation failed: {str(e)}"
            logger.error(error_msg)
            errors = [
                {"type": "validation", "field": err["loc"], "message": err["msg"]}
                for err in e.errors()
            ]
            return ValidationResult(
                success=False,
                errors=errors,
                raw_output=raw_output
            )
            
        except Exception as e:
            error_msg = f"Unexpected validation error: {str(e)}"
            logger.error(error_msg)
            return ValidationResult(
                success=False,
                errors=[{"type": "unexpected", "message": error_msg}],
                raw_output=raw_output
            )
    
    def validate_with_retry(self, raw_output: str, schema: Type[T],
                           retry_callback=None) -> ValidationResult:
        """
        Validate with automatic retry on failure.
        
        Args:
            raw_output: Raw JSON string from agent
            schema: Pydantic model class to validate against
            retry_callback: Optional function to call for retry (gets error feedback)
            
        Returns:
            ValidationResult from final attempt
        """
        result = self.validate(raw_output, schema, retry_count=0)
        
        if not result.success and retry_callback and self.max_retries > 0:
            logger.info(f"Validation failed, retrying (max {self.max_retries} attempts)")
            
            for retry in range(self.max_retries):
                # Provide error feedback to callback
                error_feedback = self._format_error_feedback(result.errors)
                
                try:
                    # Get corrected output
                    corrected_output = retry_callback(error_feedback, raw_output)
                    result = self.validate(corrected_output, schema, retry_count=retry + 1)
                    
                    if result.success:
                        logger.info(f"Validation succeeded on retry {retry + 1}")
                        return result
                except Exception as e:
                    logger.error(f"Retry callback failed: {str(e)}")
                    continue
            
            logger.warning(f"Validation failed after {self.max_retries} retries")
        
        return result
    
    def _format_error_feedback(self, errors: list) -> str:
        """Format validation errors into helpful feedback message."""
        if not errors:
            return "Unknown validation error"
        
        feedback_lines = ["Validation failed with the following errors:"]
        for error in errors:
            if error["type"] == "json_decode":
                feedback_lines.append(f"- Invalid JSON format: {error['message']}")
            elif error["type"] == "validation":
                feedback_lines.append(
                    f"- Field '{'.'.join(map(str, error['field']))}': {error['message']}"
                )
            else:
                feedback_lines.append(f"- {error['message']}")
        
        feedback_lines.append("\nPlease ensure output matches the required schema exactly.")
        return "\n".join(feedback_lines)


def enforce_json_structure(data: Dict[str, Any], schema: Type[T]) -> T:
    """
    Enforce JSON structure and field types.
    Raises ValidationError if invalid.
    
    Args:
        data: Dictionary to validate
        schema: Pydantic model class
        
    Returns:
        Validated instance of schema
    """
    return schema(**data)


def clamp_confidence_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clamp confidence values to 0-1 range in a dictionary.
    Modifies in place and returns the modified dict.
    
    Args:
        data: Dictionary potentially containing confidence values
        
    Returns:
        Modified dictionary with clamped confidence values
    """
    if "confidence" in data:
        data["confidence"] = max(0.0, min(1.0, float(data["confidence"])))
    
    # Handle nested structures
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = clamp_confidence_values(value)
        elif isinstance(value, list):
            data[key] = [
                clamp_confidence_values(item) if isinstance(item, dict) else item
                for item in value
            ]
    
    return data
