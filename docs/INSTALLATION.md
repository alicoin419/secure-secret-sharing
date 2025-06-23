# Installation Guide - Secure Secret Sharing Tool

## 🎯 Prerequisites

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.7 or higher (3.9+ recommended)
- **Memory**: Minimum 512MB RAM available
- **Storage**: 50MB free space
- **Network**: None required (air-gapped operation recommended)

### Security Requirements
- ✅ Dedicated, air-gapped device (strongly recommended)
- ✅ Physical security for the device
- ✅ Clean, malware-free operating system
- ✅ No active network connections during use

## 🔧 Installation Steps

### Option 1: Direct Download (Recommended for Air-gapped)

1. **Download Source Code**
   - Download the complete source code to a USB drive on a network-connected device
   - Transfer to your air-gapped device
   - Extract to a secure location (e.g., `C:\SecretSharing\`)

2. **Verify Python Installation**
   ```bash
   python --version
   ```
   Should show Python 3.7 or higher.

3. **Test Installation**
   ```bash
   cd "C:\SecretSharing"
   python main.py
   ```

### Option 2: Git Clone (For Development)

⚠️ **Only use this method on development systems, not production air-gapped devices**

```bash
git clone https://github.com/username/cryptovault.git secure-secret-sharing
cd secure-secret-sharing
python main.py
```

### Option 3: Manual Setup

1. **Create Directory Structure**
   ```
   SecretSharing/
   ├── main.py
   ├── README.md
   ├── src/
   │   ├── __init__.py
   │   ├── crypto/
   │   │   ├── __init__.py
   │   │   ├── security.py
   │   │   └── shamir.py
   │   ├── gui/
   │   │   ├── __init__.py
   │   │   └── main_window.py
   │   └── utils/
   │       ├── __init__.py
   │       └── validators.py
   ├── tests/
   │   └── test_all.py
   └── docs/
       ├── USAGE_GUIDE.md
       ├── SECURITY_REVIEW.md
       └── INSTALLATION.md
   ```

2. **Copy Source Files**
   - Copy all source files to the created structure
   - Ensure file permissions are set correctly

## 🧪 Verification Steps

### 1. Security Check
```bash
python main.py
```
Should display:
```
============================================================
🔒 SECURE SECRET SHARING TOOL
============================================================
SECURITY WARNING: Use only on air-gapped devices!
============================================================
🔍 Performing security checks...
✅ CSPRNG verification passed
⚠️  WARNING: Network interfaces detected!
   Ensure this device is properly air-gapped.
   Continue anyway? (yes/no):
```

### 2. Run Test Suite
```bash
python tests/test_all.py
```
Should show all tests passing:
```
test_basic_secret_sharing ... ok
test_csprng_verification ... ok
test_memory_clearing ... ok
...
Ran XX tests in X.XXXs

OK
```

### 3. Functional Test
1. Launch the application
2. Generate a test secret
3. Split it into shares
4. Reconstruct from shares
5. Verify the result matches

## 🔒 Security Hardening

### Air-gap Configuration

#### Network Disconnection
```bash
# Windows
ipconfig /release
netsh interface set interface "Wi-Fi" disabled
netsh interface set interface "Ethernet" disabled

# Linux
sudo ifconfig wlan0 down
sudo ifconfig eth0 down

# macOS
sudo ifconfig en0 down
sudo ifconfig en1 down
```

#### Verify Network Isolation
```bash
ping google.com  # Should fail
```

### System Hardening

#### Windows
1. **Disable Windows Update** during secret operations
2. **Disable Windows Defender** real-time scanning (temporarily)
3. **Close unnecessary applications**
4. **Disable swap file** (if possible)

#### Linux
1. **Disable network services**
   ```bash
   sudo systemctl stop NetworkManager
   sudo systemctl stop bluetooth
   ```
2. **Clear swap**
   ```bash
   sudo swapoff -a
   sudo swapon -a
   ```
3. **Minimal running processes**

#### macOS
1. **Turn off Wi-Fi and Bluetooth**
2. **Disable automatic updates**
3. **Close unnecessary applications**

## 🚨 Troubleshooting

### Common Installation Issues

#### "Python not found"
**Solution**: Install Python 3.7+ from python.org
- Download installer
- Check "Add to PATH" during installation
- Restart terminal/command prompt

#### "ModuleNotFoundError"
**Cause**: Missing standard library modules
**Solution**: Reinstall Python with standard library

#### "Permission denied"
**Solution**: Run as administrator or fix file permissions
```bash
# Windows (as administrator)
python main.py

# Linux/macOS
chmod +x main.py
python main.py
```

#### "CSPRNG verification failed"
**Cause**: System lacks secure random number generation
**Solution**: 
- Update Python to latest version
- Check system entropy: `cat /proc/sys/kernel/random/entropy_avail` (Linux)
- Try different system if problem persists

### Security-Related Issues

#### "Network interfaces detected" warning
**Expected behavior** - Confirms network isolation check is working
**Action**: Disconnect all networks or continue with "yes" if testing

#### Test failures
**Critical**: If security tests fail, do not use for production
**Action**: 
1. Check Python version compatibility
2. Verify clean system state
3. Review error messages
4. Consider using different system

## 📁 File Structure Explanation

### Core Application Files
- `main.py` - Application entry point with security checks
- `src/crypto/` - Cryptographic implementations (Shamir's Secret Sharing)
- `src/gui/` - User interface components
- `src/utils/` - Input validation and utility functions

### Documentation
- `README.md` - Project overview and quick start
- `docs/USAGE_GUIDE.md` - Detailed usage instructions  
- `docs/SECURITY_REVIEW.md` - Security audit and considerations
- `docs/INSTALLATION.md` - This file

### Testing
- `tests/test_all.py` - Comprehensive test suite

## 🔄 Updates and Maintenance

### Checking for Updates
⚠️ **Only check for updates on network-connected, non-production systems**

### Applying Updates
1. Download updates on network-connected system
2. Transfer via secure media (USB) to air-gapped system
3. Backup current version before updating
4. Run full test suite after update
5. Verify security checks still pass

### Version Management
- Keep record of current version
- Maintain backups of working versions
- Document any customizations made

## 🛡️ Production Deployment Checklist

### Before First Use
- [ ] Python 3.7+ installed and verified
- [ ] All source files correctly placed
- [ ] Full test suite passes
- [ ] Security checks pass
- [ ] Network disconnected and verified
- [ ] Physical security measures in place
- [ ] Backup procedures established

### Before Each Session
- [ ] System is air-gapped
- [ ] No unauthorized access possible
- [ ] Application launches without errors
- [ ] Clear any sensitive data from previous sessions
- [ ] Verify system time is reasonable (for any logs)

### After Each Session
- [ ] Clear all application data
- [ ] Clear system clipboard
- [ ] Clear browser history (if used for any research)
- [ ] Consider system restart for memory clearing
- [ ] Secure storage of any generated shares

---

**Installation Support**: If you encounter issues not covered here, check the security review documentation or contact your security team.
