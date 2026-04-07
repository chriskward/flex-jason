from nicegui import ui, run
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


def _file_icon(path: str) -> tuple[str, str]:
    """Return a (Material icon name, Tailwind color class) based on file extension."""
    ext = Path(path).suffix.lower()
    if ext in ('.xlsx', '.xls'):
        return 'table_chart', 'text-green-7'
    if ext == '.pdf':
        return 'picture_as_pdf', 'text-red-7'
    if ext == '.md':
        return 'article', 'text-blue-7'
    if ext in ('.yaml', '.yml'):
        return 'data_object', 'text-amber-8'
    if ext == '.json':
        return 'code', 'text-orange-7'
    if ext == '.txt':
        return 'description', 'text-grey-7'
    if ext == '.csv':
        return 'grid_on', 'text-teal-7'
    return 'insert_drive_file', 'text-grey-7'


def _open_file_dialog() -> str:
    """Open a native OS file picker (runs in a thread to avoid blocking)."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askopenfilename(
        title='Select a file',
        filetypes=[
            ('Supported files', '*.xlsx *.xls *.pdf *.md *.yaml *.yml *.json *.txt *.csv'),
            ('Excel files', '*.xlsx *.xls'),
            ('PDF files', '*.pdf'),
            ('Markdown files', '*.md'),
            ('YAML files', '*.yaml *.yml'),
            ('JSON files', '*.json'),
            ('Text files', '*.txt'),
            ('CSV files', '*.csv'),
            ('All files', '*.*'),
        ],
    )
    root.destroy()
    return path


def render(container, pipeline):
    selected_files: dict[int, str] = {}
    card_counter = {'next': 0}
    expand_holder = {'card': None}

    CARD_W = '140px'
    CARD_H = '200px'

    def _make_file_card(grid):
        idx = card_counter['next']
        card_counter['next'] += 1
        card = ui.card().classes(
            'flex flex-col items-center justify-center cursor-pointer hover:bg-grey-1'
        ).style(f'width: {CARD_W}; height: {CARD_H};')
        with card:
            ui.icon('add').classes('text-5xl text-grey-5')
            ui.label('Add file').classes('text-xs text-grey-5 q-mt-sm')

        async def _on_click(_e, i=idx, c=card):
            file_path = await run.io_bound(_open_file_dialog)
            if file_path:
                selected_files[i] = file_path
                c.clear()
                with c:
                    icon_name, icon_color = _file_icon(file_path)
                    ui.icon(icon_name).classes(f'text-5xl {icon_color}')
                    ui.label(Path(file_path).name).classes(
                        'text-xs text-center q-mt-sm'
                    ).style(
                        f'max-width: 110px; overflow: hidden; '
                        'text-overflow: ellipsis; white-space: nowrap;'
                    )

        card.on('click', _on_click)

    def _make_expand_card(grid):
        card = ui.card().classes(
            'flex flex-col items-center justify-center cursor-pointer hover:bg-grey-1'
        ).style(f'width: {CARD_W}; height: {CARD_H};')
        with card:
            ui.icon('double_arrow').classes('text-5xl text-grey-5')
            ui.label('More').classes('text-xs text-grey-5 q-mt-sm')

        def _on_expand(_e):
            old = expand_holder['card']
            if old:
                old.delete()
            with grid:
                for _ in range(3):
                    _make_file_card(grid)
                _make_expand_card(grid)

        card.on('click', _on_expand)
        expand_holder['card'] = card

    def _on_done():
        paths = list(selected_files.values())
        pipeline['selected_files'] = paths
        ui.notify(f'{len(paths)} file(s) selected')

    def _on_clear():
        selected_files.clear()
        card_counter['next'] = 0
        expand_holder['card'] = None
        grid_holder['ref'].clear()
        with grid_holder['ref']:
            for _ in range(2):
                _make_file_card(grid_holder['ref'])
            _make_expand_card(grid_holder['ref'])

    grid_holder = {}

    with container:
        with ui.element('div').classes(
            'flex flex-wrap gap-4 q-pa-md'
        ) as grid:
            grid_holder['ref'] = grid
            for _ in range(2):
                _make_file_card(grid)
            _make_expand_card(grid)
        with ui.row().classes('q-mt-md q-ml-md gap-2'):
            ui.button('Done', on_click=_on_done, icon='check').props(
                'flat color=standard'
            ).classes('text-grey-8')
            ui.button('Clear', on_click=_on_clear, icon='restart_alt').props(
                'flat color=standard'
            ).classes('text-grey-8')
