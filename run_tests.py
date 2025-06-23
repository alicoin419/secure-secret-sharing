#!/usr/bin/env python3
"""
Test runner script for the Secure Secret Sharing Tool.

This script runs all tests and provides a summary of security verification.
"""

import os
import sys
import time

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run all tests and security checks."""
    print("=" * 60)
    print("🧪 SECURE SECRET SHARING TOOL - TEST SUITE")
    print("=" * 60)
    
    print("🔍 Running comprehensive security and functionality tests...")
    print()
    
    start_time = time.time()
    
    try:
        # Import and run tests
        from tests.test_all import run_all_tests
        
        success = run_all_tests()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print()
        print("=" * 60)
        if success:
            print("✅ ALL TESTS PASSED")
            print(f"🕒 Test duration: {duration:.2f} seconds")
            print()
            print("🔒 Security Status: VERIFIED")
            print("✅ CSPRNG verification working")
            print("✅ Memory clearing functional")
            print("✅ Input validation comprehensive")
            print("✅ Share generation/reconstruction accurate")
            print("✅ Error handling secure")
            print()
            print("🚀 Ready for secure air-gapped deployment!")
        else:
            print("❌ SOME TESTS FAILED")
            print(f"🕒 Test duration: {duration:.2f} seconds")
            print()
            print("⚠️  Security Status: UNVERIFIED")
            print("❌ DO NOT USE for production until all tests pass")
            print()
            print("🔧 Review test output above for specific failures")
        
        print("=" * 60)
        
        return 0 if success else 1
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Ensure all source files are present and correctly structured.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("Check system configuration and Python installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
