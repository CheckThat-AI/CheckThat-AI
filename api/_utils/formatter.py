import logging
from typing import Dict, Any, List, Optional, Union, Tuple

try:
    from .prompts import sys_prompt as DefaultSystemPrompt
except ImportError:
    # Fallback for testing
    DefaultSystemPrompt = "You are a helpful AI assistant."

logger = logging.getLogger(__name__)


class OpenAITypesFormatter:
    """
    Centralized formatter for converting OpenAI-compatible parameters to different API provider formats.
    
    This class handles the transformation of request parameters from our unified format
    to the specific formats required by different LLM providers.
    """
    
    def __init__(self):
        self.default_system_prompt = DefaultSystemPrompt
    
    def process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process messages array, ensuring there's a system prompt.
        
        Args:
            messages: List of message dictionaries from the request
            
        Returns:
            Processed messages list with system prompt ensured
        """
        if not messages:
            return [
                {"role": "system", "content": self.default_system_prompt},
                {"role": "user", "content": ""}
            ]
        
        # Check if there's already a system message
        has_system_message = any(msg.get("role") == "system" for msg in messages)
        
        if has_system_message:
            # Return messages as-is if system prompt already exists
            return messages
        else:
            # Prepend default system prompt
            return [
                {"role": "system", "content": self.default_system_prompt},
                *messages
            ]
    
    # ============================================================================
    # CLIENT FORMATTER DISPATCHER
    # ============================================================================
    
    def format_for_client(self, openai_payload: Dict[str, Any], client_type: str) -> Dict[str, Any]:
        """
        Format OpenAI-compatible payload for specific LLM client API.
        
        Args:
            openai_payload: OpenAI-compatible payload dictionary
            client_type: String identifier for the client type (e.g., "OpenAIClient", "AnthropicClient")
            
        Returns:
            Payload formatted for the specific client API
        """
        # Process messages first (common for all clients)
        if 'messages' in openai_payload:
            openai_payload['messages'] = self.process_messages(openai_payload['messages'])
        
        # Dispatch to appropriate formatter based on client type
        if 'openai' in client_type.lower() or 'xai' in client_type.lower():
            return self.format_for_openai(openai_payload)
        elif 'anthropic' in client_type.lower():
            return self.format_for_anthropic(openai_payload)
        elif 'gemini' in client_type.lower():
            return self.format_for_gemini(openai_payload)
        elif 'together' in client_type.lower():
            return self.format_for_together(openai_payload)
        else:
            # Default to OpenAI format
            logger.warning(f"Unknown client type '{client_type}', using OpenAI format")
            return self.format_for_openai(openai_payload)
    
    def format_response_to_openai(self, response: Any, client_type: str) -> Dict[str, Any]:
        """
        Format any LLM response to OpenAI-compatible format.
        
        Args:
            response: Raw response from LLM client
            client_type: String identifier for the client type
            
        Returns:
            OpenAI-compatible response dictionary
        """
        if 'openai' in client_type.lower() or 'xai' in client_type.lower():
            return response
        elif 'anthropic' in client_type.lower():
            return self._format_anthropic_response_to_openai(response)
        elif 'gemini' in client_type.lower():
            return self._format_gemini_response_to_openai(response)
        elif 'together' in client_type.lower():
            return self._format_together_response_to_openai(response)
        else:
            logger.warning(f"Unknown client type '{client_type}', returning raw response")
            return response
    
    # ============================================================================
    # LEGACY METHODS (KEPT FOR BACKWARD COMPATIBILITY)
    # ============================================================================
    
    def extract_openai_base_params(self, body: Any) -> Dict[str, Any]:
        """
        Extract OpenAI-compatible parameters from CheckThatCompletionCreateParams.
        This forms the base for all API transformations.
        
        Args:
            body: The request body containing all parameters
            
        Returns:
            Dictionary with OpenAI-compatible parameters
        """
        # Define CheckThat-specific fields to exclude
        checkthat_fields = {
            'refine_claims',
            'post_norm_eval_metrics', 
            'save_eval_report',
            'checkthat_api_key'
        }
        
        # Get all fields from the request, excluding None values and CheckThat fields
        openai_params = {}
        for field_name, field_value in body.model_dump(exclude_none=True).items():
            if field_name not in checkthat_fields:
                if field_name == 'messages':
                    # Process messages to ensure system prompt
                    openai_params[field_name] = self.process_messages(field_value)
                else:
                    openai_params[field_name] = field_value
        
        return openai_params
    
    def extract_checkthat_params(self, body: Any) -> Dict[str, Any]:
        """
        Extract CheckThat AI specific parameters.
        
        Args:
            body: The request body containing all parameters
            
        Returns:
            Dictionary with CheckThat-specific parameters
        """
        return {
            'refine_claims': body.refine_claims,
            'post_norm_eval_metrics': body.post_norm_eval_metrics,
            'save_eval_report': body.save_eval_report,
            'checkthat_api_key': body.checkthat_api_key
        }
    
    # ============================================================================
    # OPENAI & XAI FORMATTERS (IDENTICAL APIs)
    # ============================================================================
    
    def format_for_openai(self, body: Any) -> Dict[str, Any]:
        """
        Format parameters for OpenAI API.
        
        Args:
            body: The request body containing all parameters
            
        Returns:
            Dictionary formatted for OpenAI chat.completions.create()
        """
        # OpenAI uses the parameters as-is, so this is mostly passthrough
        logger.info("Formatting parameters for OpenAI API")
        
        if hasattr(body, 'model_dump'):
            # It's a Pydantic model
            openai_params = self.extract_openai_base_params(body)
        else:
            # It's already a dict
            openai_params = body
        
        return openai_params
    
    def format_for_xai(self, body: Any) -> Dict[str, Any]:
        """
        Format parameters for xAI API (Grok models).
        
        Args:
            body: The request body containing all parameters
            
        Returns:
            Dictionary formatted for xAI chat.completions.create()
        """
        # xAI uses the same format as OpenAI
        logger.info("Formatting parameters for xAI API")
        return self.format_for_openai(body)
    
    # ============================================================================
    # TOGETHER AI FORMATTER (MINIMAL PROCESSING)
    # ============================================================================
    
    def format_for_together(self, body: Any) -> Dict[str, Any]:
        """
        Format parameters for Together AI API.
        
        Args:
            body: The request body containing all parameters
            
        Returns:
            Dictionary formatted for Together AI chat.completions.create()
        """
        logger.info("Formatting parameters for Together AI API")
        
        if hasattr(body, 'model_dump'):
            openai_params = self.extract_openai_base_params(body)
        else:
            openai_params = body
        
        return openai_params
    
    # ============================================================================
    # ANTHROPIC FORMATTER (MAJOR TRANSFORMATION)
    # ============================================================================
    
    def format_for_anthropic(self, body: Any) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Format parameters for Anthropic API (Claude models).
        
        Args:
            body: The request body containing all parameters
            
        Returns:
            Tuple of (system_instruction, messages, additional_params)
        """
        logger.info("Formatting parameters for Anthropic API")
        
        if hasattr(body, 'model_dump'):
            openai_params = self.extract_openai_base_params(body)
        else:
            openai_params = body
        
        messages = openai_params.get("messages", [])
        
        # Extract system prompt
        system_instruction = self.default_system_prompt
        anthropic_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_instruction = msg.get("content", self.default_system_prompt)
            else:
                anthropic_messages.append(msg)
        
        # Transform OpenAI parameters to Anthropic format
        additional_params = {}
        
        # Parameter mapping
        if 'max_tokens' in openai_params:
            additional_params['max_tokens'] = openai_params['max_tokens']
        if 'temperature' in openai_params:
            additional_params['temperature'] = openai_params['temperature']
        if 'top_p' in openai_params:
            additional_params['top_p'] = openai_params['top_p']
        if 'stream' in openai_params:
            additional_params['stream'] = openai_params['stream']
        
        return system_instruction, anthropic_messages, additional_params
    
    # ============================================================================
    # GEMINI FORMATTER (MAJOR TRANSFORMATION)
    # ============================================================================
    
    def format_for_gemini(self, body: Any) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Format parameters for Google Gemini API.
        
        Args:
            body: The request body containing all parameters
            
        Returns:
            Tuple of (system_instruction, contents, generation_config)
        """
        logger.info("Formatting parameters for Gemini API")
        
        if hasattr(body, 'model_dump'):
            openai_params = self.extract_openai_base_params(body)
        else:
            openai_params = body
        
        messages = openai_params.get("messages", [])
        
        # Extract system instruction
        system_instruction = self.default_system_prompt
        gemini_contents = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_instruction = msg.get("content", self.default_system_prompt)
            elif msg.get("role") == "user":
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": msg.get("content", "")}]
                })
            elif msg.get("role") == "assistant":
                gemini_contents.append({
                    "role": "model",  # Gemini uses "model" instead of "assistant"
                    "parts": [{"text": msg.get("content", "")}]
                })
        
        # Transform OpenAI parameters to Gemini generation config
        generation_config = {}
        
        # Parameter mapping
        if 'temperature' in openai_params:
            generation_config['temperature'] = openai_params['temperature']
        if 'max_tokens' in openai_params:
            generation_config['max_output_tokens'] = openai_params['max_tokens']
        if 'top_p' in openai_params:
            generation_config['top_p'] = openai_params['top_p']
        
        return system_instruction, gemini_contents, generation_config
    
    # ============================================================================
    # RESPONSE FORMATTERS (FOR CONSISTENCY)
    # ============================================================================
    
    def _format_anthropic_response_to_openai(self, response: Any) -> Dict[str, Any]:
        """Format Anthropic response to OpenAI format."""
        logger.info("Transforming Anthropic response to OpenAI format")
        # Placeholder implementation
        return {}
    
    def _format_gemini_response_to_openai(self, response: Any) -> Dict[str, Any]:
        """Format Gemini response to OpenAI format."""
        logger.info("Transforming Gemini response to OpenAI format")
        # Placeholder implementation
        return {}
    
    def _format_together_response_to_openai(self, response: Any) -> Dict[str, Any]:
        """Format Together AI response to OpenAI format."""
        logger.info("Transforming Together AI response to OpenAI format")
        # Placeholder implementation
        return {}


# Global formatter instance
openai_formatter = OpenAITypesFormatter()
