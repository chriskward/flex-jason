from nicegui import ui


def render(container):
    with container:
        ui.label("Datasets").classes("text-h4 q-pa-md")
