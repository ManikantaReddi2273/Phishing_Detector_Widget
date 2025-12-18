import time
from PyQt5.QtCore import QObject, pyqtSignal

from core.window_monitor import get_active_window_info
from core.screen_capture import capture_active_window
from core.accessibility_reader import get_accessible_text
from core.ocr_engine import extract_text_from_image
from core.text_processor import clean_text, chunk_text

from core.groq_client import analyze_text_with_groq
from core.phishing_prompt import build_phishing_prompt
from core.decision_engine import parse_groq_response, aggregate_results


def is_own_app(window):
    if not window:
        return False
    return (
        window.get("process", "").lower() == "python.exe"
        or "phishing guard" in (window.get("title") or "").lower()
    )


class BackgroundService(QObject):
    update_ui_signal = pyqtSignal(str, float, list)

    def __init__(self):
        super().__init__()
        self.running = True
        self.last_window = None

    def start(self):
        while self.running:
            try:
                window = get_active_window_info()

                # ❌ Skip our own app window
                if is_own_app(window):
                    time.sleep(0.7)
                    continue

                if window != self.last_window:
                    # 🔄 Immediate UI feedback
                    self.update_ui_signal.emit("scanning", 0.0, [])

                    image = capture_active_window()
                    if image is None:
                        # Fail-safe → treat as safe
                        self.update_ui_signal.emit("low", 0.0, [])
                        self.last_window = window
                        continue

                    ocr_text = extract_text_from_image(image)
                    acc_text = get_accessible_text()

                    combined_text = ocr_text + "\n" + acc_text
                    cleaned_text = clean_text(combined_text)
                    chunks = chunk_text(cleaned_text)

                    results = []

                    for chunk in chunks:
                        if not chunk.strip():
                            continue

                        prompt = build_phishing_prompt(chunk)
                        response = analyze_text_with_groq(prompt)
                        parsed = parse_groq_response(response)
                        results.append(parsed)

                    # 🔐 Reset logic
                    if not results:
                        final_decision = {
                            "final_risk": "low",
                            "confidence": 0.0,
                            "reasons": []
                        }
                    else:
                        final_decision = aggregate_results(results)

                    risk = final_decision["final_risk"]
                    confidence = final_decision["confidence"]
                    reasons = final_decision.get("reasons", [])

                    print("DEBUG → Emitting UI update:", risk, confidence)
                    self.update_ui_signal.emit(risk, confidence, reasons)

                    self.last_window = window

                time.sleep(0.7)

            except Exception as e:
                print("❌ Service loop error:", e)
                time.sleep(2)
