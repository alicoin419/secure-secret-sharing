#!/usr/bin/env python3
"""
Secure Secret Sharing Tool - Main Entry Point

A private, secure, offline tool for generating and splitting sensitive secrets
using Shamir's Secret Sharing scheme.

SECURITY NOTICE: This tool should only be used on air-gapped devices.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.crypto.security import SecurityValidator
from src.gui.main_window import SecretSharingGUI

def main():
    """Main entry point for the application."""
    print("=" * 60)
    print("🔒 SECURE SECRET SHARING TOOL")
    print("=" * 60)
    print("SECURITY WARNING: Use only on air-gapped devices!")
    print("=" * 60)
    
    # Perform security validation before starting
    validator = SecurityValidator()
    
    print("🔍 Performing security checks...")
    
    # Check for CSPRNG availability
    if not validator.verify_csprng():
        print("❌ CRITICAL: No cryptographically secure random number generator available!")
        print("   This system is NOT safe for generating secrets.")
        sys.exit(1)
    
    print("✅ CSPRNG verification passed")
    
    # Check network isolation (basic check)
    if not validator.check_network_isolation():
        print("⚠️  WARNING: Network interfaces detected!")
        print("   Ensure this device is properly air-gapped.")
        response = input("   Continue anyway? (yes/no): ").lower()
        if response != 'yes':
            print("Exiting for security.")
            sys.exit(1)
    
    print("✅ Security checks completed")
    print("🚀 Starting application...")
    
    try:
        # Start the GUI application
        app = SecretSharingGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)
    finally:
        # Ensure any remaining sensitive data is cleared
        validator.clear_memory()
        print("🧹 Memory cleared")

if __name__ == "__main__":
    main()
