import pytesseract
import cv2

# If tesseract is not detected automatically, uncomment and set path:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image):
    if image is None:
        return ""

    # MSS gives BGRA images → convert to BGR
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # OCR configuration tuned for UI text
    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(gray, config=config)

    return text.strip()
