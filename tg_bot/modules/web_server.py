# Persistent Web Server for Render Keep-Alive by @TheRealPhoenix

import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Respond with a healthy 200 OK to any incoming ping
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

    def log_message(self, format, *args):
        # Silences the console logs from filling up with pings every 5 minutes
        pass

def run_server():
    # Render assigns a port dynamically via the PORT env variable; default to 10000
    port = int(os.environ.get("PORT", 10000))
    server_address = ("", port)
    
    try:
        httpd = HTTPServer(server_address, KeepAliveHandler)
        print(f"[Keep-Alive] Web server successfully started on port {port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"[Keep-Alive] Failed to start web server: {e}")

# Spin up the server inside an isolated background thread so it never blocks your bot
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
