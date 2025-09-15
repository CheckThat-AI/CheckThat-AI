from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
from .evals import EvaluationReport

class ReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: Optional[str] = None

class OpenAIMessage(BaseModel):
    """OpenAI-compatible message format."""
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, List[Dict[str, Any]], None] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionAudioParam(BaseModel):
    """Audio generation parameters for OpenAI-compatible requests."""
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    format: Literal["wav", "mp3", "flac", "opus", "pcm16"] = "mp3"


class ChatCompletionPredictionContentParam(BaseModel):
    """Prediction content parameters."""
    type: Literal["content"]
    content: str


class ChatCompletionToolChoiceOptionParam(BaseModel):
    """Tool choice parameters."""
    type: Literal["function", "auto", "none"]
    function: Optional[Dict[str, str]] = None


class ChatCompletionToolParam(BaseModel):
    """Tool definition parameters."""
    type: Literal["function"]
    function: Dict[str, Any]


class ChatCompletionStreamOptionsParam(BaseModel):
    """Streaming options parameters."""
    include_usage: bool = False


class ChatCompletionMessageParam(BaseModel):
    """Message parameters for chat completions."""
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, List[Dict[str, Any]], None] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionModality(BaseModel):
    """Modality parameters for chat completions."""
    type: Literal["text", "audio"]


class ChatCompletionWebSearchOptions(BaseModel):
    """Web search options parameters."""
    search_context_size: Optional[Literal["low", "medium", "high"]] = None
    user_location: Optional[Dict[str, Any]] = None


class Metadata(BaseModel):
    """Metadata parameters."""
    pass  # Placeholder for metadata structure


class ChatCompletionCreateParams(BaseModel):
    """
    Complete OpenAI-compatible chat completion request parameters.
    Supports all 40+ OpenAI parameters plus CheckThat AI custom enhancements.
    """

    # Core required parameters
    messages: List[ChatCompletionMessageParam]
    model: str
    api_key: Optional[str] = None  # API key for LLM provider (OpenAI, Gemini, etc.)

    # Audio parameters
    audio: Optional[ChatCompletionAudioParam] = None

    # Response format (for structured outputs)
    response_format: Optional[Dict[str, Any]] = None

    # Generation control parameters
    frequency_penalty: Optional[float] = None
    function_call: Optional[Union[str, Dict[str, Any]]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    logit_bias: Optional[Dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_completion_tokens: Optional[int] = None
    max_tokens: Optional[int] = None

    # Metadata and organization
    metadata: Optional[Metadata] = None
    modalities: Optional[List[Literal["text", "audio"]]] = None

    # Multiple completions and advanced features
    n: Optional[int] = None
    parallel_tool_calls: Optional[bool] = None
    prediction: Optional[ChatCompletionPredictionContentParam] = None
    presence_penalty: Optional[float] = None
    prompt_cache_key: Optional[str] = None
    reasoning_effort: Optional[ReasoningEffort] = None
    safety_identifier: Optional[str] = None
    seed: Optional[int] = None
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] = None
    stop: Optional[Union[str, List[str]]] = None
    store: Optional[bool] = None
    stream_options: Optional[ChatCompletionStreamOptionsParam] = None
    stream: Optional[bool] = None
    temperature: Optional[float] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    tools: Optional[List[ChatCompletionToolParam]] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: Optional[str] = None
    verbosity: Optional[Literal["low", "medium", "high"]] = None
    web_search_options: Optional[ChatCompletionWebSearchOptions] = None

    # OpenAI infrastructure parameters
    extra_headers: Optional[Dict[str, str]] = None
    extra_query: Optional[Dict[str, Any]] = None
    timeout: Optional[Union[float, Dict[str, float]]] = None

    # CheckThat AI Custom Parameters (processed from extra_body)
    refine_claims: bool = Field(default=False, description="Enable claim refinement and normalization")
    post_norm_eval_metrics: Optional[List[str]] = Field(default=None, description="Quality evaluation metrics to run")
    save_eval_report: Optional[bool] = Field(default=None, description="Save evaluation reports")
    checkthat_api_key: Optional[str] = Field(default=None, description="CheckThat AI API key for cloud services")


class CompletionUsage(BaseModel):
    """Token usage statistics for chat completions."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionChoice(BaseModel):
    """Individual choice in chat completion response."""
    index: int
    message: Dict[str, Any]
    finish_reason: Optional[str] = None



class ChatCompletion(BaseModel):
    """
    Complete OpenAI-compatible ChatCompletion response with CheckThat AI extensions.
    """
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: CompletionUsage
    system_fingerprint: Optional[str] = None

    # CheckThat AI extensions (when applicable)
    evaluation_report: Optional[EvaluationReport] = None
    refinement_metadata: Optional[Dict[str, Any]] = None


class ParsedChatCompletion(BaseModel):
    """
    Parsed chat completion response for structured outputs.
    This matches OpenAI's ParsedChatCompletion[T] generic type.
    """
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]  # Contains parsed data
    usage: CompletionUsage
    system_fingerprint: Optional[str] = None

    # CheckThat AI extensions
    evaluation_report: Optional[EvaluationReport] = None
    refinement_metadata: Optional[Dict[str, Any]] = None
