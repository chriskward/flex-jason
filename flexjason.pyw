import sys
import subprocess
import webview
import time
import io
import cairosvg
import urllib.request
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from pathlib import Path
import os
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["EGL_LOG_LEVEL"] = "fatal"
os.environ["MESA_DEBUG"] = "silent"

# note relative path to lib/<streamlit apps>
path = Path(__file__).parent / "lib" / "main.py"
img = Path(__file__).parent / "assets" / "jason_logo.svg"
port = 8401
timeout = 20

# generate loading splash screen
splash = tk.Tk()
splash.title("")
splash.resizable(False, False)
splash.overrideredirect(True)
splash.configure(bg="white", highlightbackground="black", highlightthickness=1)
splash.update_idletasks()
w, h = splash.winfo_screenwidth() , splash.winfo_screenheight()
x, y = (w // 2) - 300, (h // 2) - 200
splash.geometry(f"600x400+{x}+{y}")

# with the Jason Logo - why not!
png_data = cairosvg.svg2png(url=str(img), output_width = 400, output_height = 400)
jason_pil = Image.open(io.BytesIO(png_data)) 
jason_img = ImageTk.PhotoImage(jason_pil)
label = tk.Label(splash, image=jason_img, bg="white")   
label.image = jason_img
label.pack()
splash.update()

time.sleep(5)

# launch the streamlit serverx
subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(path), "--server.port", str(port), "--server.headless", "true"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
timer = time.time()

# repeatedly test for server readiness
# abandon bootup if this doesn't occur within 4 seconds
bootloader = True
while  bootloader:
    if time.time() - timer > timeout:
        root = tk.Tk()
        root.withdraw()
        splash.destroy()
        messagebox.showerror("Error", f"Streamlit failed to start, check port and firewall settings\nhttp://localhost:{port}")
        sys.exit(1)
    try:
        urllib.request.urlopen(f"http://localhost:{port}/_stcore/health")
        bootloader = False  # exit while loop if sucessful connection to streamlit server
    except:
        time.sleep(0.2)


# launch app in webview window
splash.destroy()
webview.create_window("Flexible Jason", f"http://localhost:{port}" )
webview.start(gui ="qt")
