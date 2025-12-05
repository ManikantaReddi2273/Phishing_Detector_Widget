# Running Flutter App on Windows Desktop

## ⚠️ Important: Run on Windows Desktop, NOT Web

The `window_manager` plugin **only works on desktop platforms** (Windows, macOS, Linux), **NOT on web**.

If you see the error:
```
MissingPluginException(No implementation found for method ensureInitialized on channel window_manager)
```

This means the app is running in **web mode** instead of **Windows desktop mode**.

---

## ✅ **Correct Way to Run**

### **Step 1: Check Available Devices**
```bash
cd frontend_flutter
flutter devices
```

You should see something like:
```
Windows (desktop) • windows • windows-x64 • Microsoft Windows [Version 10.0.19045]
Chrome (web)      • chrome  • web-javascript • Google Chrome 120.0.0.0
```

### **Step 2: Run on Windows Desktop (NOT web)**
```bash
flutter run -d windows
```

**NOT:**
- ❌ `flutter run` (might default to web)
- ❌ `flutter run -d chrome` (web mode)
- ❌ `flutter run -d web` (web mode)

### **Step 3: Verify It's Running on Desktop**
When running correctly, you should see:
- A small floating window appears on your desktop (not in a browser)
- The window is always-on-top
- The window is draggable
- No browser window opens

---

## 🔧 **Troubleshooting**

### **Issue: "No Windows desktop device found"**

**Solution:** Enable Windows desktop support:
```bash
flutter config --enable-windows-desktop
flutter doctor
```

### **Issue: "Windows toolchain not found"**

**Solution:** Install Visual Studio with C++ desktop development:
1. Download Visual Studio Community (free)
2. Install "Desktop development with C++" workload
3. Run `flutter doctor` to verify

### **Issue: Still running in web mode**

**Solution:** Explicitly specify Windows:
```bash
# Check available devices
flutter devices

# Run specifically on Windows
flutter run -d windows

# Or build for Windows
flutter build windows
```

---

## 📝 **Code Changes Made**

The code has been updated to:
- ✅ Detect if running on web (`kIsWeb`)
- ✅ Only use `window_manager` on desktop platforms
- ✅ Gracefully handle web mode (for testing, but window features won't work)

---

## 🎯 **Expected Behavior**

### **On Windows Desktop:**
- ✅ Floating widget appears
- ✅ Always-on-top window
- ✅ Draggable widget
- ✅ Automatic polling works
- ✅ Auto-alerts work

### **On Web (for testing only):**
- ✅ App runs without crashing
- ⚠️ Window features don't work (no always-on-top, no dragging)
- ✅ Polling and alerts still work

---

## 🚀 **Quick Start**

```bash
# 1. Navigate to Flutter directory
cd frontend_flutter

# 2. Get dependencies
flutter pub get

# 3. Ensure backend is running
# (In another terminal: cd backend && python main.py)

# 4. Run on Windows desktop
flutter run -d windows
```

---

## 📋 **Checklist**

Before running, ensure:
- [ ] Flutter is installed: `flutter --version`
- [ ] Windows desktop support is enabled: `flutter config --enable-windows-desktop`
- [ ] Visual Studio with C++ is installed (if building)
- [ ] Backend is running on `http://127.0.0.1:8000`
- [ ] You're using `flutter run -d windows` (not web)

---

## 🐛 **Still Having Issues?**

1. **Check Flutter doctor:**
   ```bash
   flutter doctor -v
   ```

2. **Clean and rebuild:**
   ```bash
   flutter clean
   flutter pub get
   flutter run -d windows
   ```

3. **Check backend is running:**
   ```bash
   curl http://127.0.0.1:8000/api/health
   ```

4. **Verify Windows desktop support:**
   ```bash
   flutter config
   flutter devices
   ```

