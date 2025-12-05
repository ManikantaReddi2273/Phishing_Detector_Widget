# Architecture Update: Flutter Frontend + Auto-Detection

## Summary of Changes

This document describes the architectural changes made to replace the Electron frontend with Flutter and implement automatic phishing detection.

---

## ✅ **Changes Implemented**

### 1. **Frontend Replacement**
- ❌ **Removed**: Electron + React + TypeScript frontend
- ✅ **Added**: Flutter Desktop frontend with floating widget

### 2. **OCR Removal**
- ❌ **Removed**: All OCR-related code and dependencies
- ✅ **Updated**: Comments/docs to reflect Windows UI Automation only
- ✅ **Verified**: No OCR code exists in backend (only comments updated)

### 3. **Manual Click Removal**
- ❌ **Removed**: Manual "click to scan" mechanism
- ✅ **Added**: Automatic continuous polling of `/api/latest-scan` endpoint

### 4. **Auto-Detection**
- ✅ **Implemented**: Continuous background scanning (already existed in backend)
- ✅ **Added**: Flutter auto-polling service (every 3 seconds)
- ✅ **Added**: Automatic alert dialog when phishing detected

### 5. **LLM-Only Detection**
- ✅ **Verified**: Backend already uses LLM-only detection (OpenAI API)
- ✅ **Confirmed**: No fallback ML models or rule-based heuristics exist

---

## 🏗️ **New Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              FLUTTER FRONTEND (Desktop)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  main.dart (Window Setup)                             │  │
│  │  - Always-on-top, frameless, transparent              │  │
│  │  - Draggable widget                                   │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                            │                                 │
│  ┌─────────────────────────▼──────────────────────────────┐  │
│  │  FloatingWidgetScreen                                    │  │
│  │  - State management                                      │  │
│  │  - ScannerService integration                           │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼──────────────────────────────────┐  │
│  │  ScannerService (Auto-Polling)                           │  │
│  │  - Polls /api/latest-scan every 3 seconds                │  │
│  │  - Updates status on response                            │  │
│  │  - Triggers alert on phishing detection                  │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼──────────────────────────────────┐  │
│  │  ApiClient                                              │  │
│  │  - HTTP client for backend API                          │  │
│  │  - GET /api/latest-scan                                 │  │
│  └───────────────────────┬──────────────────────────────────┘  │
└──────────────────────────┼─────────────────────────────────────┘
                           │ HTTP GET /api/latest-scan
                           │ (every 3 seconds)
┌──────────────────────────▼─────────────────────────────────────┐
│              BACKEND (Python FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  scanner.py (Background Scanner)                       │  │
│  │  - Runs every 5 seconds                                │  │
│  │  - Extracts screen text via UI Automation              │  │
│  │  - Analyzes with OpenAI LLM                           │  │
│  │  - Stores latest result in memory                      │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼──────────────────────────────────┐  │
│  │  routes.py → GET /api/latest-scan                      │  │
│  │  - Returns latest scan result from memory               │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 **File Structure**

### **New Flutter Files**
```
frontend_flutter/lib/
├── main.dart                          # App entry, window config
├── models/
│   └── analyze_response.dart         # API response models
├── services/
│   ├── api_client.dart                # HTTP client
│   └── scanner_service.dart           # Auto-polling service
└── widgets/
    ├── floating_widget.dart          # Status indicator
    └── phishing_alert_dialog.dart    # Alert dialog
```

### **Backend Files Modified**
- `backend/app/models/schemas.py` - Updated OCR comment
- `backend/app/services/text_processing.py` - Updated OCR comment
- `backend/app/services/__init__.py` - Updated OCR comment

### **Backend Files (No Changes Needed)**
- `backend/app/services/scanner.py` - Already implements continuous scanning
- `backend/app/services/ai_analyzer.py` - Already LLM-only
- `backend/app/services/text_extractor.py` - Already UI Automation only

---

## 🔄 **Complete Workflow**

### **Automatic Detection Flow**

1. **Backend Startup**
   ```
   main.py → start_background_scanner()
   ↓
   scanner.py → _scan_loop() starts
   ↓
   Every 5 seconds:
     - extract_screen_text() (UI Automation)
     - process_text_for_analysis()
     - analyze_with_llm() (OpenAI)
     - Store result in memory
   ```

2. **Flutter Startup**
   ```
   main.dart → Window setup (always-on-top, frameless)
   ↓
   FloatingWidgetScreen → ScannerService.start()
   ↓
   Every 3 seconds:
     - ApiClient.getLatestScan()
     - GET /api/latest-scan
     - Update status widget
     - Show alert if phishing detected
   ```

3. **Phishing Detection**
   ```
   Backend detects phishing
   ↓
   Result stored in memory
   ↓
   Flutter polls and receives result
   ↓
   Status widget turns RED
   ↓
   Alert dialog automatically appears
   ↓
   User sees detailed phishing information
   ```

---

## 🎯 **Key Features**

### **1. Floating Widget**
- Always-on-top overlay
- Draggable (click and drag)
- Visual status indicator:
  - 🟢 Green = Safe
  - 🔴 Red = Phishing
  - 🟠 Orange = Scanning
  - ⚪ Grey = Error

### **2. Automatic Polling**
- Polls `/api/latest-scan` every 3 seconds
- No user interaction required
- Real-time status updates

### **3. Auto-Alert**
- Automatically shows alert dialog when phishing detected
- Displays:
  - Risk level (low/medium/high/critical)
  - Detailed reason
  - Suspicious elements
  - URLs found
  - Recommended action
  - Confidence score

### **4. Full Screen Text Detection**
- Backend uses Windows UI Automation
- Captures ALL visible text, including scrolled content
- No visual area limitations
- Works with any Windows application

---

## 🔧 **Configuration**

### **Backend**
- Scan interval: `SCAN_INTERVAL_SECONDS=5` (in `.env`)
- API endpoint: `http://127.0.0.1:8000`
- OpenAI model: `gpt-4o-mini`

### **Flutter**
- Poll interval: 3 seconds (in `scanner_service.dart`)
- Backend URL: `http://127.0.0.1:8000/api` (in `api_client.dart`)
- Window size: 100x100 pixels (in `main.dart`)

---

## 🚀 **Running the System**

### **1. Start Backend**
```bash
cd backend
python main.py
```

### **2. Start Flutter Frontend**
```bash
cd frontend_flutter
flutter run -d windows
```

### **3. System Behavior**
- Flutter widget appears as floating overlay
- Backend continuously scans active window
- Flutter polls for results every 3 seconds
- Alert appears automatically when phishing detected

---

## ✅ **Requirements Met**

- ✅ Flutter Desktop frontend implemented
- ✅ OCR completely removed (only comments updated)
- ✅ Floating widget with always-on-top behavior
- ✅ Draggable widget
- ✅ Manual click removed
- ✅ Automatic continuous scanning
- ✅ Auto-alert on phishing detection
- ✅ LLM-only detection (already implemented)
- ✅ Full screen text detection (UI Automation)

---

## 📝 **Notes**

- The backend continuous scanner was already implemented
- Only the Flutter frontend needed to be built
- OCR was never actually implemented (only mentioned in comments)
- LLM-only detection was already the only method used

---

## 🔮 **Future Enhancements**

- System tray integration
- Configurable polling interval
- History of detections
- Whitelist/blacklist domains
- Customizable alert styles
- Sound notifications

