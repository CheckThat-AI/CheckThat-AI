import os
import sys
from pathlib import Path
from typing import Union, Type, List, Dict, Any
from ...types.feedback import Feedback
from ..._utils.LLMRouter import LLMRouter
from ...services.refinement.refine import refine_claims_service

def refine_claims(response: Any, checkthat_config: Dict[str, Any]) -> Any:
    """
    Legacy function that wraps the new refinement service.
    Maintained for backward compatibility.
    """
    config = {
        'model': checkthat_config.get('refine_model') or checkthat_config.get('model', 'gpt-3.5-turbo'),
        'threshold': checkthat_config.get('refine_threshold', 0.5),
        'max_iters': checkthat_config.get('refine_max_iters', 3),
        'metrics': checkthat_config.get('refine_metrics'),
        'api_key': checkthat_config.get('checkthat_api_key')
    }
    
    refined_response, metadata = refine_claims_service(response, config)
    return refined_response