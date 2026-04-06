from nicegui import ui


def render(container):
    with container:
        ui.label("Settings").classes("text-h4 q-pa-md")
