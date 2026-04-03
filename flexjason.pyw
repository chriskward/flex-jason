import sys
import subprocess
import webview
import time
import urllib.request
import tkinter as tk
from pathlib import Path

path = Path.cwd() / "app" / "main.py"
bootloader = True
port = 8410
timer = time.time()

while  bootloader:
    
    if time.time() - timer > 10:
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", "Streamlit failed to start")
        bootloader = False
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(path),
                 "--server.port", str(port), "--server.headless", "true"])
        time.sleep(0.2)
        urllib.request.urlopen(f"http://localhost:{port}/_stcore/health")
        webview.create_window("Flexible Jason", f"http://localhost:{port}" )
        webview.start()
        bootloader = True
    except:
        time.sleep(0.2)


