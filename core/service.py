import time
import numpy as np
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
        self.last_image = None

    def start(self):
        while self.running:
            try:
                window = get_active_window_info()

                # ❌ Skip our own app window
                if is_own_app(window):
                    time.sleep(0.7)
                    continue

                print("DEBUG → Current window:", window)

                # Capture current image for visual-change detection
                image = capture_active_window()

                # If we can't capture, fall back to safe
                if image is None:
                    self.update_ui_signal.emit("low", 0.0, [])
                    self.last_window = window
                    self.last_image = None
                    time.sleep(0.7)
                    continue

                # Determine if image changed significantly
                visual_changed = self.image_has_changed(image, self.last_image)

                # If window changed, force immediate detection (keep previous UX)
                if window != self.last_window:
                    self.update_ui_signal.emit("scanning", 0.0, [])
                    visual_changed = True

                print("DEBUG → Window changed:", window != self.last_window)
                print("DEBUG → Visual changed:", visual_changed)
                print("DEBUG → Image captured:", image.shape if image is not None else None)

                if not visual_changed:
                    # Nothing changed visually — skip expensive OCR/LLM
                    self.last_image = image
                    time.sleep(0.7)
                    continue

                # Proceed with OCR + analysis
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

                # update last seen state
                self.last_window = window
                self.last_image = image

                time.sleep(0.7)

            except Exception as e:
                print("❌ Service loop error:", e)
                time.sleep(2)

    def image_has_changed(self, img_new, img_old, threshold=0.02):
        """Lightweight visual-change detection using downsampled grayscale diff.

        img_new/img_old are numpy arrays as returned by `capture_active_window()`.
        Returns True if images differ by more than `threshold` (fraction 0..1).
        """
        try:
            if img_new is None:
                return False
            if img_old is None:
                return True

            # Convert to grayscale by averaging RGB channels (ignore alpha if present)
            a = img_new[..., :3].astype("float32")
            b = img_old[..., :3].astype("float32")

            # Downsample by taking every Nth pixel to keep it cheap
            downsample = 8
            a_small = a[::downsample, ::downsample].mean(axis=2)
            b_small = b[::downsample, ::downsample].mean(axis=2)

            diff = np.mean(np.abs(a_small - b_small)) / 255.0
            print("DEBUG → Grayscale diff:", diff)
            return diff > threshold
        except Exception:
            return True
