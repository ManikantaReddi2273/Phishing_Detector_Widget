import win32gui
import mss
import numpy as np

def capture_active_window():
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return None

    try:
        rect = win32gui.GetWindowRect(hwnd)
    except Exception:
        return None

    x1, y1, x2, y2 = rect

    # Ignore invalid or tiny windows
    if x2 - x1 < 50 or y2 - y1 < 50:
        return None

    with mss.mss() as sct:
        monitor = {
            "top": y1,
            "left": x1,
            "width": x2 - x1,
            "height": y2 - y1
        }
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)

    return img
