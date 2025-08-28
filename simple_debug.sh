#!/bin/bash

echo "Simple debug build - catching ALL output..."
echo "========================================"

# Set version
export VERSION=${VERSION:-1.0.0}

# Run the command and capture everything to both screen and file
{
    echo "Starting build at $(date)"
    echo "Working directory: $(pwd)"
    echo "Python version: $(python3 --version)"
    echo "Files present:"
    ls -la
    echo ""
    echo "Running appimage-builder..."
    echo "============================"
    
    appimage-builder --recipe AppImageBuilder.yml
    
} 2>&1 | tee full_build.log

echo ""
echo "Build finished. Check full_build.log for complete output."
echo "Press any key to continue..."
read -n 1