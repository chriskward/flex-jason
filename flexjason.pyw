import sys
import io
import time
import cairosvg
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import os

# suppress Qt/Mesa debug noise
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["EGL_LOG_LEVEL"] = "fatal"
os.environ["MESA_DEBUG"] = "silent"

img = Path(__file__).parent / "assets" / "jason_logo.svg"
port = 8401

# ── splash screen ────────────────────────────────────────────────────────
splash = tk.Tk()
splash.title("")
splash.resizable(False, False)
splash.overrideredirect(True)
splash.configure(bg="white", highlightbackground="black", highlightthickness=1)
splash.update_idletasks()
w, h = splash.winfo_screenwidth(), splash.winfo_screenheight()
x, y = (w // 2) - 300, (h // 2) - 200
splash.geometry(f"600x400+{x}+{y}")

png_data = cairosvg.svg2png(url=str(img), output_width=400, output_height=400)
jason_pil = Image.open(io.BytesIO(png_data))
jason_img = ImageTk.PhotoImage(jason_pil)
label = tk.Label(splash, image=jason_img, bg="white")
label.image = jason_img
label.pack()
splash.update()

time.sleep(5)
splash.destroy()

# ── launch NiceGUI in native (pywebview) mode ────────────────────────────
# importing main registers all @ui.page routes
sys.path.insert(0, str(Path(__file__).parent / "lib"))
import main  # noqa: F401, E402
from nicegui import ui  # noqa: E402

ui.run(
    title="Flexible Jason",
    port=port,
    native=True,          # opens a pywebview window instead of a browser tab
    reload=False,
    show=True,
    window_size=(1280, 800),
)
