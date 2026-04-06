from nicegui import ui


def render(container):
    with container:
        ui.label("Code Gen").classes("text-h4 q-pa-md")
