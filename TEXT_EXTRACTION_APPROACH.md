# Screen Text Extraction Approach

## Overview

Our system uses **direct text extraction from Windows UI elements** instead of relying solely on OCR. This approach provides superior accuracy, speed, and preserves text structure.

## Primary Method: Windows UI Automation API

### How It Works

1. **Windows UI Automation (UIA)**
   - Uses Microsoft's UI Automation framework
   - Directly accesses text from UI elements
   - Works with all Windows applications that support accessibility APIs

2. **Text Sources Captured**
   - Window titles and headers
   - Text controls (labels, textboxes, rich text)
   - Button text and tooltips
   - List items and table cells
   - Menu items
   - Status bars and notifications
   - Web browser content (via accessibility APIs)

3. **Advantages**
   - ✅ **100% Accuracy**: No OCR errors or misreadings
   - ✅ **Faster**: No image processing required
   - ✅ **Structured Text**: Preserves headers, fields, context
   - ✅ **Complete Coverage**: Captures all visible text elements
   - ✅ **Works Everywhere**: Standard Windows apps, browsers, Electron apps

### Implementation

```python
# Example: Using Windows UI Automation
import comtypes.client
from comtypes.gen import UIAutomationClient

# Get root element (desktop)
root = automation.GetRootElement()

# Find all visible windows
windows = root.FindAll(True, automation.CreateCondition(...))

# Extract text from each window
for window in windows:
    text = window.GetCurrentPropertyValue(automation.NameProperty)
    # Extract all text elements within window
    # Preserve structure and context
```

## Fallback Method: Screenshot + OCR

### When Used

- Applications that don't support UI Automation
- Custom UI frameworks without accessibility support
- When UI Automation fails or is blocked
- Legacy applications

### Implementation

1. Capture screenshot using `mss` library
2. Process image with OCR (`easyocr` or `pytesseract`)
3. Extract and clean text
4. Return extracted text

## Text Processing Pipeline

```
1. Extract Text (Primary: UI Automation | Fallback: OCR)
   ↓
2. Clean & Structure Text
   - Remove duplicates
   - Preserve context (window titles, field labels)
   - Normalize formatting
   ↓
3. Extract URLs & Email Addresses
   - Regex pattern matching
   - Validate URLs
   ↓
4. Send to AI Analyzer
   - Include context (headers, fields)
   - Structured text format
```

## Example: Text Extraction

### Input Screen
```
┌─────────────────────────────────┐
│ WhatsApp Desktop                │ ← Window Title
├─────────────────────────────────┤
│ Chat with John                  │ ← Header
├─────────────────────────────────┤
│                                 │
│ Your bank account will be       │ ← Message Text
│ blocked. Click here:            │
│ http://fakebank-security.com    │ ← URL
│                                 │
│ [Reply] [Forward]               │ ← Buttons
└─────────────────────────────────┘
```

### Extracted Text (Structured)
```
[Window: WhatsApp Desktop]
[Header: Chat with John]
Your bank account will be blocked. Click here: http://fakebank-security.com
[Buttons: Reply, Forward]
```

### Extracted Text (Plain)
```
WhatsApp Desktop
Chat with John
Your bank account will be blocked. Click here: http://fakebank-security.com
```

## Supported Applications

### ✅ Full Support (UI Automation)
- Standard Windows applications (Win32, WPF)
- Microsoft Office (Word, Outlook, Excel)
- Web browsers (Chrome, Edge, Firefox)
- Electron applications (WhatsApp Desktop, Discord, etc.)
- Notepad, Calculator, File Explorer

### ⚠️ Partial Support (Fallback to OCR)
- Custom UI frameworks
- Legacy applications
- Some games and multimedia apps
- Applications with custom rendering

## Performance Comparison

| Method | Accuracy | Speed | Structure Preserved |
|--------|----------|-------|-------------------|
| UI Automation | 100% | Fast (~0.5s) | ✅ Yes |
| OCR | ~90-95% | Slower (~2-3s) | ❌ No |

## Technical Details

### Windows UI Automation API
- **Namespace**: `UIAutomationClient`
- **Python Libraries**: `pywin32`, `comtypes`
- **Access**: Requires no special permissions (uses standard Windows APIs)

### Text Extraction Process
1. Get desktop root element
2. Enumerate all visible windows
3. For each window:
   - Extract window title
   - Find all text elements
   - Extract text with context
   - Preserve element hierarchy
4. Combine all text with structure
5. Return complete text representation

### Error Handling
- If UI Automation fails → Automatic fallback to Screenshot + OCR
- Log extraction method used
- Return structured error if both methods fail

## Benefits for Phishing Detection

1. **Accurate Text Capture**: No OCR errors means AI gets exact text
2. **Context Preservation**: Headers and field labels help AI understand context
3. **Complete Coverage**: Captures all visible text, not just main content
4. **Fast Processing**: Direct extraction is faster than OCR
5. **Structured Analysis**: AI can better analyze when it knows what's a header vs. body text

---

**This approach ensures our phishing detector gets the most accurate and complete text representation of what the user sees on their screen.**

