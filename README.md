# Claim Extraction and Normalization

This project is a part of <a href="https://checkthat.gitlab.io/clef2025/task2/" rel="noopener nofollow ugc">CLEF-CheckThat! Lab's Task2 (2025)</a>. Given a noisy, unstructured social media post, the task is to simplify it into a concise form. This system leverages advanced AI models to transform complex, informal claims into clear, normalized statements suitable for fact-checking and analysis.

## 🎥 Demo Video 

https://github.com/user-attachments/assets/0363cfca-8a38-4abf-b04f-244f92cd878e

![Claim Normalization Demo](https://img.shields.io/badge/Status-Live%20Demo-brightgreen?style=for-the-badge)

## 🌐 Live Demo

- **🚀 Web Application**: [https://nikhil-kadapala.github.io/clef2025-checkthat-lab-task2/](https://nikhil-kadapala.github.io/clef2025-checkthat-lab-task2/)
- **⚡ API Backend**: Available via the web application interface
- **🐍 Python SDK**: In development - will be released soon for programmatic access

## 🚀 Features

### 💬 Web Application
- **Interactive Chat Interface**: Real-time claim normalization with streaming responses
- **Batch Evaluation**: Upload datasets for comprehensive evaluation with multiple models
- **Model Support**: GPT-4, Claude, Gemini, Llama, and Grok models
- **Real-time Progress**: WebSocket-based live evaluation tracking
- **Self-Refine & Cross-Refine**: Advanced refinement algorithms
- **METEOR Scoring**: Automatic evaluation with detailed metrics
- **Modern UI**: Responsive design with dark theme

### 🔌 API Features
- **RESTful Endpoints**: Clean API for claim normalization
- **WebSocket Support**: Real-time evaluation progress updates
- **Multiple Models**: Support for 8+ AI models
- **Streaming Responses**: Efficient real-time text generation
- **CORS Configured**: Ready for cross-origin requests

## 🧠 How It Works

The system follows a sophisticated pipeline to normalize social media claims:

1. **Input Processing**: Receives noisy, unstructured social media posts
2. **Model Selection**: Chooses from multiple AI models (GPT-4, Claude, Gemini, etc.)
3. **Normalization**: Applies selected prompting strategy:
   - **Zero-shot**: Direct claim normalization
   - **Few-shot**: Example-based learning
   - **Chain-of-Thought**: Step-by-step reasoning
   - **Self-Refine**: Iterative improvement process
   - **Cross-Refine**: Multi-model collaborative refinement
4. **Evaluation**: Automated METEOR scoring for quality assessment
5. **Output**: Clean, normalized claims ready for fact-checking

## 🛠️ Technology Stack

- **Frontend**: [React](https://reactjs.org/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/) + [Tailwind CSS](https://tailwindcss.com/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + [WebSocket](https://websockets.readthedocs.io/) + [Streaming](https://fastapi.tiangolo.com/advanced/streaming-response/)
- **AI Models**: [OpenAI GPT](https://openai.com/api/), [Anthropic Claude](https://www.anthropic.com/), [Google Gemini](https://ai.google.dev/), [Meta Llama](https://llama.meta.com/), [xAI Grok](https://grok.x.ai/)
- **Evaluation**: [METEOR](https://aclanthology.org/W05-0909/) scoring (nltk) with [pandas](https://pandas.pydata.org/) + [numpy](https://numpy.org/)
- **Deployment**: [GitHub Pages](https://pages.github.com/) + [Render](https://render.com/)

## 📋 Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **API Keys** for chosen models (OpenAI, Anthropic, Gemini, xAI)

## 🚀 Getting Started: Development and Local Testing

Follow these steps to get the application running locally for development and testing.

### Option 1: Automated Setup (Recommended)

The project includes automation scripts that handle the entire setup process:

#### ⚡ **Quick Start**
```bash
# 1. Clone the repository
git clone <repository-url>
cd clef2025-checkthat-lab-task2

# 2. Set up environment variables (see below)

# 3. Run automated setup
./setup-project.sh

# 4. Start the application
./run-project.sh
```

> **📝 Note**: You only need to run `./setup-project.sh` once for initial setup. After that, use `./run-project.sh` to start the application.

#### 🔧 **Environment Variables**
Set these before running the setup script:

```bash
# Linux/macOS:
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GEMINI_API_KEY="your-gemini-key"
export GROK_API_KEY="your-grok-key"

# Windows (PowerShell):
$env:OPENAI_API_KEY="your-openai-key"
$env:ANTHROPIC_API_KEY="your-anthropic-key"
$env:GEMINI_API_KEY="your-gemini-key"
$env:GROK_API_KEY="your-grok-key"
```

#### 📝 **What the Scripts Do**

**`setup-project.sh`**:
- ✅ Detects your OS (Linux/macOS/Windows)
- ✅ Terminates conflicting processes on port 5173
- ✅ Installs Node.js dependencies for the frontend
- ✅ Fixes npm vulnerabilities automatically
- ✅ Creates Python virtual environment
- ✅ Installs Python dependencies with `uv` (faster) or falls back to `pip`
- ✅ Handles cross-platform compatibility

**`run-project.sh`**:
- 🚀 Starts both frontend and backend simultaneously
- 🎯 Frontend runs on `http://localhost:5173`
- 🎯 Backend runs on `http://localhost:8000`
- 🛑 Graceful shutdown with `Ctrl+C`
- 📊 Shows process IDs for monitoring

### Option 2: Manual Setup

If you prefer manual setup or encounter issues with the scripts:

#### 1. Install Dependencies

**Backend:**
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt
```

**Frontend:**
```bash
cd src/app
npm install
```

#### 2. Run Development Servers

**Backend & Frontend:**
```bash
# Start both servers
./run-project.sh
```

_Alternatively, you can run them separately:_
```bash
# Terminal 1: Backend
cd src/api && python main.py

# Terminal 2: Frontend  
cd src/app && npm run dev
```

Open your browser and navigate to `http://localhost:5173` to see the application.

## 🤖 Supported Models

| Provider | Model | Free Tier | API Key Required |
|----------|-------|-----------|------------------|
| Together.ai | Llama 3.3 70B | ✅ | ❌ |
| OpenAI | GPT-4o, GPT-4.1 | ❌ | ✅ |
| Anthropic | Claude 3.7 Sonnet | ❌ | ✅ |
| Google | Gemini 2.5 Pro, Flash | ❌ | ✅ |
| xAI | Grok 3 | ❌ | ✅ |

## 📊 Evaluation Methods

- **Zero-shot**: Direct claim normalization
- **Few-shot**: Example-based learning  
- **Zero-shot-CoT**: Chain-of-thought reasoning
- **Few-shot-CoT**: Examples with reasoning
- **Self-Refine**: Iterative improvement
- **Cross-Refine**: Multi-model refinement

## 🧪 Example

```
Input: "The government is hiding something from us!"

Output: "Government transparency concerns have been raised by citizens regarding public information access."

METEOR Score: 0.847
```

## 🖥️ Usage

### Web Application
```bash
# Start both frontend and backend
./run-project.sh
```

Visit `http://localhost:5173` to access the interactive web interface.

### API Usage

#### Start the API Server
```bash
cd src/api
python main.py
```

#### Example API Call
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "The government is hiding something from us!",
    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
  }'
```

### CLI Tool (Legacy)
```bash
# Default usage (Llama 3.3 70B, Zero-shot)
python src/claim_norm.py

# Custom configuration
python src/claim_norm.py -m OpenAI -p Zero-Shot-CoT -it 1
```

## 🌐 Deployment

### Production Mode

For production deployment, you can run the application in production mode:

```bash
# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GEMINI_API_KEY="your-gemini-key" 
export GROK_API_KEY="your-grok-key"

# Build frontend for production
cd src/app
npm run build

# Start backend in production mode
cd ../api
python main.py
```

> **📝 Note**: Docker support is not currently implemented. The application runs natively using Python and Node.js.

### Frontend (GitHub Pages)
The frontend is automatically deployed to GitHub Pages:

1. Build: `npm run deploy`
2. Commit and push changes
3. GitHub Pages serves from `/docs` folder

### Backend (Cloud Hosting)
The FastAPI backend is deployed to a cloud hosting service with standard configuration:

- **Runtime**: Python FastAPI application
- **Environment**: Production environment with API keys configured
- **Features**: CORS enabled, WebSocket support, streaming responses

## 🔧 Development

### Project Architecture
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + WebSocket + Streaming
- **Evaluation**: METEOR scoring with pandas/numpy
- **Models**: Multiple AI providers with unified interface

### Code Quality
- TypeScript for type safety
- ESLint + Prettier for code formatting
- Python type hints
- Error handling and logging

## 🛠️ Troubleshooting

### Script Issues

#### Permission Denied
```bash
# Make scripts executable
chmod +x setup-project.sh run-project.sh
```

#### Windows Script Execution
```bash
# Use Git Bash or WSL
bash setup-project.sh
bash run-project.sh

# Or install WSL if not available
wsl --install
```

#### Port Already in Use
The scripts automatically handle port conflicts, but if you encounter issues:
```bash
# Kill processes on port 5173 (frontend)
# Linux/macOS:
lsof -ti:5173 | xargs kill -9

# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Kill processes on port 8000 (backend)
# Linux/macOS:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Common Issues

#### API Keys Not Working
- Ensure environment variables are set before running scripts
- Check for typos in environment variable names
- Verify API keys are valid and have sufficient quota

#### Frontend Build Errors
- Clear node_modules and reinstall dependencies
- Check Node.js version (requires v18+)
- Update npm to latest version: `npm install -g npm@latest`

#### Backend Import Errors
- Ensure virtual environment is activated
- Install missing dependencies: `pip install -r requirements.txt`
- Check Python version (requires v3.8+)

## 📁 Project Structure

```
clef2025-checkthat-lab-task2/
├── src/
│   ├── api/                        # FastAPI backend (deployed to Render)
│   │   └── main.py                 # Main API server with WebSocket support
│   ├── app/                        # Full-stack web application
│   │   ├── client/                 # React frontend application
│   │   │   ├── src/
│   │   │   │   ├── components/     # React components
│   │   │   │   ├── contexts/       # React contexts
│   │   │   │   ├── lib/           # Utility libraries
│   │   │   │   └── pages/         # Page components
│   │   │   └── index.html         # Main HTML template
│   │   ├── server/                 # Development server (Express + Vite)
│   │   ├── shared/                 # Shared types and utilities
│   │   │   ├── types.ts           # TypeScript type definitions
│   │   │   ├── prompts.ts         # Prompt templates
│   │   │   └── schema.ts          # Database schema
│   │   ├── vite.config.ts         # Vite configuration
│   │   └── package.json           # Frontend dependencies
│   ├── utils/                      # ML utilities and model interfaces
│   │   ├── evaluate.py            # Evaluation logic with METEOR scoring
│   │   ├── self_refine.py         # Self-refinement algorithms
│   │   ├── get_model_response.py  # Model API orchestration
│   │   ├── prompts.py             # Python prompt templates
│   │   ├── gpt.py                 # OpenAI GPT integration
│   │   ├── llama.py               # Llama model integration
│   │   ├── claude.py              # Anthropic Claude integration
│   │   ├── gemini.py              # Google Gemini integration
│   │   └── grok.py                # xAI Grok integration
│   ├── data/                       # Dataset results and cache
│   └── claim_norm.py              # CLI tool (legacy interface)
├── data/                          # Main datasets
│   ├── dev.csv                    # Development dataset
│   ├── test.csv                   # Test dataset
│   ├── dev_data.jsonl             # JSONL format development data
│   └── dev_data_fixed.jsonl       # Corrected development data
├── docs/                          # Production build (GitHub Pages)
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 📚 Citation

If you use this project in your research, please cite:

```bibtex
@misc{nkadapala-clef2025-checkthat-task2,
  title={Claim Extraction and Normalization for CLEF-CheckThat! Lab Task 2},
  author={Nikhil Kadapala},
  year={2025},
  url={https://github.com/nikhil-kadapala/clef2025-checkthat-lab-task2}
}
```



I'll help you build a comprehensive Python SDK for claim normalization with a refinement loop using DeepEval's G-Eval metric. Let me first explore your current codebase to understand the existing structure and then provide you with a detailed implementation plan.

[8 tools called]

Based on my analysis of your codebase, I can see you have a solid foundation with LLM integrations, claim normalization logic, and partial DeepEval integration. However, there's a syntax error in your `refine.py` file and several areas that need enhancement for a production-ready SDK. Here's my comprehensive implementation plan:

## 🎯 Implementation Plan: Claim Normalization SDK with DeepEval G-Eval

### Phase 1: Core SDK Architecture (Week 1)

#### 1.1 Fix Current Issues
First, let's fix the syntax error in `api/services/refine.py`:

```python
# Line 74-76 needs completion
if feedback is not None and feedback.score > 0.5:
    # Add refinement logic here
    refine_user_prompt = f"""
        ## Original Query
        {original_query}
        
        ## Current Response
        {current_claim}
        
        ## Feedback
        {feedback}
        
        ## Task
        Please refine the response based on the feedback provided.
    """
    current_claim = self._refine_claim(refine_user_prompt, self.refine_sys_prompt)
```

#### 1.2 SDK Core Structure
Create a new SDK module structure:

```
clef_claim_norm_sdk/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── normalizer.py         # Main ClaimNormalizer class
│   ├── refiner.py           # Enhanced refinement logic
│   ├── evaluator.py         # DeepEval G-Eval integration
│   └── session_manager.py   # Session and state management
├── models/
│   ├── __init__.py
│   ├── llm_providers.py     # LLM provider abstractions
│   ├── schemas.py           # Pydantic models
│   └── config.py            # Configuration management
├── utils/
│   ├── __init__.py
│   ├── decorators.py        # Custom decorators
│   ├── logging.py           # Structured logging
│   ├── metrics.py           # Performance metrics
│   └── exceptions.py        # Custom exceptions
├── api/
│   ├── __init__.py
│   ├── client.py            # SDK client interface
│   └── async_client.py      # Async client interface
└── examples/
    ├── basic_usage.py
    ├── advanced_refinement.py
    └── batch_processing.py
```

#### 1.3 Main SDK Client Interface

```python
# clef_claim_norm_sdk/api/client.py
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from ..core.normalizer import ClaimNormalizer
from ..core.refiner import ClaimRefiner
from ..core.evaluator import GEvalEvaluator
from ..models.config import SDKConfig, ModelConfig, RefinementConfig
from ..utils.decorators import retry, log_execution, monitor_performance

@dataclass
class ClaimResult:
    """Result container for claim processing"""
    original_claim: str
    normalized_claim: str
    confidence_score: float
    refinement_iterations: int
    evaluation_metrics: Dict[str, float]
    metadata: Dict[str, Any]

class ClaimNormalizationSDK:
    """
    Main SDK interface for claim normalization with refinement and evaluation.
    
    Example:
        >>> from clef_claim_norm_sdk import ClaimNormalizationSDK
        >>> sdk = ClaimNormalizationSDK(
        ...     model_provider="openai",
        ...     model_name="gpt-4",
        ...     api_key="your-api-key"
        ... )
        >>> result = sdk.normalize_claim("The government is hiding something!")
        >>> print(result.normalized_claim)
    """
    
    def __init__(
        self,
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        api_key: Optional[str] = None,
        config: Optional[SDKConfig] = None,
        **kwargs
    ):
        self.config = config or SDKConfig.from_dict(kwargs)
        self.normalizer = ClaimNormalizer(
            model_provider=model_provider,
            model_name=model_name,
            api_key=api_key
        )
        self.evaluator = GEvalEvaluator(
            model_provider=model_provider,
            model_name=model_name,
            api_key=api_key
        )
        self.refiner = ClaimRefiner(
            normalizer=self.normalizer,
            evaluator=self.evaluator,
            config=self.config.refinement
        )
    
    @retry(max_attempts=3, backoff_factor=2)
    @log_execution
    @monitor_performance
    def normalize_claim(
        self,
        claim: str,
        enable_refinement: bool = True,
        custom_criteria: Optional[List[str]] = None
    ) -> ClaimResult:
        """
        Normalize a single claim with optional refinement.
        
        Args:
            claim: Raw claim text to normalize
            enable_refinement: Whether to use refinement loop
            custom_criteria: Custom evaluation criteria for G-Eval
            
        Returns:
            ClaimResult with normalized claim and metrics
        """
        # Implementation here
        pass
    
    @log_execution
    @monitor_performance
    def normalize_batch(
        self,
        claims: List[str],
        batch_size: int = 10,
        enable_refinement: bool = True,
        progress_callback: Optional[callable] = None
    ) -> List[ClaimResult]:
        """
        Process multiple claims in batches.
        
        Args:
            claims: List of raw claims to normalize
            batch_size: Number of claims to process simultaneously
            enable_refinement: Whether to use refinement loop
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ClaimResult objects
        """
        # Implementation here
        pass
```

### Phase 2: Enhanced G-Eval Integration (Week 2)

#### 2.1 G-Eval Evaluator Implementation

```python
# clef_claim_norm_sdk/core/evaluator.py
from typing import List, Dict, Any, Optional
import asyncio
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.models import GPTModel, AnthropicModel, GeminiModel
from ..utils.decorators import async_retry, log_execution
from ..utils.exceptions import EvaluationError

class GEvalEvaluator:
    """
    G-Eval based evaluator for claim quality assessment.
    
    Supports multiple evaluation criteria and custom scoring.
    """
    
    DEFAULT_CRITERIA = [
        "Clarity: Is the claim clear and unambiguous?",
        "Verifiability: Can this claim be fact-checked with reliable sources?",
        "Specificity: Is the claim specific rather than vague?",
        "Neutrality: Is the claim presented in a neutral, factual manner?",
        "Completeness: Does the claim contain sufficient context to be understood?"
    ]
    
    def __init__(
        self,
        model_provider: str,
        model_name: str,
        api_key: str,
        criteria: Optional[List[str]] = None,
        threshold: float = 0.7
    ):
        self.model_provider = model_provider
        self.model_name = model_name
        self.api_key = api_key
        self.criteria = criteria or self.DEFAULT_CRITERIA
        self.threshold = threshold
        self._setup_model()
    
    def _setup_model(self):
        """Initialize the evaluation model based on provider"""
        if self.model_provider.lower() == "openai":
            self.model = GPTModel(model=self.model_name, api_key=self.api_key)
        elif self.model_provider.lower() == "anthropic":
            self.model = AnthropicModel(model=self.model_name, api_key=self.api_key)
        elif self.model_provider.lower() == "gemini":
            self.model = GeminiModel(model=self.model_name, api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    @async_retry(max_attempts=3)
    @log_execution
    async def evaluate_claim_quality(
        self,
        original_claim: str,
        normalized_claim: str,
        custom_criteria: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Evaluate normalized claim quality using G-Eval.
        
        Args:
            original_claim: Original raw claim
            normalized_claim: Processed claim to evaluate
            custom_criteria: Override default evaluation criteria
            
        Returns:
            Dictionary with evaluation scores
        """
        try:
            criteria = custom_criteria or self.criteria
            evaluation_results = {}
            
            for criterion in criteria:
                metric = GEval(
                    name=f"Claim_Quality_{criterion.split(':')[0]}",
                    criteria=criterion,
                    evaluation_params=[
                        LLMTestCaseParams.INPUT,
                        LLMTestCaseParams.ACTUAL_OUTPUT
                    ],
                    model=self.model
                )
                
                test_case = LLMTestCase(
                    input=original_claim,
                    actual_output=normalized_claim
                )
                
                # Run evaluation
                await metric.a_measure(test_case)
                
                criterion_name = criterion.split(':')[0].lower()
                evaluation_results[criterion_name] = metric.score
            
            # Calculate overall score
            evaluation_results['overall_score'] = sum(evaluation_results.values()) / len(evaluation_results)
            
            return evaluation_results
            
        except Exception as e:
            raise EvaluationError(f"G-Eval evaluation failed: {str(e)}")
    
    def meets_threshold(self, scores: Dict[str, float]) -> bool:
        """Check if evaluation scores meet the quality threshold"""
        return scores.get('overall_score', 0) >= self.threshold
```

#### 2.2 Enhanced Refinement Loop

```python
# clef_claim_norm_sdk/core/refiner.py
from typing import Optional, Dict, Any, List
import asyncio
from ..models.config import RefinementConfig
from ..utils.decorators import log_execution, monitor_performance
from ..utils.exceptions import RefinementError

class ClaimRefiner:
    """
    Advanced claim refinement with G-Eval feedback loop.
    """
    
    def __init__(
        self,
        normalizer,
        evaluator,
        config: RefinementConfig
    ):
        self.normalizer = normalizer
        self.evaluator = evaluator
        self.config = config
    
    @log_execution
    @monitor_performance
    async def refine_claim(
        self,
        original_claim: str,
        initial_normalized: str,
        custom_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Refine claim through iterative G-Eval feedback.
        
        Args:
            original_claim: Original raw claim
            initial_normalized: Initial normalization attempt
            custom_criteria: Custom evaluation criteria
            
        Returns:
            Dictionary with final claim and refinement metadata
        """
        current_claim = initial_normalized
        iteration = 0
        refinement_history = []
        
        while iteration < self.config.max_iterations:
            # Evaluate current claim
            scores = await self.evaluator.evaluate_claim_quality(
                original_claim, current_claim, custom_criteria
            )
            
            refinement_history.append({
                'iteration': iteration,
                'claim': current_claim,
                'scores': scores
            })
            
            # Check if quality threshold is met
            if self.evaluator.meets_threshold(scores):
                break
            
            # Generate refinement feedback
            feedback = self._generate_feedback(scores, original_claim, current_claim)
            
            # Apply refinement
            refined_claim = await self.normalizer.refine_with_feedback(
                original_claim, current_claim, feedback
            )
            
            current_claim = refined_claim
            iteration += 1
        
        return {
            'final_claim': current_claim,
            'iterations': iteration,
            'final_scores': scores,
            'history': refinement_history,
            'converged': self.evaluator.meets_threshold(scores)
        }
    
    def _generate_feedback(
        self,
        scores: Dict[str, float],
        original_claim: str,
        current_claim: str
    ) -> str:
        """Generate specific feedback based on G-Eval scores"""
        feedback_parts = []
        
        for criterion, score in scores.items():
            if criterion == 'overall_score':
                continue
                
            if score < self.config.improvement_threshold:
                feedback_parts.append(
                    f"Improve {criterion}: Current score {score:.2f} is below threshold. "
                    f"Focus on making the claim more {criterion.lower()}."
                )
        
        return "\n".join(feedback_parts)
```

### Phase 3: Production-Ready Features (Week 3)

#### 3.1 Configuration Management

```python
# clef_claim_norm_sdk/models/config.py
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from enum import Enum

class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    XAI = "xai"

class RefinementConfig(BaseModel):
    """Configuration for refinement process"""
    max_iterations: int = Field(default=3, ge=1, le=10)
    improvement_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    convergence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    early_stopping: bool = True

class SDKConfig(BaseModel):
    """Main SDK configuration"""
    # Model settings
    model_provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "gpt-4"
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1)
    
    # Refinement settings
    refinement: RefinementConfig = Field(default_factory=RefinementConfig)
    
    # Evaluation settings
    evaluation_criteria: Optional[List[str]] = None
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Performance settings
    request_timeout: int = Field(default=30, ge=1)
    max_retries: int = Field(default=3, ge=0, le=10)
    batch_size: int = Field(default=10, ge=1, le=100)
    
    # Logging and monitoring
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SDKConfig':
        """Create config from dictionary"""
        return cls(**config_dict)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'SDKConfig':
        """Load config from YAML/JSON file"""
        import json
        import yaml
        from pathlib import Path
        
        path = Path(config_path)
        if path.suffix.lower() == '.json':
            with open(path) as f:
                config_dict = json.load(f)
        elif path.suffix.lower() in ['.yml', '.yaml']:
            with open(path) as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")
        
        return cls.from_dict(config_dict)
```

#### 3.2 Custom Decorators and Utilities

```python
# clef_claim_norm_sdk/utils/decorators.py
import functools
import time
import asyncio
import logging
from typing import Any, Callable, Optional
from .exceptions import RetryExhaustedError, SDKError
from .metrics import performance_monitor

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, backoff_factor: float = 2, exceptions: tuple = (Exception,)):
    """Retry decorator with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            raise RetryExhaustedError(f"Failed after {max_attempts} attempts") from last_exception
        return wrapper
    return decorator

def async_retry(max_attempts: int = 3, backoff_factor: float = 2, exceptions: tuple = (Exception,)):
    """Async retry decorator with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            raise RetryExhaustedError(f"Failed after {max_attempts} attempts") from last_exception
        return wrapper
    return decorator

def log_execution(func: Callable) -> Callable:
    """Log function execution with timing"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {execution_time:.2f}s: {e}")
            raise
    return wrapper

def monitor_performance(func: Callable) -> Callable:
    """Monitor function performance metrics"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return performance_monitor.track_execution(func, *args, **kwargs)
    return wrapper

def validate_inputs(**validation_rules):
    """Validate function inputs"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Perform validation based on rules
            for param_name, rule in validation_rules.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if not rule(value):
                        raise ValueError(f"Invalid value for {param_name}: {value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Phase 4: API and Distribution (Week 4)

#### 4.1 API Client for Remote Usage

```python
# clef_claim_norm_sdk/api/async_client.py
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from ..models.schemas import ClaimResult, BatchProcessRequest
from ..utils.exceptions import APIError

class AsyncClaimNormalizationClient:
    """
    Async client for remote API access to claim normalization service.
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def normalize_claim(
        self,
        claim: str,
        enable_refinement: bool = True,
        custom_criteria: Optional[List[str]] = None
    ) -> ClaimResult:
        """Normalize a single claim via API"""
        url = f"{self.base_url}/api/v1/normalize"
        
        payload = {
            "claim": claim,
            "enable_refinement": enable_refinement,
            "custom_criteria": custom_criteria
        }
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return ClaimResult(**data)
            else:
                error_msg = await response.text()
                raise APIError(f"API request failed: {response.status} - {error_msg}")
    
    async def normalize_batch_stream(
        self,
        claims: List[str],
        batch_size: int = 10,
        enable_refinement: bool = True
    ) -> AsyncGenerator[ClaimResult, None]:
        """Stream batch normalization results"""
        url = f"{self.base_url}/api/v1/normalize/batch/stream"
        
        payload = {
            "claims": claims,
            "batch_size": batch_size,
            "enable_refinement": enable_refinement
        }
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                async for line in response.content:
                    if line:
                        data = await response.json()
                        yield ClaimResult(**data)
            else:
                error_msg = await response.text()
                raise APIError(f"Stream request failed: {response.status} - {error_msg}")
```

#### 4.2 Package Setup for Distribution

```python
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clef-claim-norm-sdk",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@domain.com",
    description="Professional SDK for claim normalization with G-Eval refinement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/clef-claim-norm-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "ruff>=0.0.200",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clef-claim-norm=clef_claim_norm_sdk.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "clef_claim_norm_sdk": ["data/*.json", "templates/*.txt"],
    },
)
```

### Phase 5: Testing and Quality Assurance

#### 5.1 Comprehensive Testing Suite

```python
# tests/test_sdk_integration.py
import pytest
import asyncio
from clef_claim_norm_sdk import ClaimNormalizationSDK
from clef_claim_norm_sdk.models.config import SDKConfig, RefinementConfig

@pytest.mark.asyncio
class TestSDKIntegration:
    
    @pytest.fixture
    def sdk_config(self):
        return SDKConfig(
            model_provider="openai",
            model_name="gpt-4",
            refinement=RefinementConfig(
                max_iterations=2,
                improvement_threshold=0.6
            )
        )
    
    @pytest.fixture
    def sdk(self, sdk_config):
        return ClaimNormalizationSDK(
            config=sdk_config,
            api_key="test-api-key"
        )
    
    async def test_single_claim_normalization(self, sdk):
        """Test basic claim normalization"""
        result = await sdk.normalize_claim(
            "The government is hiding alien technology!"
        )
        
        assert result.normalized_claim
        assert result.confidence_score >= 0
        assert result.refinement_iterations >= 0
        assert 'overall_score' in result.evaluation_metrics
    
    async def test_batch_processing(self, sdk):
        """Test batch claim processing"""
        claims = [
            "The government is hiding alien technology!",
            "COVID vaccines contain microchips",
            "Climate change is a hoax"
        ]
        
        results = await sdk.normalize_batch(claims, batch_size=2)
        
        assert len(results) == len(claims)
        for result in results:
            assert result.normalized_claim
            assert isinstance(result.evaluation_metrics, dict)
    
    async def test_custom_criteria(self, sdk):
        """Test custom evaluation criteria"""
        custom_criteria = [
            "Scientific accuracy: Is the claim scientifically plausible?",
            "Evidence requirement: Does the claim require specific evidence?"
        ]
        
        result = await sdk.normalize_claim(
            "Water boils at 100°C at sea level",
            custom_criteria=custom_criteria
        )
        
        assert 'scientific_accuracy' in result.evaluation_metrics
        assert 'evidence_requirement' in result.evaluation_metrics
```

### Summary and Next Steps

This implementation plan provides:

1. **🏗️ Robust Architecture**: Modular design with clear separation of concerns
2. **🔧 Industry Standards**: Proper decorators, error handling, logging, and monitoring
3. **📊 G-Eval Integration**: Comprehensive evaluation with custom criteria support
4. **🔄 Advanced Refinement**: Iterative improvement loop with convergence detection
5. **🌐 API Ready**: Both local SDK and remote API client capabilities
6. **📦 Distribution Ready**: Proper packaging for PyPI publication
7. **🧪 Testing Coverage**: Comprehensive test suite for reliability
8. **📚 Documentation**: Clear examples and API documentation

**Implementation Timeline**: 4 weeks to complete all phases

**Next Immediate Steps**:
1. Fix the syntax error in `refine.py`
2. Set up the new SDK project structure
3. Implement the core `ClaimNormalizer` class
4. Integrate G-Eval evaluation
5. Create comprehensive tests

Would you like me to start implementing any specific component, or would you prefer to discuss any aspects of this plan in more detail?