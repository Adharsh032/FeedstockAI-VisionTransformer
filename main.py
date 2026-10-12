"""
FEEDSTOCK.AI - Main Application Entrypoint for Visual Studio Code
Run this file directly in VS Code (F5 or the Run Python File button).
"""

import sys
import webbrowser
import threading
import time
import uvicorn

from backend.config import HOST, PORT, APP_TITLE


def open_browser():
    """Wait for the server to start, then automatically open the web dashboard in the browser."""
    time.sleep(1.2)
    url = f"http://{HOST}:{PORT}"
    print(f"\n[+] Opening Feedstock.AI in your default browser: {url}\n")
    webbrowser.open(url)


def main():
    print("=" * 70)
    print(f"  {APP_TITLE}")
    print("  Industry 4.0 Vision Transformer Defect Detection System")
    print("=" * 70)
    print(f"[*] Starting local application server at: http://{HOST}:{PORT}")
    print(f"[*] Interactive API Documentation:       http://{HOST}:{PORT}/docs")
    print("[*] Press Ctrl+C in this terminal to stop the server.\n")

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn server
    uvicorn.run(
        "backend.app:app",
        host=HOST,
        port=PORT,
        reload=False
    )


if __name__ == "__main__":
    main()
