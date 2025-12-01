"""
Setup verification script for Phase 1
Run this to verify your backend setup is correct
"""
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_project_structure():
    """Check if project structure is correct"""
    base_dir = Path(__file__).parent
    required_dirs = [
        "app",
        "app/api",
        "app/core",
        "app/models",
        "app/services",
        "tests"
    ]
    
    all_present = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            print(f"❌ Missing directory: {dir_path}")
            all_present = False
        else:
            print(f"✓ Directory exists: {dir_path}")
    
    return all_present

def check_required_files():
    """Check if required files exist"""
    base_dir = Path(__file__).parent
    required_files = [
        "main.py",
        "requirements.txt",
        "pytest.ini",
        "app/__init__.py",
        "app/core/config.py",
        "app/core/logger.py",
        "app/api/routes.py",
        "app/models/schemas.py",
        "tests/conftest.py",
        "tests/test_api.py"
    ]
    
    all_present = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            print(f"❌ Missing file: {file_path}")
            all_present = False
        else:
            print(f"✓ File exists: {file_path}")
    
    return all_present

def check_dependencies():
    """Check if dependencies can be imported (after installation)"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✓ Core dependencies available")
        return True
    except ImportError as e:
        print(f"⚠ Dependencies not installed. Run: pip install -r requirements.txt")
        print(f"  Error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 50)
    print("Phishing Detector Backend - Setup Verification")
    print("=" * 50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Required Files", check_required_files),
        ("Dependencies", check_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Create virtual environment: python -m venv venv")
        print("2. Activate it: venv\\Scripts\\activate")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Copy .env.example to .env and configure API keys")
        print("5. Run server: python main.py")
    else:
        print("⚠ Some checks failed. Please review the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

