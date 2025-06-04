#!/bin/bash
# run-project.sh
set -e  # Exit on error

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define directories
APP_DIR="$SCRIPT_DIR/src/app"
API_DIR="$SCRIPT_DIR/src/api"

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
if netstat -ano | grep 5173 >/dev/null; then
echo "Port 5173 is in use. Attempting to terminate Node.js processes..."
taskkill /IM node.exe /F || echo "Warning: Could not terminate Node.js processes. Please close them manually."
fi

# Install Node.js dependencies for the app
echo "Installing Node.js dependencies..."
cd "$APP_DIR"

# Clear npm cache and remove node_modules to avoid conflicts
npm cache clean --force
if [ -d "node_modules" ]; then
rm -rf node_modules || {
echo "Error: Failed to delete node_modules. Try running this script as Administrator."
exit 1
}
fi

# Run npm install and check for errors
if ! npm install; then
echo "Error: npm install failed. Try running this script as Administrator or check for file locks (e.g., antivirus, running processes)."
exit 1
fi

# Address vulnerabilities
echo "Checking for vulnerabilities in Node.js dependencies..."
if npm audit | grep -q "found"; then
echo "Vulnerabilities found. Running npm audit fix..."
npm audit fix || {
echo "Warning: npm audit fix failed. Consider running 'npm audit fix --force' manually to address all issues (may include breaking changes)."
}
fi
cd "$SCRIPT_DIR"

# Install uv and create virtual environment
echo "Setting up Python virtual environment..."
pip install uv
uv venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/Scripts/activate

# Install Python dependencies
echo "Installing Python dependencies..."
# pip install -r requirements.txt
uv pip install -r requirements.txt

# Run frontend and backend in parallel
echo "Starting frontend and backend..."

# Start frontend (npm run dev)
cd "$APP_DIR" && npm run dev &

# Start backend (fastapi dev)
cd "$API_DIR" && fastapi dev main.py &

# Keep the script running to allow monitoring
echo "Frontend running on http://localhost:5173"
echo "Backend running on http://localhost:8000"
echo "Press Ctrl+C to stop..."
wait