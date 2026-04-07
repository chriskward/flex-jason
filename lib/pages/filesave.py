import yaml

from nicegui import ui, run
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


def _save_file_dialog() -> str:
    """Open a native OS save-file picker (runs in a thread to avoid blocking)."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.asksaveasfilename(
        title='Save pipeline',
        defaultextension='.yaml',
        filetypes=[
            ('YAML files', '*.yaml *.yml'),
            ('All files', '*.*'),
        ],
    )
    root.destroy()
    return path


def render(container, pipeline):
    CARD_W = '140px'
    CARD_H = '200px'

    with container:

        async def _on_save_pipeline():
            if not pipeline:
                ui.notify('Pipeline is empty — nothing to save', type='warning')
                return
            dest = await run.io_bound(_save_file_dialog)
            if dest:
                Path(dest).write_text(
                    yaml.dump(pipeline, default_flow_style=False, sort_keys=False),
                    encoding='utf-8',
                )
                ui.notify(f'Pipeline saved to {Path(dest).name}')

        save_card = ui.card().classes(
            'flex flex-col items-center justify-center cursor-pointer '
            'hover:bg-blue-1 q-ml-md'
        ).style(f'width: {CARD_W}; height: {CARD_H};')
        with save_card:
            ui.icon('data_object').classes('text-5xl text-amber-8')
            ui.label('Save Pipeline').classes('text-xs text-grey-7 q-mt-sm')
        save_card.on('click', _on_save_pipeline)
