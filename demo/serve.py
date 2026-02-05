#!/usr/bin/env python3
"""Simple HTTP server to serve the pyfpspack web demo.

Usage:
    python serve.py [port]

Example:
    python serve.py 8000

Then open http://localhost:8000 in your browser.
"""
import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    # Change to demo directory
    demo_dir = Path(__file__).parent
    os.chdir(demo_dir)

    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"pyfpspack Web Demo")
        print(f"==================")
        print(f"Serving at: {url}")
        print(f"Press Ctrl+C to stop\n")

        # Try to open browser
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
