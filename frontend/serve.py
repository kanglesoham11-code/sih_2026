"""
Simple HTTP server to serve the frontend
Run this to access the ORCA dashboard
"""
import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌊 ORCA Frontend Dashboard")
        print(f"=" * 50)
        print(f"✅ Server running at: http://localhost:{PORT}")
        print(f"✅ Dashboard: http://localhost:{PORT}/index.html")
        print(f"=" * 50)
        print(f"Press Ctrl+C to stop the server")
        print()
        
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}/index.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
