import sys
import os
import logging
from pathlib import Path

# Suppress all console output from libraries
logging.disable(logging.CRITICAL)
os.environ["PYWEBVIEW_LOG"] = "warning"
os.environ["WEBVIEW_LOG_LEVEL"] = "warning"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["MESA_GL_VERSION_OVERRIDE"] = "4.5"

from nicegui import ui

# relative path to main.py appended to local path var
sys.path.insert(0, str(Path(__file__).parent / "lib"))

# choose a port
port = 8501

import main

ui.run(
    title="Flexible Jason",
    port=port,
    native=False,
    reload=False,
    show=True,
    window_size=(1280, 800),
)
