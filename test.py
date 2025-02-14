from nicegui import app,ui

@ui.page('/test')
def main():
    print(app.storage.user)
    state = app.storage.user

    def print_values():
        if 'input' in state:
            print(state['input'])

    #def set_storage(value):
    #    app.storage.browser.clear()
    #   app.storage.browser['input'] = value




    ui.input().bind_value(state,'input')
    ui.label().bind_text(state,'input')
    ui.button(on_click= lambda:print_values())

ui.run(storage_secret='STORAGE_SECRET')