import win32gui
import win32process
import psutil

def get_active_window_info():
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)

    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process_name = "Unknown"

    try:
        process = psutil.Process(pid)
        process_name = process.name()
    except Exception:
        pass

    return {
        "title": window_title,
        "process": process_name
    }


