import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread

from ui.widget import FloatingWidget
from core.service import BackgroundService


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # UI
    widget = FloatingWidget()
    widget.show()

    # Background service
    service = BackgroundService()

    # Thread
    thread = QThread()
    service.moveToThread(thread)

    # Wire signals
    service.update_ui_signal.connect(widget.update_ui)
    thread.started.connect(service.start)

    # Start background processing
    thread.start()

    sys.exit(app.exec_())
