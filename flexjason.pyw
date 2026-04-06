import sys
from pathlib import Path
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
