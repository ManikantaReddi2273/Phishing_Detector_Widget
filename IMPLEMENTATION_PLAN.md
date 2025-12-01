# Implementation Plan: Windows Phishing Detector Widget

## 📋 Table of Contents
1. [Project Structure](#project-structure)
2. [Technology Stack Decisions](#technology-stack-decisions)
3. [Implementation Phases](#implementation-phases)
4. [Development Workflow](#development-workflow)
5. [Testing Strategy](#testing-strategy)
6. [Packaging & Distribution](#packaging--distribution)

---

## 📁 Project Structure

```
phishing-detector-widget/
│
├── frontend/                    # Electron + React Application
│   ├── package.json
│   ├── electron-builder.yml
│   ├── src/
│   │   ├── main/               # Electron main process
│   │   │   ├── main.js         # Main Electron entry point
│   │   │   ├── preload.js      # Preload script for security
│   │   │   └── window-manager.js
│   │   ├── renderer/           # React UI
│   │   │   ├── App.jsx
│   │   │   ├── components/
│   │   │   │   ├── FloatingWidget.jsx
│   │   │   │   ├── ResultModal.jsx
│   │   │   │   └── LoadingSpinner.jsx
│   │   │   ├── styles/
│   │   │   │   └── App.css
│   │   │   └── utils/
│   │   │       └── api-client.js
│   │   └── index.html
│   └── public/
│
├── backend/                     # Python FastAPI Backend
│   ├── requirements.txt
│   ├── main.py                 # FastAPI application entry
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py       # API endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py       # Configuration management
│   │   │   └── logger.py       # Logging setup
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── text_extractor.py  # Screen text extraction service (primary)
│   │   │   ├── screenshot.py      # Screenshot capture (fallback)
│   │   │   ├── ocr.py              # OCR text extraction (fallback)
│   │   │   └── ai_analyzer.py      # LLM phishing detection
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py       # Pydantic models
│   └── tests/
│       ├── test_screenshot.py
│       ├── test_ocr.py
│       └── test_ai_analyzer.py
│
├── shared/                      # Shared configuration
│   └── config.json             # API endpoints, ports, etc.
│
├── build/                       # Build outputs
│   ├── frontend/               # Electron build
│   └── backend/                # Python executable
│
├── docs/                        # Documentation
│   ├── API.md
│   └── SETUP.md
│
├── .gitignore
├── README.md
└── IMPLEMENTATION_PLAN.md       # This file
```

---

## 🔧 Technology Stack Decisions

### Frontend
- **Electron**: v28+ (latest stable)
- **React**: v18+ with Vite for fast development
- **UI Library**: TailwindCSS or styled-components for modern UI
- **State Management**: React Context API (simple state) or Zustand

### Backend
- **Python**: 3.10+ (for better type hints and performance)
- **FastAPI**: Modern, fast, async-capable API framework
- **Screen Text Extraction**: 
  - Primary: Windows UI Automation API (`pywin32`, `comtypes`) - Direct text extraction from UI elements
  - Alternative: `pyautogui` with accessibility APIs
  - Fallback: Screenshot + OCR for applications that don't support UI Automation
- **Screenshot**: `mss` (for fallback OCR method)
- **OCR**: `easyocr` or `pytesseract` (fallback only, when UI Automation fails)
- **AI/LLM**: 
  - Primary: OpenAI GPT-4o-mini (cost-effective, high accuracy)
  - Alternative: Google Gemini API (free tier available)
  - Local option: Ollama with Llama 3 (for offline use)
- **Image Processing**: Pillow (PIL) - for fallback OCR only
- **HTTP Client**: `httpx` (async) or `requests`
- **Windows APIs**: `pywin32`, `comtypes` for Windows UI Automation

### Development Tools
- **Python**: Black (formatting), pytest (testing), mypy (type checking)
- **Node.js**: ESLint, Prettier
- **Version Control**: Git

### Packaging
- **Electron Builder**: For Windows installer (.exe, .msi)
- **PyInstaller**: Convert Python backend to standalone .exe
- **NSIS**: For creating Windows installer (via Electron Builder)

---

## 🚀 Implementation Phases

### Phase 1: Project Setup & Backend Foundation (Week 1)
**Goal**: Set up project structure and create basic Python backend API

#### Tasks:
1. **Initialize Project Structure**
   - Create directory structure
   - Initialize Git repository
   - Set up .gitignore

2. **Backend Setup**
   - Create Python virtual environment
   - Install FastAPI, uvicorn, and dependencies
   - Set up basic FastAPI app with health check endpoint
   - Configure logging
   - Create configuration management (config.py)
   - Set up environment variables for API keys

3. **API Design**
   - Design API endpoints:
     - `POST /api/analyze` - Main analysis endpoint
     - `GET /api/health` - Health check
     - `GET /api/status` - Backend status
   - Define request/response schemas (Pydantic models)

4. **Testing Infrastructure**
   - Set up pytest
   - Create test fixtures
   - Write basic API tests

**Deliverable**: Working FastAPI server with health check endpoint

---

### Phase 2: Screen Text Extraction Module (Week 1-2)
**Goal**: Extract all visible text directly from screen UI elements (not OCR)

In this phase we ensure that the system can **accurately capture all the visible text on the entire screen—exactly as it appears—without breaking or missing header fields, labels, or other UI elements**.  
In simple terms: **the solution is designed to extract every piece of text currently displayed on the screen as real text (not just a screenshot or image), giving the AI the complete on‑screen content to analyze.**

#### Tasks:
1. **Text Extraction Service (Primary Method)**
   - Implement `text_extractor.py` using Windows UI Automation API
   - Use `pywin32` and `comtypes` to access Windows accessibility APIs
   - Extract text from all visible windows and UI elements:
     - Window titles and headers
     - Text controls (labels, textboxes, etc.)
     - List items and table cells
     - Button text
     - Menu items
     - Status bars
   - Handle different application types:
     - Standard Windows applications (Win32, WPF)
     - Web browsers (Chrome, Edge, Firefox)
     - Electron apps (WhatsApp Desktop, etc.)
     - Office applications (Word, Outlook, etc.)
   - Preserve text structure and context (headers, fields, etc.)

2. **Text Aggregation**
   - Combine text from all visible windows
   - Maintain spatial context (which text belongs to which window/control)
   - Filter out system UI elements (taskbar, system notifications) if needed
   - Preserve text order and hierarchy

3. **Fallback Strategy**
   - Implement screenshot capture (`screenshot.py`) as fallback
   - Use when UI Automation is not available or fails
   - Support for applications that don't expose accessibility APIs

4. **Error Handling**
   - Handle permission issues gracefully
   - Fallback to screenshot+OCR when UI Automation fails
   - Log extraction method used for debugging

5. **Testing**
   - Test with various applications (Notepad, WhatsApp, Gmail, Word, etc.)
   - Test with different window configurations
   - Test error handling and fallback mechanisms
   - Verify all visible text is captured accurately

**Deliverable**: Working screen text extraction service that captures all visible text accurately

---

### Phase 3: OCR Fallback & Text Processing (Week 2)
**Goal**: Implement OCR as fallback method and process extracted text

#### Tasks:
1. **OCR Service Implementation (Fallback Only)**
   - Integrate `easyocr` library
   - Create `ocr.py` service
   - Process screenshot images when UI Automation fails
   - Extract and clean text from images
   - Handle multiple languages (English primary, add others later)

2. **Text Processing & Cleaning**
   - Clean extracted text (remove extra spaces, normalize newlines)
   - Extract URLs and email addresses using regex
   - Preserve important formatting (line breaks, paragraphs)
   - Remove duplicate text (if same text appears in multiple windows)
   - Structure text with context (window titles, field labels)

3. **Text Extraction Strategy**
   - Primary: Windows UI Automation (Phase 2)
   - Fallback 1: Screenshot + OCR for unsupported applications
   - Fallback 2: Alternative OCR engine (`pytesseract`) if `easyocr` fails
   - Automatic fallback when primary method fails

4. **Text Quality Assurance**
   - Validate extracted text quality
   - Compare UI Automation vs OCR results when both available
   - Log extraction method and confidence scores

5. **Testing**
   - Test fallback mechanisms
   - Test with applications that don't support UI Automation
   - Test OCR accuracy for fallback scenarios
   - Verify text structure is preserved

**Deliverable**: Complete text extraction system with OCR fallback and text processing

---

### Phase 4: AI Phishing Detection (Week 2-3)
**Goal**: Integrate LLM for phishing detection

#### Tasks:
1. **AI Service Implementation**
   - Create `ai_analyzer.py` service
   - Integrate OpenAI API (or chosen LLM)
   - Design effective phishing detection prompt
   - Parse LLM response into structured format

2. **Prompt Engineering**
   - Create comprehensive prompt for phishing detection
   - Include examples of phishing patterns
   - Request structured JSON response:
     ```json
     {
       "is_phishing": true/false,
       "risk_level": "low|medium|high",
       "reason": "detailed explanation",
       "suspicious_elements": ["url", "urgency", "threat"],
       "recommended_action": "ignore|report|verify"
     }
     ```

3. **Response Parsing**
   - Handle JSON response from LLM
   - Validate response structure
   - Handle API errors and rate limits

4. **Caching (Optional)**
   - Cache results for identical text inputs
   - Reduce API calls and costs

5. **Testing**
   - Test with known phishing examples
   - Test with safe text examples
   - Test error handling (API failures, invalid responses)

**Deliverable**: AI service that accurately detects phishing content

---

### Phase 5: Frontend - Electron Setup (Week 3)
**Goal**: Set up Electron application with React

#### Tasks:
1. **Electron Project Setup**
   - Initialize Electron project with Vite + React
   - Configure Electron Builder
   - Set up main process and renderer process
   - Configure preload script for security

2. **Window Management**
   - Create always-on-top floating widget window
   - Implement draggable functionality
   - Set window properties (transparent, frameless, etc.)
   - Handle window positioning and persistence

3. **Basic UI Components**
   - Create FloatingWidget component (circular button)
   - Add hover effects and animations
   - Implement click handlers

4. **Backend Communication**
   - Set up HTTP client to communicate with Python backend
   - Implement API client utility
   - Handle connection errors

**Deliverable**: Basic Electron app with floating widget button

**Status (current)**: Initial Electron + React scaffold completed with floating widget UI, API client stub, and development scripts.

---

### Phase 6: Frontend - Result Display (Week 3-4)
**Goal**: Create result modal and integrate with backend

#### Tasks:
1. **Result Modal Component**
   - Design and implement ResultModal component
   - Display phishing status (Safe/Phishing)
   - Show risk level with color coding
   - Display reason and recommended action
   - Add close button and animations

2. **Loading State**
   - Create LoadingSpinner component
   - Show loading state during analysis
   - Display progress or status messages

3. **Error Handling**
   - Handle backend connection errors
   - Display user-friendly error messages
   - Implement retry functionality

4. **UI/UX Polish**
   - Apply modern styling (TailwindCSS or styled-components)
   - Add smooth animations
   - Ensure responsive design
   - Add accessibility features

**Deliverable**: Complete UI with result display

---

### Phase 7: Integration & End-to-End Testing (Week 4)
**Goal**: Integrate all components and test complete workflow

#### Tasks:
1. **End-to-End Integration**
   - Connect Electron frontend to Python backend
   - Test complete workflow:
     - Click widget → Screen Text Extraction (entire visible screen) → Text Processing → AI → Display result
   - Verify that **all visible on‑screen text is captured exactly as it appears**, including headers, labels, buttons, and other UI elements
   - Handle edge cases

2. **Performance Optimization**
   - Optimize screenshot capture speed
   - Optimize OCR processing time
   - Cache AI responses where appropriate
   - Minimize memory usage

3. **Error Handling**
   - Test all error scenarios
   - Ensure graceful degradation
   - Add proper error messages

4. **User Testing**
   - Test with real-world scenarios
   - Test on different Windows versions
   - Test with various applications (Notepad, WhatsApp, Gmail, etc.)

**Status (current)**: Backend `/api/scan-screen` orchestrates text extraction → AI analysis; frontend widget now triggers full backend workflow. Remaining work: performance tuning, manual cross-app testing.

---

### Phase 8: Packaging & Distribution (Week 4-5)
**Goal**: Package application for Windows distribution

#### Tasks:
1. **Python Backend Packaging**
   - Use PyInstaller to create standalone .exe
   - Bundle all dependencies
   - Test standalone executable
   - Handle paths and resources correctly

2. **Electron Packaging**
   - Configure Electron Builder
   - Bundle Python backend with Electron app
   - Create Windows installer (.exe or .msi)
   - Add application icon
   - Configure auto-updater (optional)

3. **Installation Testing**
   - Test installer on clean Windows machine
   - Verify all dependencies are included
   - Test application launch and functionality
   - Verify uninstaller works

4. **Documentation**
   - Create user guide
   - Document installation steps
   - Create API documentation
   - Add troubleshooting guide

**Deliverable**: Windows installer ready for distribution

---

## 🔄 Development Workflow

### Daily Development Process
1. **Start Backend Server**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Start Electron Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Run Tests**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests (if added)
   cd frontend
   npm test
   ```

### Code Quality
- Use type hints in Python
- Follow PEP 8 style guide
- Use ESLint and Prettier for JavaScript/React
- Write unit tests for critical functions
- Document complex logic

### Version Control
- Use feature branches
- Commit frequently with descriptive messages
- Tag releases

---

## 🧪 Testing Strategy

### Unit Tests
- **Backend**: Test each service independently
  - Screen text extraction (UI Automation) – primary
  - Screenshot capture – fallback
  - OCR text extraction – fallback
  - AI analysis logic
  - API endpoints

### Integration Tests
- Test API endpoints with real data
- Test Electron-Python communication
- Test complete workflow

### End-to-End Tests
- Test full user flow
- Test with real applications (Notepad, WhatsApp, etc.)
- Test error scenarios

### Test Data
- Create synthetic screen layouts with known phishing text and safe text
- Create test images with known phishing text (for OCR fallback)
- Create test images with safe text (for OCR fallback)
- Test various text formats, fonts, and languages

---

## 📦 Packaging & Distribution

### Backend Packaging (PyInstaller)
```bash
cd backend
pyinstaller --onefile --name phishing-detector-backend main.py
```

### Frontend Packaging (Electron Builder)
```bash
cd frontend
npm run build
npm run dist
```

### Combined Package
- Electron Builder can bundle Python executable
- Or create installer that installs both components
- Ensure Python backend starts automatically with Electron

### Distribution Options
1. **Windows Installer (.exe/.msi)**
   - Single-click installation
   - Auto-start on boot (optional)
   - System tray integration (future enhancement)

2. **Portable Version**
   - No installation required
   - Run from USB drive

---

## 🔐 Security Considerations

1. **API Keys**
   - Store API keys in environment variables
   - Never commit keys to repository
   - Use .env file for local development

2. **Electron Security**
   - Use preload scripts
   - Disable node integration in renderer
   - Use context isolation

3. **Data Privacy**
   - Screenshots are temporary (delete after processing)
   - Text sent to AI (ensure API provider privacy policy)
   - No data stored locally (unless user opts in)

---

## 📊 Success Metrics

### Functionality
- ✅ Screen text extraction works on all Windows versions
- ✅ Text extraction accuracy: 100% (UI Automation) or > 90% (OCR fallback)
- ✅ Captures all visible text including headers, fields, UI elements
- ✅ Phishing detection accuracy > 95%
- ✅ Response time < 3 seconds end-to-end (faster than OCR)

### User Experience
- ✅ Widget is always accessible
- ✅ Results are clear and actionable
- ✅ No false positives for common safe text
- ✅ Works across all major applications

---

## 🚧 Future Enhancements (Post-MVP)

1. **Advanced Features**
   - Region selection for text extraction (specific window/area)
   - Multiple OCR language support (for fallback)
   - Local LLM option (Ollama)
   - History of scans
   - Whitelist/blacklist domains
   - Text extraction from specific applications only

2. **UI Improvements**
   - System tray integration
   - Keyboard shortcuts
   - Customizable widget position
   - Dark/light theme

3. **Performance**
   - Background processing
   - Batch analysis
   - Offline mode with local LLM

4. **Analytics**
   - Usage statistics (optional, privacy-respecting)
   - Detection accuracy tracking

---

## 📝 Next Steps

1. **Immediate Actions**
   - [ ] Set up project structure
   - [ ] Initialize Git repository
   - [ ] Create backend FastAPI skeleton
   - [ ] Set up frontend Electron project
   - [ ] Configure development environment

2. **Week 1 Goals**
   - [ ] Complete Phase 1 (Backend Foundation)
   - [ ] Complete Phase 2 (Screen Text Extraction – full on‑screen content)
   - [ ] Start Phase 3 (OCR Fallback & Text Processing)

3. **Week 2 Goals**
   - [ ] Complete Phase 3 (OCR Integration)
   - [ ] Complete Phase 4 (AI Phishing Detection)

4. **Week 3 Goals**
   - [ ] Complete Phase 5 (Electron Setup)
   - [ ] Complete Phase 6 (Result Display)

5. **Week 4 Goals**
   - [ ] Complete Phase 7 (Integration & Testing)
   - [ ] Complete Phase 8 (Packaging)

---

## 🛠️ Development Environment Setup

### Prerequisites
- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **Git** installed
- **Windows 10/11** development machine

### Initial Setup Commands

```bash
# Clone/create project
mkdir phishing-detector-widget
cd phishing-detector-widget

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Required API Keys
- OpenAI API key (or alternative LLM provider)
- Store in `.env` file (backend/.env)

---

**This plan provides a comprehensive roadmap for implementing the Windows Phishing Detector Widget. Follow phases sequentially, but feel free to adjust timelines based on development speed and requirements.**

