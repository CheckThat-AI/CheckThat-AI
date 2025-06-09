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
