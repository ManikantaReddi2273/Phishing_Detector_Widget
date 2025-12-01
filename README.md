# Windows Phishing Detector Widget

A Windows desktop application that captures on-screen text and uses AI to detect phishing content. Built with Electron (frontend) and Python FastAPI (backend).

## 🚀 Features

- **Floating Widget**: Always-on-top draggable button on your desktop
- **Screenshot Capture**: Captures visible text from any application
- **OCR Text Extraction**: Extracts text from screenshots using advanced OCR
- **AI Phishing Detection**: Uses LLM to analyze text for phishing patterns
- **Instant Results**: Shows safe/phishing status with detailed analysis

## 📋 Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** and npm (for frontend - Phase 5)
- **Windows 10/11**

## 🛠️ Setup Instructions

### Backend Setup (Phases 1-4 Complete)

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
   - API: http://127.0.0.1:8000
   - Docs: http://127.0.0.1:8000/docs
   - Health: http://127.0.0.1:8000/api/health

### Frontend Setup (Phase 5 - Electron + React)

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run in development mode**
   ```bash
   npm run dev
   ```
   This starts Vite (renderer) and Electron (floating widget) concurrently.  
   Ensure the backend server is already running on `http://127.0.0.1:8000`.

3. **Environment variables (optional)**
   - Create `frontend/.env` and set `VITE_BACKEND_URL=http://127.0.0.1:8000/api`
     if you need to override the backend endpoint.

4. **Build for production**
   ```bash
   npm run build
   ```
   Bundles the renderer with Vite and compiles the Electron main process to `dist/`.

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
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration and logging
│   │   ├── models/         # Pydantic schemas
│   │   └── services/       # Business logic (Phase 2-4)
│   ├── tests/              # Test suite
│   ├── main.py             # Application entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # Electron + React (Phase 5)
└── docs/                   # Documentation
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

### Scan Entire Screen
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

## 📊 Development Status

### ✅ Phase 1: Project Setup & Backend Foundation (Current)
- [x] Project structure created
- [x] FastAPI backend setup
- [x] API endpoints implemented
- [x] Pydantic models defined
- [x] Testing infrastructure
- [x] Logging configuration

### ✅ Phase 2: Screen Text Extraction
- [x] Windows UI Automation extractor
- [x] Safe fallback scaffolding
- [x] Unit tests

### ✅ Phase 3: OCR Fallback & Text Processing
- [x] OCR fallback service (easyocr / pytesseract)
- [x] Text cleaning and URL/email extraction
- [x] Unit tests

### ✅ Phase 4: AI Phishing Detection
- [x] AI analyzer service
- [x] OpenAI integration with JSON schema
- [x] Response parsing + rule-based fallback

### 🔄 Phase 5: Frontend (Electron)
- [x] Electron setup with Vite + React
- [x] Floating widget UI
- [x] Backend communication stub

### 🔄 Phase 7: Integration & Testing
- [x] New `/api/scan-screen` endpoint (screen text → AI → result)
- [x] Frontend wired to real backend workflow
- [ ] Performance tuning & cross-app manual testing

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
- OCR settings
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

**Note**: This is Phase 1 implementation. Full functionality will be available after completing all phases.

