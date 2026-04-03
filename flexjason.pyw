import sys
import subprocess
import webview
import time
import urllib.request
import tkinter as tk
from tkinter import messagebox

from pathlib import Path

path = Path.cwd() / "app" / "main.py"
bootloader = True
port = 8410

# launch the streamlit server
subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(path), "--server.port", str(port), "--server.headless", "true"])
timer = time.time()

# repeatedly test for server readiness
# abandon bootup if this doesn't occur within 4 seconds
while  bootloader:
    if time.time() - timer > 5:
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", "Streamlit failed to start, check port and firewall settings")
        sys.exit(1)
    try:
        time.sleep(0.2)
        urllib.request.urlopen(f"http://localhost:{port}/_stcore/health")
        bootloader = False  # exit while loop if sucessful connection to streamlit server
    except:
        time.sleep(0.2)


# launch app in webview window
webview.create_window("Flexible Jason", f"http://localhost:{port}" )
webview.start()
