#!/usr/bin/env python3
"""
Build script for creating the Secure Secret Sharing executable.

This script creates a standalone Windows executable that can run on any
Windows machine without requiring Python to be installed.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_directories():
    """Clean any existing build directories."""
    print("🧹 Cleaning build directories...")
    
    directories_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in directories_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean Python cache files recursively
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:  # Use slice to avoid modifying list while iterating
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)
        for file_name in files:
            if file_name.endswith('.pyc'):
                os.remove(os.path.join(root, file_name))

def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")
    
    # Get the Python executable path
    python_exe = sys.executable
    
    # Build using the spec file
    cmd = [python_exe, "-m", "PyInstaller", "--clean", "SecureSecretSharing.spec"]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_distribution_package():
    """Create a distribution package with documentation."""
    print("📦 Creating distribution package...")
    
    dist_dir = Path("dist")
    exe_path = dist_dir / "SecureSecretSharing.exe"
    
    if not exe_path.exists():
        print("❌ Executable not found!")
        return False
    
    # Create distribution folder
    package_dir = dist_dir / "SecureSecretSharing_Portable"
    package_dir.mkdir(exist_ok=True)
    
    # Copy executable
    shutil.copy2(exe_path, package_dir / "SecureSecretSharing.exe")
    
    # Copy documentation
    docs_to_copy = [
        "README.md",
        "ORDER_ACCURACY_GUARANTEE.md",
        "CLEANUP_SUMMARY.md"
    ]
    
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, package_dir / doc)
    
    # Copy docs folder if it exists
    if os.path.exists("docs"):
        shutil.copytree("docs", package_dir / "docs", dirs_exist_ok=True)
    
    # Create a quick start guide
    quick_start = package_dir / "QUICK_START.txt"
    with open(quick_start, 'w') as f:
        f.write("""SECURE SECRET SHARING TOOL - QUICK START
========================================

SECURITY WARNING: Use only on air-gapped devices!

USAGE:
1. Double-click SecureSecretSharing.exe to start
2. Follow the on-screen security warnings
3. Use the GUI to generate or reconstruct secrets

FEATURES:
- Shamir's Secret Sharing with Base62 encoding
- Modern dark theme GUI
- Automatic clipboard management
- Minimum 250-character shares
- Support for secrets up to 50,000 characters
- Order-preserving reconstruction guarantee

DOCUMENTATION:
- README.md - Complete setup and usage guide
- ORDER_ACCURACY_GUARANTEE.md - Technical guarantees
- docs/ - Detailed documentation folder

For support or technical details, see the documentation files.
""")
    
    print(f"✅ Distribution package created: {package_dir}")
    print(f"📁 Executable size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True

def main():
    """Main build process."""
    print("=" * 60)
    print("🔒 SECURE SECRET SHARING TOOL - BUILD SCRIPT")
    print("=" * 60)
    
    # Step 1: Clean
    clean_build_directories()
    
    # Step 2: Build
    if not build_executable():
        print("❌ Build failed!")
        sys.exit(1)
    
    # Step 3: Package
    if not create_distribution_package():
        print("❌ Packaging failed!")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("📦 Your portable executable is ready in:")
    print("   dist/SecureSecretSharing_Portable/")
    print("")
    print("🚀 You can now copy this folder to any Windows machine")
    print("   and run SecureSecretSharing.exe without installing Python!")
    print("=" * 60)

if __name__ == "__main__":
    main()
