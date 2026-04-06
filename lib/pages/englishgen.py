from nicegui import ui


def render(container):
    with container:
        ui.label("Descriptions").classes("text-h4 q-pa-md")
