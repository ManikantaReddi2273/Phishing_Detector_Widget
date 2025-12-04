# Windows Phishing Detector Widget

A Windows desktop application that captures on-screen text and uses AI to detect phishing content.  
Backend is built with **Python FastAPI**, and the floating desktop UI is built with **Flutter Desktop**.

## 🚀 Features

- **Floating Widget**: Always-on-top draggable overlay on your desktop (Flutter desktop app)
- **Continuous Screen Scanning**: Backend continuously scans visible text from the active window (no clicks required)
- **Windows UI Automation Text Extraction**: Extracts text directly via Windows UI Automation (no OCR)
- **AI Phishing Detection (LLM-only)**: Uses the OpenAI API to analyze text for phishing patterns
- **Instant Results**: Shows safe/phishing status with risk level and explanation in the overlay

## 📋 Prerequisites

- **Python 3.10+** installed
- **Flutter 3+** with Windows desktop support enabled
- **Windows 10/11**

## 🛠️ Setup Instructions

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac (for reference)
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   # Copy example environment file
   copy .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_api_key_here
   ```

6. **Run the backend server**
   ```bash
   python main.py
   ```

   The API will be available at:
   - API base: http://127.0.0.1:8000
   - Docs: http://127.0.0.1:8000/docs
   - Health: http://127.0.0.1:8000/api/health

### Flutter Desktop Frontend (Floating Overlay)

1. **Navigate to the Flutter frontend**
   ```bash
   cd frontend_flutter
   ```

2. **Get dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the floating widget (Windows desktop)**
   ```bash
   flutter run -d windows
   ```

   Make sure the backend server is already running on `http://127.0.0.1:8000`.  
   The Flutter window will appear as a small, always-on-top, draggable overlay in the top-right corner.

### Running Tests

```bash
cd backend
pytest
```

For verbose output:
```bash
pytest -v
```

## 📁 Project Structure

```
phishing-detector-widget/
├── backend/                   # Python FastAPI backend
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Configuration and logging
│   │   ├── models/           # Pydantic schemas
│   │   └── services/         # Business logic (text extraction, LLM analysis, scanner)
│   ├── tests/                # Test suite
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
├── frontend_flutter/          # Flutter desktop floating widget (Windows)
└── docs/                      # Documentation
```

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```
Returns service health status.

### Backend Status
```
GET /api/status
```
Returns detailed backend and service status.

### Analyze Text
```
POST /api/analyze
```
Analyzes text for phishing content.

### Scan Entire Screen (on demand)
```
POST /api/scan-screen
```
Captures all visible on-screen text via Windows UI Automation and analyzes it in one step.

**Request Body:**
```json
{
  "text": "Your bank account will be blocked. Click here: http://fakebank.com",
  "include_urls": true
}
```

**Response:**
```json
{
  "is_phishing": true,
  "status": "phishing",
  "risk_level": "high",
  "confidence": 0.95,
  "reason": "Suspicious URL detected...",
  "suspicious_elements": [],
  "recommended_action": "ignore",
  "extracted_text": "...",
  "extracted_urls": ["http://fakebank.com"]
}
```

### Latest Scan (continuous background scanner)

```
GET /api/latest-scan
```

Returns the most recent phishing analysis result produced by the continuous
background scanner. Intended to be polled by the Flutter floating widget.

Example response (phishing detected):

```json
{
  "last_scan_at": "2024-01-15T10:30:00Z",
  "has_result": true,
  "error": null,
  "result": {
    "is_phishing": true,
    "status": "phishing",
    "risk_level": "high",
    "confidence": 0.95,
    "reason": "Suspicious URL detected...",
    "suspicious_elements": [],
    "recommended_action": "ignore",
    "extracted_text": "...",
    "extracted_urls": ["http://fakebank.com"]
  }
}
```

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## 📝 Configuration

Edit `backend/.env` to configure:
- OpenAI API key
- Server host and port
- Scan interval (`SCAN_INTERVAL_SECONDS`)
- Logging level

## 🔒 Security Notes

- Never commit `.env` file with API keys
- API keys are loaded from environment variables
- Screenshots are temporary and deleted after processing

## 📄 License

[To be determined]

## 🤝 Contributing

[To be determined]

---

**Note**: This project now uses a Flutter desktop overlay and continuous,
LLM-only phishing detection. The old Electron/React frontend and OCR
fallback have been removed.

