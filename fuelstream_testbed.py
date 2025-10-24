from nicegui import ui

ui.label('Hello NiceGUI!')

ui.button('Click me!', on_click=lambda: ui.notify('You clicked me!'))

ui.run(port=5000)

