from nicegui import ui


def render(container):
    with container:
        ui.label("Derivations").classes("text-h4 q-pa-md")
