#!/usr/bin/env python3
"""Verify that the application is ready for Vercel deployment."""

import sys
import os

def check_files():
    """Check that all required files exist."""
    required_files = [
        'vercel.json',
        'requirements.txt',
        'api/index.py',
        'app/__init__.py',
        'app/config.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files present")
    return True

def check_imports():
    """Check that the app can be imported successfully."""
    try:
        from api.index import app
        print("✅ App imports successfully from api/index.py")
        return True
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        return False

def check_health_endpoint():
    """Check that the health endpoint works."""
    try:
        from api.index import app
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
                return True
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🔍 Verifying Vercel deployment readiness...\n")
    
    checks = [
        check_files,
        check_imports,
        check_health_endpoint
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All checks passed! Ready for Vercel deployment.")
        print("\nNext steps:")
        print("1. Install Vercel CLI: npm install -g vercel")
        print("2. Login: vercel login")
        print("3. Deploy: vercel")
        print("4. Deploy to production: vercel --prod")
    else:
        print("❌ Some checks failed. Please fix the issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()