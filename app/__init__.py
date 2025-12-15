class AppState:
    resources = {}

app_state = AppState()

def getAppState(): # use this for dependency injection
    return app_state
