#!/usr/bin/env python3
"""
Wrapper script to launch the Streamlit expense tracker app
"""
import subprocess
import sys
import os
import webbrowser
import time
import threading

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:8501')

def main():
    # Get the directory where this script is located
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the app directory
    os.chdir(app_dir)
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'expense_tracker.py',
            '--server.headless', 'true',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error running app: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()