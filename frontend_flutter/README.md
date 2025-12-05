# Phishing Detector Flutter Frontend

A Flutter desktop application that provides a floating, always-on-top widget for real-time phishing detection.

## Features

- ✅ **Floating Widget**: Always-on-top, draggable overlay on your desktop
- ✅ **Automatic Scanning**: Continuously polls backend for phishing detection results
- ✅ **Auto-Alert**: Automatically shows alert dialog when phishing is detected
- ✅ **Real-time Status**: Visual indicator showing current status (Safe/Phishing/Scanning/Error)
- ✅ **No Manual Interaction**: Fully automatic - no clicks required

## Prerequisites

- **Flutter 3.0+** with Windows desktop support enabled
- **Windows 10/11**
- **Backend server** running on `http://127.0.0.1:8000`

## Setup Instructions

1. **Navigate to Flutter frontend directory**
   ```bash
   cd frontend_flutter
   ```

2. **Get dependencies**
   ```bash
   flutter pub get
   ```

3. **Ensure backend is running**
   - The backend server must be running on `http://127.0.0.1:8000`
   - Start the backend: `cd backend && python main.py`

4. **Run the Flutter app (Windows desktop)**
   ```bash
   flutter run -d windows
   ```

   The Flutter window will appear as a small, always-on-top, draggable overlay.

## How It Works

1. **Automatic Polling**: The app polls `/api/latest-scan` every 3 seconds
2. **Status Display**: The floating widget shows current status:
   - 🟢 **SAFE**: No phishing detected
   - 🔴 **PHISHING**: Phishing content detected
   - 🟠 **SCANNING**: Currently scanning
   - ⚪ **ERROR**: Connection or backend error
3. **Auto-Alert**: When phishing is detected, an alert dialog automatically appears showing:
   - Risk level
   - Detailed reason
   - Suspicious elements
   - URLs found
   - Recommended action
4. **Draggable**: Click and drag the widget to move it anywhere on screen

## Project Structure

```
lib/
├── main.dart                    # App entry point, window configuration
├── models/
│   └── analyze_response.dart   # API response models
├── services/
│   ├── api_client.dart          # HTTP client for backend API
│   └── scanner_service.dart     # Continuous polling service
└── widgets/
    ├── floating_widget.dart     # Status indicator widget
    └── phishing_alert_dialog.dart  # Alert dialog for phishing results
```

## Configuration

The backend URL is configured in `lib/services/api_client.dart`:
```dart
static const String baseUrl = 'http://127.0.0.1:8000/api';
```

To change the polling interval, modify `lib/services/scanner_service.dart`:
```dart
final Duration pollInterval = const Duration(seconds: 3);
```

## Building for Distribution

```bash
flutter build windows
```

The executable will be in `build/windows/runner/Release/`

## Troubleshooting

- **Widget not appearing**: Check that backend is running and accessible
- **No alerts showing**: Verify backend is scanning and detecting phishing content
- **Connection errors**: Ensure backend is running on `http://127.0.0.1:8000`
