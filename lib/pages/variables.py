from nicegui import ui


def render(container):
    with container:
        ui.label("Variables").classes("text-h4 q-pa-md")
