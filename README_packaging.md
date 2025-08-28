# Packaging the Expense Tracker as a Linux App

## AppImage Packaging

This directory contains files to package the expense tracker as a portable Linux AppImage.

### Files Created:
- `AppImageBuilder.yml` - Configuration for building the AppImage
- `expense_tracker.desktop` - Desktop entry file
- `run_app.py` - Launcher script that starts Streamlit and opens browser
- `build_appimage.sh` - Build script

### To Build:

The build script automatically detects your Linux distribution and installs the required dependencies.

**Supported distributions:**
- Ubuntu, Debian, Linux Mint, Pop!_OS
- Fedora
- CentOS, RHEL, Rocky Linux, AlmaLinux  
- openSUSE, SLES
- Arch Linux, Manjaro

**Build the AppImage:**
```bash
./build_appimage.sh
```

The script will:
1. Auto-detect your Linux distribution
2. Install required system packages using your distro's package manager
3. Install appimage-builder via pip
4. Build the AppImage

**Manual dependency installation (if needed):**

*Ubuntu/Debian:*
```bash
sudo apt update
sudo apt install -y python3-pip python3-setuptools patchelf desktop-file-utils libgdk-pixbuf2.0-dev fakeroot strace
```

*Fedora:*
```bash
sudo dnf install -y python3-pip python3-setuptools patchelf desktop-file-utils gdk-pixbuf2-devel fakeroot strace
```

3. **Run the app:**
   ```bash
   ./expense_tracker-1.0.0-x86_64.AppImage
   ```

### How it works:
- The AppImage bundles Python, all dependencies, and your app code
- When launched, it starts a Streamlit server and opens your default browser
- The app runs at `http://localhost:8501`
- Close the terminal/app to stop the server

### Alternative Packaging Options:

#### Docker Container:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "expense_tracker.py", "--server.address", "0.0.0.0"]
```

#### Flatpak:
Create a Flatpak manifest file for distribution through Flathub.

#### Snap:
Create a `snapcraft.yaml` for Ubuntu Snap Store distribution.

## Alternative: PyInstaller (Recommended)

If AppImage build fails, use PyInstaller which is more reliable:

**Build with PyInstaller:**
```bash
./build_pyinstaller.sh
```

**Run the executable:**
```bash
./dist/expense-tracker
```

**Install system-wide (optional):**
```bash
sudo cp dist/expense-tracker /usr/local/bin/
```

PyInstaller creates a single executable file that bundles Python and all dependencies. It's more compatible across different Linux systems.

---

The PyInstaller approach is recommended for most users as it's more reliable than AppImage and works across Linux distributions.