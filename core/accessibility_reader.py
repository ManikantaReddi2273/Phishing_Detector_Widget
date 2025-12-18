from pywinauto import Desktop

def get_accessible_text():
    try:
        app = Desktop(backend="uia").get_active()
        texts = []

        for element in app.descendants():
            try:
                if element.window_text():
                    texts.append(element.window_text())
            except Exception:
                pass

        return "\n".join(texts)

    except Exception:
        return ""
