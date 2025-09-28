from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union, Literal, TypeVar
from typing_extensions import Iterable,Literal, Required, TypeAlias, TypedDict
from openai.types.chat import ChatCompletion
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
from openai.types.chat.completion_create_params import CompletionCreateParams
from openai import Stream
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam, ChatCompletionChunk
from openai.resources.chat import Completions as OpenAIChatCompletions
from openai.resources.chat import AsyncCompletions as OpenAIAsyncCompletions
import httpx
from openai._types import NOT_GIVEN, Headers, Body, Query, NotGiven
from openai import Stream, AsyncStream
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
from deepeval.metrics import GEval, BaseMetric

class ReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: Optional[str] = None

# Type variable for response format matching OpenAI's pattern
ResponseFormatT = TypeVar("ResponseFormatT")

class EvaluationReport(BaseModel):
    """Evaluation report for post-normalization quality audits."""
    metrics_used: List[str] = Field(description="The evaluation metrics that were applied")
    scores: Dict[str, float] = Field(description="Scores for each metric (0.0 to 1.0 scale)")
    detailed_results: Dict[str, Dict[str, Any]] = Field(description="Detailed results for each metric")
    timestamp: str = Field(description="ISO timestamp when the evaluation was performed")
    report_url: Optional[str] = Field(default=None, description="URL to the full evaluation report if saved to cloud")
    model_info: Optional[Dict[str, Any]] = Field(default=None, description="Information about the model used")

class ClaimType(str, Enum):
    ORIGINAL = "original"
    REFINED = "refined"
    FINAL = "final"
class RefinementHistory(BaseModel):
    claim_type: ClaimType = Field(description="The type of claim")
    claim: Optional[str] = Field(default=None, description="The claim")
    score: float = Field(description="Score for the claim (0.0 to 1.0 scale)")
    feedback: Optional[str] = Field(default=None, description="The feedback from the refinement")

class RefinementMetadata(BaseModel):
    """Metadata about the claim refinement process."""
    metric_used: Optional[str] = Field(default=None, description="The metric that was used for refinement")
    threshold: Optional[float] = Field(default=None, description="The threshold that was used for refinement")
    refinement_model: Optional[str] = Field(default=None, description="The model that was used for refinement")
    refinement_history: List[RefinementHistory] = Field(description="History of the refinement process")

class ChatCompletionResponse(ChatCompletion):
    """Extended ChatCompletion with CheckThat AI evaluation and refinement data."""
    evaluation_report: Optional[EvaluationReport] = Field(
        default=None,
        description="Post-normalization evaluation results when requested"
    )
    refinement_metadata: Optional[RefinementMetadata] = Field(
        default=None,
        description="Metadata about claim refinement process when applied"
    )
    checkthat_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional CheckThat AI-specific metadata"
    )

class ParsedChatCompletionResponse(ParsedChatCompletion[ResponseFormatT]):
    """Extended ParsedChatCompletion with CheckThat AI evaluation and refinement data."""
    evaluation_report: Optional[EvaluationReport] = Field(
        default=None,
        description="Post-normalization evaluation results when requested"
    )
    refinement_metadata: Optional[RefinementMetadata] = Field(
        default=None,
        description="Metadata about claim refinement process when applied"
    )
    checkthat_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional CheckThat AI-specific metadata"
    )
    
from typing import Dict, List, Union, Iterable, Optional, Literal, Any
from typing_extensions import Required, TypedDict
from pydantic import BaseModel, Field
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.shared.chat_model import ChatModel

# Base parameters that both streaming and non-streaming requests share
class CompletionCreateParamsBase(TypedDict, total=False):
    messages: Required[Iterable[ChatCompletionMessageParam]]
    model: Required[Union[str, ChatModel]]
    
    # Optional OpenAI parameters (40+ fields)
    audio: Optional[Dict[str, Any]]
    frequency_penalty: Optional[float]
    function_call: Optional[Union[str, Dict[str, Any]]]
    functions: Optional[Iterable[Dict[str, Any]]]
    logit_bias: Optional[Dict[str, int]]
    logprobs: Optional[bool]
    max_completion_tokens: Optional[int]
    max_tokens: Optional[int]
    metadata: Optional[Dict[str, Any]]
    modalities: Optional[List[Literal["text", "audio"]]]
    n: Optional[int]
    parallel_tool_calls: Optional[bool]
    prediction: Optional[Dict[str, Any]]
    presence_penalty: Optional[float]
    prompt_cache_key: Optional[str]
    reasoning_effort: Optional[Literal["low", "medium", "high"]]
    response_format: Optional[Dict[str, Any]]
    safety_identifier: Optional[str]
    seed: Optional[int]
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]]
    stop: Optional[Union[str, List[str]]]
    store: Optional[bool]
    stream_options: Optional[Dict[str, Any]]
    temperature: Optional[float]
    tool_choice: Optional[Union[str, Dict[str, Any]]]
    tools: Optional[Iterable[Dict[str, Any]]]
    top_logprobs: Optional[int]
    top_p: Optional[float]
    user: Optional[str]
    verbosity: Optional[Literal["low", "medium", "high"]]
    web_search_options: Optional[Dict[str, Any]]
    
    # CheckThat AI custom parameters (always potentially present via extra_body)
    refine_claims: Optional[bool] = False
    refine_model: Optional[str] = None
    refine_threshold: Optional[float] = 0.5
    refine_max_iters: Optional[int] = 3
    refine_metrics: Optional[Any] = None
    checkthat_api_key: Optional[str]

# Non-streaming request
class CompletionCreateParamsNonStreaming(CompletionCreateParamsBase, total=False):
    stream: Optional[Literal[False]]

# Streaming request
class CompletionCreateParamsStreaming(CompletionCreateParamsBase):
    stream: Required[Literal[True]]

# Union type for all requests
CompletionCreateParams = Union[CompletionCreateParamsNonStreaming, CompletionCreateParamsStreaming]

# Alternative: Pydantic model for better validation (recommended)
class CheckThatCompletionCreateParams(BaseModel):
    # Required fields
    messages: List[Dict[str, Any]] = Field(description="List of messages comprising the conversation")
    model: str = Field(description="Model ID to use for completion")
    
    # Optional OpenAI fields
    audio: Optional[Dict[str, Any]] = None
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    function_call: Optional[Union[str, Dict[str, Any]]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    logit_bias: Optional[Dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_completion_tokens: Optional[int] = Field(default=None, ge=1)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    metadata: Optional[Dict[str, Any]] = None
    modalities: Optional[List[Literal["text", "audio"]]] = None
    n: Optional[int] = Field(default=None, ge=1, le=128)
    parallel_tool_calls: Optional[bool] = None
    prediction: Optional[Dict[str, Any]] = None
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    prompt_cache_key: Optional[str] = None
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None
    response_format: Optional[Dict[str, Any]] = None
    safety_identifier: Optional[str] = None
    seed: Optional[int] = None
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] = None
    stop: Optional[Union[str, List[str]]] = None
    store: Optional[bool] = None
    stream: Optional[bool] = Field(default=False, description="Whether to stream the response")
    stream_options: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    top_logprobs: Optional[int] = Field(default=None, ge=0, le=20)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    user: Optional[str] = None
    verbosity: Optional[Literal["low", "medium", "high"]] = None
    web_search_options: Optional[Dict[str, Any]] = None
    
    # CheckThat AI custom parameters
    refine_claims: Optional[bool] = None
    refine_model: Optional[str] = None
    refine_threshold: Optional[float] = None
    refine_max_iters: Optional[int] = None
    refine_metrics: Optional[Any] = None  
    checkthat_api_key: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields for forward compatibility
        arbitrary_types_allowed = True  # Allow DeepEval metric classes

_all_ = [CheckThatCompletionCreateParams, ChatCompletionResponse, ParsedChatCompletionResponse, Stream, ChatCompletionChunk]