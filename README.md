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

### Option 1: Automated Setup (Recommended)

The project includes automation scripts that handle the entire setup process:

#### 🚀 **Quick Start**
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

# Windows (Command Prompt):
set OPENAI_API_KEY=your-openai-key
set ANTHROPIC_API_KEY=your-anthropic-key
set GEMINI_API_KEY=your-gemini-key
set GROK_API_KEY=your-grok-key
```

#### 🪟 **Windows Users**
On Windows, run the scripts using Git Bash or WSL:
```bash
# In Git Bash or WSL
bash setup-project.sh
bash run-project.sh
```

### Option 2: Manual Setup

If you prefer manual setup or encounter issues with the scripts:

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd clef2025-checkthat-lab-task2
```

#### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
# Or use uv for faster installation:
# pip install uv && uv pip install -r requirements.txt
```

#### 3. Frontend Setup
```bash
cd src/app
npm install
```

## 🖥️ Usage

### Option 1: Using Automation Scripts (Easiest)

```bash
# Start both frontend and backend
./run-project.sh
```

This will automatically:
- Start the backend on `http://localhost:8000`
- Start the frontend on `http://localhost:5173`
- Show both URLs for easy access
- Allow graceful shutdown with `Ctrl+C`

### Option 2: Manual Start (Alternative)

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

#### Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Node.js Dependency Issues
```bash
# Clear npm cache and reinstall
cd src/app
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
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