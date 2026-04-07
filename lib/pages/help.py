from nicegui import ui


def render(container):
    container.clear()
    with container:
        pass  # page title shown in top bar
        ui.label("Help documentation coming soon.")
