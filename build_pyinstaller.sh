#!/bin/bash

# Build script using PyInstaller (more reliable than AppImage)
set -e

echo "Building Expense Tracker using PyInstaller..."

# Set version
export VERSION=${VERSION:-1.0.0}

# Detect the Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    else
        echo "unknown"
    fi
}

# Install PyInstaller if not present
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install --user pyinstaller
fi

# Install app dependencies
echo "Installing application dependencies..."
pip3 install --user -r requirements.txt

# Clean previous build
rm -rf dist build *.spec || true

# Create the executable
echo "Creating standalone executable..."
python3 -m PyInstaller \
    --onefile \
    --name "expense-tracker" \
    --add-data "static:static" \
    --hidden-import "streamlit" \
    --hidden-import "plotly" \
    --hidden-import "pandas" \
    --hidden-import "sqlite3" \
    --hidden-import "dateutil" \
    run_app.py

if [ -f "dist/expense-tracker" ]; then
    echo "Build successful!"
    echo "Executable created: dist/expense-tracker"
    echo "File size: $(ls -lh dist/expense-tracker | awk '{print $5}')"
    echo ""
    echo "To run: ./dist/expense-tracker"
    echo "Or copy to /usr/local/bin for system-wide access"
else
    echo "Build failed - no executable found in dist/"
    exit 1
fi