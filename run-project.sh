#!/bin/bash
# run-project.sh
set -e  # Exit on error

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define directories
APP_DIR="$SCRIPT_DIR/src/app"
API_DIR="$SCRIPT_DIR/src/api"

# Detect the operating system
detect_os() {
    case "$OSTYPE" in
        linux-gnu*) echo "linux" ;;
        darwin*) echo "mac" ;;
        cygwin*|msys*|mingw*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

OS=$(detect_os)
echo "Detected OS: $OS"

# Check if directories exist
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Directory $APP_DIR does not exist. Please check the project structure."
    exit 1
fi

if [ ! -d "$API_DIR" ]; then
    echo "Error: Directory $API_DIR does not exist. Please check the project structure."
    exit 1
fi

# Check for running Node.js processes and terminate them
echo "Checking for running Node.js processes..."

if [ "$OS" = "windows" ]; then
    # Windows environment
    if netstat -ano | grep 5173 >/dev/null 2>&1; then
        echo "Port 5173 is in use. Attempting to terminate Node.js processes..."
        taskkill /IM node.exe /F 2>/dev/null || echo "Warning: Could not terminate Node.js processes. Please close them manually."
    fi
elif [ "$OS" = "linux" ] || [ "$OS" = "mac" ]; then
    # Unix-like environment (including Replit)
    if command -v lsof >/dev/null 2>&1; then
        if lsof -ti:5173 >/dev/null 2>&1; then
            echo "Port 5173 is in use. Attempting to terminate processes..."
            lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "Warning: Could not terminate processes on port 5173."
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tulpn | grep :5173 >/dev/null 2>&1; then
            echo "Port 5173 is in use. Attempting to find and terminate processes..."
            pkill -f "node.*5173" 2>/dev/null || echo "Warning: Could not terminate Node.js processes."
        fi
    else
        echo "Warning: Cannot check for running processes (no lsof or ss command available)"
    fi
fi

# Function to start processes based on OS
start_services() {
    echo "Starting the App..."
    
    # Start frontend
    echo "Starting frontend..."
    cd "$APP_DIR" && npm run dev &
    FRONTEND_PID=$!
    
    # Start backend
    echo "Starting backend..."
    cd "$API_DIR" && fastapi dev main.py --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Store PIDs for cleanup
    echo "Frontend PID: $FRONTEND_PID"
    echo "Backend PID: $BACKEND_PID"
}

# Start the services
start_services

# Keep the script running to allow monitoring
echo "Frontend running on http://localhost:5173"
echo "Backend running on http://localhost:8000"
echo "Press Ctrl+C to stop..."

# Handle cleanup on script termination
cleanup() {
    echo "Stopping services..."
    if [ "$OS" != "windows" ] && [ -n "$FRONTEND_PID" ] && [ -n "$BACKEND_PID" ]; then
        kill $FRONTEND_PID $BACKEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup INT TERM

# Wait for background processes
wait