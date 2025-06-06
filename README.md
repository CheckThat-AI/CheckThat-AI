# Claim Extraction and Normalization

This project is a part of <a href="https://checkthat.gitlab.io/clef2025/task2/" rel="noopener nofollow ugc">CLEF-CheckThat! Lab's Task2 (2025)</a>. Given a noisy, unstructured social media post, the task is to simplify it into a concise form. This is a text generation task in which systems have to generate the normalized claims for the given social media posts.

## 🌐 Live Demo

- **Web Application**: [https://nikhil-kadapala.github.io/clef2025-checkthat-lab-task2/](https://nikhil-kadapala.github.io/clef2025-checkthat-lab-task2/)
- **API Backend**: [https://claim-normalization.onrender.com/](https://claim-normalization.onrender.com/)

## Project Structure

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

## 🚀 Features

### Web Application
- **Interactive Chat Interface**: Real-time claim normalization with streaming responses
- **Batch Evaluation**: Upload datasets for comprehensive evaluation with multiple models
- **Model Support**: GPT-4, Claude, Gemini, Llama, and Grok models
- **Real-time Progress**: WebSocket-based live evaluation tracking
- **Self-Refine & Cross-Refine**: Advanced refinement algorithms
- **METEOR Scoring**: Automatic evaluation with detailed metrics
- **Modern UI**: Responsive design with dark theme

### API Features
- **RESTful Endpoints**: Clean API for claim normalization
- **WebSocket Support**: Real-time evaluation progress updates
- **Multiple Models**: Support for 8+ AI models
- **Streaming Responses**: Efficient real-time text generation
- **CORS Configured**: Ready for cross-origin requests

## 📋 Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **API Keys** for chosen models (OpenAI, Anthropic, Google AI, xAI)

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd clef2025-checkthat-lab-task2
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt
# Or use uv for faster installation:
# pip install uv && uv pip install -r requirements.txt

# Set environment variables
# Linux/macOS:
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GEMINI_API_KEY="your-gemini-key"
export GROQ_API_KEY="your-grok-key"

# Windows:
$env:OPENAI_API_KEY="your-openai-key"
$env:ANTHROPIC_API_KEY="your-anthropic-key"
$env:GEMINI_API_KEY="your-gemini-key"
$env:GROQ_API_KEY="your-grok-key"
```

### 3. Frontend Setup
```bash
cd src/app
npm install
```

## 🖥️ Usage

### Web Application (Recommended)

#### Development Mode
```bash
# Terminal 1: Start the backend
cd src/api
python main.py

# Terminal 2: Start the frontend
cd src/app
npm run dev
```

Visit `http://localhost:5173` to access the web application.

#### Production Build
```bash
cd src/app
npm run deploy
```

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

# Help
python src/claim_norm.py -h
```

## 🌐 Deployment

### Frontend (GitHub Pages)
The frontend is automatically deployed to GitHub Pages from the `docs/` directory.

1. Build the frontend: `npm run deploy`
2. Commit and push changes
3. GitHub Pages serves from `/docs` folder

### Backend (Render)
The FastAPI backend is deployed to Render.

**Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables**:
- `ENV_TYPE=prod`
- `OPENAI_API_KEY=your-key`
- `ANTHROPIC_API_KEY=your-key`
- `GEMINI_API_KEY=your-key`
- `GROK_API_KEY=your-key`

## 🤖 Supported Models

| Provider | Model | Free Tier |
|----------|-------|-----------|
| Together.ai | Llama 3.3 70B | ✅ |
| OpenAI | GPT-4o, GPT-4.1 | ❌ |
| Anthropic | Claude 3.7 Sonnet | ❌ |
| Google | Gemini 2.5 Pro/Flash | ❌ |
| xAI | Grok 3 | ❌ |

## 📊 Evaluation Methods

- **Zero-shot**: Direct claim normalization
- **Few-shot**: Example-based learning
- **Zero-shot-CoT**: Chain-of-thought reasoning
- **Few-shot-CoT**: Examples with reasoning
- **Self-Refine**: Iterative improvement
- **Cross-Refine**: Multi-model refinement

## 🧪 Example Output

```
Initial Claim: "The government is hiding something from us!"

Normalized Claim: "Government transparency concerns have been raised by citizens regarding public information access."

METEOR Score: 0.847
```

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

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for more details.

## 📚 Citation

If you use this project in your research, please cite:

```bibtex
@misc{nkadapala-clef2025-checkthat-task2,
  title={Claim Extraction and Normalization for CLEF-CheckThat! Lab Task 2},
  author={Nikhil Kadapala},
  year={2025},
  url={https://github.com/your-username/clef2025-checkthat-lab-task2}
}
```