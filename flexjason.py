import sys
import subprocess
import webview
import time
import ctypes
import urllib.request
from pathlib import Path

path = Path.cwd() / "app" / "main.py"
bootloader = False
port = 8410

subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(path),
                 "--server.port", str(port), "--server.headless", "true"])

timer = time.time()

while not bootloader:
    if time.time() - timer > 10:
        ctypes.windll.user32.MessageBoxW(0, "Streamlit failed to start", "Error", 0x10)
        sys.exit(1)
    try:
        urllib.request.urlopen(f"http://localhost:{port}/_stcore/health")
        bootloader = True
    except:
        time.sleep(0.2)

webview.create_window("Flexible Jason", f"http://localhost:{port}" )
webview.start()
