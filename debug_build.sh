#!/bin/bash

# Debug build script - captures all output and keeps terminal open
set -e

echo "Debug build for Expense Tracker AppImage..."
echo "Logging all output to build.log"

# Set version
export VERSION=${VERSION:-1.0.0}

# Function to log and display
log_and_show() {
    echo "$1" | tee -a build.log
}

# Clear previous log
> build.log

log_and_show "=== Starting debug build at $(date) ==="

# Check Python version
log_and_show "Python version: $(python3 --version)"

# Check if appimage-builder is installed
if command -v appimage-builder &> /dev/null; then
    log_and_show "appimage-builder found: $(which appimage-builder)"
    log_and_show "appimage-builder version: $(appimage-builder --version 2>&1 || echo 'version check failed')"
else
    log_and_show "ERROR: appimage-builder not found!"
    log_and_show "Run ./build_appimage.sh first to install dependencies"
    exit 1
fi

# Check required files
log_and_show "=== Checking required files ==="
for file in expense_tracker.py run_app.py requirements.txt AppImageBuilder.yml expense_tracker.desktop; do
    if [ -f "$file" ]; then
        log_and_show "✓ $file exists"
    else
        log_and_show "✗ $file missing!"
    fi
done

if [ -d "static" ]; then
    log_and_show "✓ static directory exists"
    log_and_show "  Files in static/: $(ls static/)"
else
    log_and_show "⚠ static directory missing (may cause issues)"
fi

# Clean previous build
log_and_show "=== Cleaning previous build ==="
rm -rf AppDir *.AppImage 2>&1 | tee -a build.log || true

# Show system info
log_and_show "=== System information ==="
log_and_show "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
log_and_show "Architecture: $(uname -m)"
log_and_show "Available space: $(df -h . | tail -1 | awk '{print $4}')"

# Run appimage-builder with verbose output
log_and_show "=== Starting AppImage build ==="
log_and_show "Command: appimage-builder --recipe AppImageBuilder.yml"

# Capture ALL output including errors
exec > >(tee -a build.log)
exec 2>&1

if appimage-builder --recipe AppImageBuilder.yml; then
    log_and_show "=== BUILD SUCCESSFUL ==="
    log_and_show "AppImage created: $(ls *.AppImage 2>/dev/null || echo 'AppImage file not found')"
    log_and_show "File size: $(ls -lh *.AppImage 2>/dev/null | awk '{print $5}' || echo 'unknown')"
else
    log_and_show "=== BUILD FAILED ==="
    log_and_show "Exit code: $?"
    log_and_show ""
    log_and_show "Full build log saved to build.log"
    log_and_show "Common solutions:"
    log_and_show "1. Check if all dependencies are installed"
    log_and_show "2. Verify Python version compatibility"
    log_and_show "3. Ensure static files exist"
    log_and_show "4. Check available disk space"
fi

echo ""
echo "=== Build complete ==="
echo "Full log saved to: build.log"
echo "Press Enter to exit..."
read