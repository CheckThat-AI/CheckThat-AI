#!/bin/bash
# setup-project.sh
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

# Install Node.js dependencies for the app
echo "Installing Node.js dependencies..."
cd "$APP_DIR"

# Clear npm cache and remove node_modules to avoid conflicts
npm cache clean --force

# Run npm install and check for errors
if ! npm install && npm install cors; then
    echo "Error: npm install failed. Check for permission issues, file locks (e.g., antivirus, running processes), or network connectivity."
    exit 1
fi

# Address vulnerabilities
echo "Checking for vulnerabilities in Node.js dependencies..."
if npm audit 2>/dev/null | grep -q "found"; then
    echo "Vulnerabilities found. Running npm audit fix..."
    npm audit fix 2>/dev/null || {
        echo "Warning: npm audit fix failed. Consider running 'npm audit fix --force' manually to address all issues (may include breaking changes)."
    }
fi

# Check for deprecated packages and replace with tsx
echo "Checking for deprecated @esbuild-kit packages..."
if npm ls @esbuild-kit/esm-loader @esbuild-kit/core-utils 2>/dev/null | grep -q "@esbuild-kit"; then
    echo "Deprecated @esbuild-kit packages found. Replacing with tsx..."
    npm uninstall @esbuild-kit/esm-loader @esbuild-kit/core-utils
    npm install tsx || {
        echo "Warning: Failed to install tsx. You may need to update your package.json manually to use tsx instead of @esbuild-kit packages."
    }
fi

cd "$SCRIPT_DIR"

# Install uv and create virtual environment
echo "Setting up Python virtual environment..."
if ! pip install uv; then
    echo "Error: Failed to install uv. Ensure pip is installed and try again."
    exit 1
fi

if ! python -m venv .venv; then
    echo "Error: Failed to create virtual environment with pip venv. Ensure Python and pip are installed correctly."
    exit 1
fi

# Activate virtual environment based on OS
echo "Activating virtual environment..."
if [ "$OS" = "windows" ]; then
    # Windows activation path
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    else
        echo "Error: Windows virtual environment activation script not found"
        exit 1
    fi
else
    # Unix-like activation path (Linux, Mac, Replit)
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo "Error: Unix virtual environment activation script not found"
        exit 1
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found in $SCRIPT_DIR. Please create it with the necessary dependencies (e.g., fastapi[standard])."
    exit 1
fi

# Try uv pip install, fall back to pip if it fails
if ! uv pip install -r requirements.txt; then
    echo "Warning: uv pip install failed. Falling back to pip..."
    if ! pip install -r requirements.txt; then
        echo "Error: Failed to install Python dependencies with both uv and pip. Check requirements.txt for errors."
        exit 1
    fi
fi


