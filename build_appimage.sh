#!/bin/bash

# Build script for creating AppImage
set -e

echo "Building Expense Tracker AppImage..."

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

# Install appimage-builder if not present
if ! command -v appimage-builder &> /dev/null; then
    echo "Installing appimage-builder..."
    
    DISTRO=$(detect_distro)
    echo "Detected distribution: $DISTRO"
    
    case $DISTRO in
        ubuntu|debian|linuxmint|pop)
            echo "Installing dependencies for Debian/Ubuntu..."
            sudo apt update
            sudo apt install -y python3-pip python3-setuptools patchelf desktop-file-utils libgdk-pixbuf2.0-dev fakeroot strace
            ;;
        fedora)
            echo "Installing dependencies for Fedora..."
            sudo dnf install -y python3-pip python3-setuptools patchelf desktop-file-utils gdk-pixbuf2-devel fakeroot strace
            ;;
        centos|rhel|rocky|almalinux)
            echo "Installing dependencies for RHEL/CentOS..."
            sudo yum install -y epel-release || sudo dnf install -y epel-release
            sudo yum install -y python3-pip python3-setuptools patchelf desktop-file-utils gdk-pixbuf2-devel fakeroot strace || \
            sudo dnf install -y python3-pip python3-setuptools patchelf desktop-file-utils gdk-pixbuf2-devel fakeroot strace
            ;;
        opensuse*|sles)
            echo "Installing dependencies for openSUSE..."
            sudo zypper install -y python3-pip python3-setuptools patchelf desktop-file-utils gdk-pixbuf-devel fakeroot strace
            ;;
        arch|manjaro)
            echo "Installing dependencies for Arch Linux..."
            sudo pacman -Sy --noconfirm python-pip python-setuptools patchelf desktop-file-utils gdk-pixbuf2 fakeroot strace
            ;;
        *)
            echo "Unknown distribution: $DISTRO"
            echo "Please install the following packages manually:"
            echo "- python3-pip python3-setuptools"
            echo "- patchelf desktop-file-utils"
            echo "- gdk-pixbuf development headers"
            echo "- fakeroot strace"
            echo ""
            echo "Then install appimage-builder with: pip3 install appimage-builder"
            exit 1
            ;;
    esac
    
    # Install appimage-builder via pip
    echo "Installing appimage-builder..."
    pip3 install --user appimage-builder
    
    # Add user bin to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "Adding ~/.local/bin to PATH for this session..."
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi

# Clean previous build
rm -rf AppDir *.AppImage || true

# Build the AppImage
echo "Starting AppImage build process..."
if appimage-builder --recipe AppImageBuilder.yml; then
    echo "AppImage built successfully!"
    echo "Run with: ./expense_tracker-${VERSION}-x86_64.AppImage"
else
    echo "ERROR: AppImage build failed!"
    echo "Check the output above for details."
    echo "Common issues:"
    echo "1. Missing dependencies - install manually using distro package manager"
    echo "2. Python version mismatch in AppImageBuilder.yml"
    echo "3. Missing static files (check static/ directory exists)"
    echo ""
    echo "Press Enter to exit..."
    read
    exit 1
fi