# Claim Normalization API - Modular Structure

This is a refactored version of the Claim Normalization API using a modular FastAPI structure for better organization, maintainability, and SDK development.

## 📁 Project Structure

```
src/api/
├── main_new.py                # New modular FastAPI application entry point
├── requirements.txt           # API-specific dependencies
├── core/                      # Core configuration and setup
│   ├── config.py             # Application settings and configuration
│   ├── middleware.py         # CORS and other middleware setup
│   └── __init__.py
├── models/                    # Pydantic models
│   ├── requests.py           # Request models (ChatRequest, EvaluationStartRequest, etc.)
│   ├── responses.py          # Response models (HealthCheck, ChatResponse, etc.)
│   └── __init__.py
├── routes/                    # API route modules
│   ├── health.py             # Health check endpoints
│   ├── chat.py               # Chat interface endpoints
│   ├── evaluation.py         # WebSocket evaluation endpoints
│   └── __init__.py           # Router aggregation
└── services/                  # Business logic services
    ├── evaluation_service.py  # Evaluation business logic
    ├── websocket_manager.py   # WebSocket connection management
    └── __init__.py
```

## 🚀 Benefits of This Structure

### 1. **Separation of Concerns**
- **Routes**: Handle HTTP/WebSocket requests and responses
- **Services**: Contain business logic and data processing
- **Models**: Define data structures and validation
- **Core**: Manage configuration and application setup

### 2. **SDK-Friendly Design**
- Clear API contracts defined in `models/`
- Consistent response formats
- Easy to generate SDK clients from OpenAPI schema
- Modular endpoints for different functionalities

### 3. **Maintainability**
- Each module has a single responsibility
- Easy to locate and modify specific functionality
- Better testing capabilities (unit tests per module)
- Reduced coupling between components

### 4. **Scalability**
- Easy to add new endpoints by creating new route modules
- Services can be easily extracted to microservices later
- Configuration is centralized and environment-aware

## 🔧 Migration Guide

### From `main.py` to Modular Structure

1. **Health endpoints** → `routes/health.py`
2. **Chat functionality** → `routes/chat.py` + `services/chat_service.py`
3. **WebSocket evaluation** → `routes/evaluation.py` + `services/evaluation_service.py`
4. **Global state management** → `services/websocket_manager.py`
5. **Configuration** → `core/config.py`
6. **CORS setup** → `core/middleware.py`

### Running the New Structure

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.api.main_new

# Or with uvicorn directly
uvicorn src.api.main_new:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API Endpoints

### Health Endpoints
- `GET /` - Root health check
- `GET /health` - Detailed health status

### Chat Endpoints  
- `POST /chat` - Stream chat responses for claim normalization

### Evaluation Endpoints
- `WebSocket /ws/evaluation/{session_id}` - Real-time evaluation with progress updates

## 🔗 SDK Development Benefits

This structure provides several advantages for SDK development:

1. **Clear Type Definitions**: All request/response models are defined in `models/`
2. **Consistent Error Handling**: Standardized error responses
3. **OpenAPI Schema**: Automatically generated and well-structured
4. **Modular Clients**: Can generate separate client classes for each route module
5. **Environment Configuration**: Easy to adapt for different environments

## 🧪 Testing Structure

```
tests/
├── test_health.py           # Health endpoint tests
├── test_chat.py             # Chat functionality tests
├── test_evaluation.py       # Evaluation WebSocket tests
├── test_services/           # Service layer tests
│   ├── test_evaluation_service.py
│   └── test_websocket_manager.py
└── conftest.py              # Test configuration and fixtures
```

## ⚙️ Configuration

Environment variables are managed through `core/config.py`:

```python
# Development
ENV_TYPE=dev

# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
# ... etc
```

## 🔄 Backward Compatibility

The new structure maintains the same API contracts as the original `main.py`, ensuring existing clients continue to work without modifications. 