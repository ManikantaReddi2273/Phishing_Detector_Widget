# Windows Phishing‑Text Detector Widget
A detailed concept document describing the complete idea, purpose, architecture, modules, and workflow of the Windows AI‑based phishing detection widget using **Python as backend**.

---

## 🚀 Project Idea: Windows Phishing‑Text Detector Widget
A small Windows application that captures on‑screen text and uses an AI model to detect phishing content.

---

## 🧩 1. What Is This Project?
This project is a **Windows desktop tool** that instantly tells whether any text visible on the screen is **phishing or safe**.

It works on:
- Notepad
- WhatsApp Desktop
- Gmail
- Websites
- PDF files
- Word documents
- Any displayed text

A floating on‑screen widget button triggers the scan and analysis.

---

## 🎯 2. Why Do We Need This?
Users commonly face:
- Fake job offers
- Fraud bank alerts
- Fake UPI payment messages
- Lottery and money scams
- Fake account deactivation threats

Most people cannot easily identify scams. **AI‑powered phishing detection** solves this problem.

---

## 🛠️ 3. What the System Will Do (Features)
### ✔ Floating Widget on Desktop
- Small circular button
- Always‑on‑top
- Draggable
- Works on any Windows laptop

### ✔ On Click → Capture Visible Text
The tool will:
- Capture a screenshot
- Use OCR (Python) to extract text
- Process the extracted text

### ✔ AI (LLM) Analysis
Python backend sends the extracted text to an LLM:
- Detects phishing patterns
- Identifies suspicious links
- Finds urgency or threats
- Analyzes tone

### ✔ Display Result
Popup shows:
- 🟢 SAFE or 🔴 PHISHING
- Reason
- Risk level
- Recommended user action

---

## 🧬 4. How It Works (Technical Workflow)
```
Floating Widget Button (Electron)
        ↓
User Clicks
        ↓
Python Backend Captures Screenshot
        ↓
OCR Extracts Text
        ↓
Python Sends Text to LLM
        ↓
AI Returns Result
        ↓
Electron Shows Result Popup
```

---

## 🧱 5. Detailed Architecture (With Python Backend)
### A. Frontend (Electron + React)
- Floating widget UI
- Popup modal for results
- Sends requests to Python backend
- Receives phishing result

Why Electron?
- Works on all Windows laptops
- Easy UI building
- Can bundle into a single installer

---

### B. Backend (Python Logic)
Python runs as a local service using **FastAPI** or **Flask**.

Backend responsibilities:
1. Capture screenshot (`pyautogui` or `mss`)
2. Run OCR to extract text (`pytesseract`, `easyocr`, or OpenAI Vision)
3. Analyze with an AI model (OpenAI, Gemini, Llama)
4. Return structured phishing results to Electron

Python Libraries Used:
- `pyautogui` or `mss` → screenshot capture
- `Pillow` (PIL) → image handling
- `pytesseract` / `easyocr` → OCR
- `openai` or similar SDK → AI
- `FastAPI` or `Flask` → API layer

Communication: Electron → Python via HTTP or WebSocket.

---

### C. OCR Engine (Python)
OCR = extract text from screenshot.

Example screenshot:
```
Your bank account is blocked.
Click here: http://fakebank-security.com
```

OCR output:
```
Your bank account is blocked. Click here: http://fakebank-security.com
```

OCR Options:
- **pytesseract** (Free, classic OCR)
- **easyocr** (Better accuracy)
- **OpenAI Vision** (Highest accuracy)

---

### D. LLM Module (Python)
Python sends extracted text to an LLM.

Example AI prompt:
```
Analyze the following text for phishing:
"Your ATM card will be deactivated. Update your KYC here: http://fake-kyc.in"
```

Example LLM Output:
```
Phishing: YES
Reason: Suspicious URL + urgency tactic
Risk: High
```

---

### E. Result Display Module (Electron)
Electron receives JSON response and displays:
- Safe / Phishing
- Reason
- Risk level
- Recommended user action

---

## 🧠 6. Example Use Case
### Scenario
WhatsApp Desktop displays:
```
Dear user, your electricity bill is overdue.
Click here to avoid power cut:
http://fake-electricitypay.in
```

### User Action
User clicks the floating widget.

### System Process
1. Python captures screenshot
2. Python extracts text via OCR
3. Python sends text to AI
4. AI detects phishing
5. Electron shows popup:
```
⚠️ PHISHING DETECTED
Reason: Fake urgency + suspicious domain
```

---

## ⚙️ 7. Main Components
| Module                     | Purpose                         |
|---------------------------|---------------------------------|
| Floating Widget (Electron)| User interface                  |
| Python Backend API        | Core logic + OCR + AI           |
| Screenshot Capture        | Capture on‑screen content       |
| OCR Engine (Python)       | Extract text                    |
| AI Analyzer (Python)      | Detect phishing                 |
| Result UI (Electron)      | Display results                 |
| Installer Builder         | Generate Windows installer       |

---

## 📦 8. Technologies Used
### Frontend
- Electron
- React

### Backend (Python)
- Python 3.x
- FastAPI or Flask
- pyautogui / mss
- Pillow
- pytesseract / easyocr
- openai or other AI SDK

### Packaging Tools
- Electron Builder → for Electron installer
- PyInstaller → convert Python backend to .exe

---

## 🌍 9. Compatibility
Works on:
- Windows 10
- Windows 11
- Any laptop

No dependency on installed applications.

---

## 🛡️ 10. Advantages
- System‑wide scanning
- Python offers powerful OCR + AI tools
- Works across all apps
- Lightweight frontend
- Fast, automated phishing detection
- Easy for non‑technical users

---

## 📘 Final Summary
A **Windows AI assistant widget** powered by Python, that:
1. Always stays on the screen
2. Captures text from any application
3. Extracts text using OCR
4. Sends it to AI
5. Instantly detects phishing

This becomes a **One‑Click Phishing Detector** for the entire OS, combining Electron UI + Python intelligence.

---

