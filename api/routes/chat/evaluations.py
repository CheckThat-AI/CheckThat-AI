import os
import sys
from pathlib import Path
from typing import Union, Type, List, Dict, Any
from ..._utils.LLMRouter import LLMRouter
from ...services.evaluation.evaluate import evaluate_claims_service

def evaluate_claims(response: Any, checkthat_config: Dict[str, Any]) -> Any:
    """
    Legacy function that wraps the new evaluation service.
    Maintained for backward compatibility.
    """
    config = {
        'metrics': checkthat_config.get('post_norm_eval_metrics', []),
        'model': checkthat_config.get('refine_model') or checkthat_config.get('model', 'gpt-3.5-turbo'),
        'api_key': checkthat_config.get('checkthat_api_key')
    }
    
    evaluated_response, report = evaluate_claims_service(response, config)
    return evaluated_response