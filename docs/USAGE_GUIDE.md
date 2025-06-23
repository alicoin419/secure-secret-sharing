# Usage Guide - Secure Secret Sharing Tool

## 🚀 Quick Start

### 1. Launch the Application
```bash
python main.py
```

The application will automatically perform security checks:
- ✅ CSPRNG verification
- ⚠️ Network isolation check
- 🧹 Memory clearing capabilities

### 2. Choose Your Operation Mode

The application provides two main functions through a tabbed interface:

## 🔀 Split Secret Tab

### Purpose
Split any secret into multiple shares using Shamir's Secret Sharing scheme.

### Steps
1. **Enter Secret**: Type or paste your secret in the text area
2. **Set Parameters**:
   - **Total Shares**: Number of shares to create (2-20 recommended)
   - **Threshold**: Minimum shares needed for reconstruction (2 to total shares)
3. **Split Secret**: Click "🔀 Split Secret"
4. **Save Shares**: Copy individual shares and store them securely in separate locations

### Parameters Guide
- **5 shares, 3 threshold**: Good for personal use (store shares in 5 different secure locations)
- **7 shares, 4 threshold**: Good for team use (distribute among 7 trusted parties)
- **3 shares, 2 threshold**: Minimum security (only for low-value secrets)

### Example
```
Secret: "MySecretSeedPhrase123"
Parameters: 5 total shares, 3 threshold

Generated Shares:
Share 1: 01-4d7953656372657453656564506872617365313233
Share 2: 02-5e8464766463686547774655507162727366323334
Share 3: 03-6f9575877574797548885766508273838467343435
Share 4: 04-708686988685808659996877619384949578454546
Share 5: 05-819797a99796919760aa7988720495a60689565657
```

## 🔄 Reconstruct Secret Tab

### Purpose
Reconstruct the original secret from shares.

### Steps
1. **Enter Shares**: Paste shares (one per line) in the text area
2. **Format**: Shares are Base62 encoded strings (66-70 characters of letters and numbers)
3. **Reconstruct**: Click "🔄 Reconstruct Secret"
4. **Copy Result**: Use "📋 Copy Secret" to get the reconstructed secret

### Supported Formats
```
# Format 1: Base62 shares (new format)
YGJbbKjpPdLsI1cwjtXOAxVG29UGhVJ4vyqZUSZ3nZCPFHOQMiimRSlbgRrmIt1Lnb
ZGJccKkqPeLtJ2dxkuYPByHG30VHiWK5wzrAVTa4oaCQGIPRNjjnSSmchSsnJu2Mnc
AGKddLlrQfMuK3eylvZQCzIG41WIjXL6x0sBWUb5pbDRHJQSOkkqTTndcTtlKv3Nod

# Format 2: Legacy hex format (backward compatibility)
01-4d7953656372657453656564506872617365313233
02-5e8464766463686547774655507162727366323334
03-6f9575877574797548885766508273838467343435

# Format 3: Mixed with extra spacing
Share 1: 01-4d7953656372657453656564506872617365313233

02-5e8464766463686547774655507162727366323334

Share 3: 03-6f9575877574797548885766508273838467343435
```

## 🔒 Security Best Practices

### Before Use
1. **Air-gap Device**: Disconnect all network connections
2. **Clean Environment**: Use a trusted, malware-free device
3. **Physical Security**: Ensure privacy and no unauthorized access

### During Use
1. **Clear Data**: Use "🧹 Clear All Data" button frequently
2. **Minimize Exposure**: Work quickly to reduce secret exposure time
3. **No Screenshots**: Never capture screens containing secrets

### After Use
1. **Clear Clipboard**: Clipboard auto-clears after 30 seconds
2. **Restart Device**: Consider restarting for complete memory clearing
3. **Secure Storage**: Store shares in separate, secure locations

### Share Distribution
- **Never store all shares together**
- **Use different storage methods** (encrypted drives, paper, secure clouds)
- **Geographic distribution** for disaster recovery
- **Trusted parties only** for share custody

## ⚠️ Important Warnings

### Do NOT:
- ❌ Use on network-connected devices during secret operations
- ❌ Store shares in the same location
- ❌ Share more than necessary for reconstruction
- ❌ Take screenshots or photos of secrets/shares
- ❌ Use for production systems without independent security audit

### DO:
- ✅ Test reconstruction before relying on shares
- ✅ Keep backup of original secret until shares are verified
- ✅ Document your threshold requirements
- ✅ Plan for share recovery procedures
- ✅ Regularly test your backup and recovery process

## 🧪 Testing Your Setup

### Before Production Use
1. **Test with dummy data**: Create and reconstruct test secrets
2. **Verify share format**: Ensure shares are properly formatted
3. **Test reconstruction**: Verify you can reconstruct with threshold shares
4. **Test partial reconstruction**: Verify insufficient shares fail appropriately

### Example Test
```
1. Generate test secret: "TestSecret123"
2. Split into 5 shares, threshold 3
3. Reconstruct using shares 1, 3, 5
4. Verify result matches original: "TestSecret123"
5. Try with only 2 shares - should fail or be incomplete
```

## 📋 Troubleshooting

### Common Issues

#### "CSPRNG verification failed"
- **Cause**: System lacks secure random number generation
- **Solution**: Use a different system with proper security support

#### "Share validation failed"
- **Cause**: Malformed share strings
- **Solution**: Check share format, ensure complete copy/paste

#### "Inconsistent share lengths"  
- **Cause**: Shares from different secrets mixed together
- **Solution**: Ensure all shares are from the same split operation

#### "Insufficient shares"
- **Cause**: Not enough shares for threshold
- **Solution**: Obtain additional shares or check threshold requirements

### Getting Help
- Check the security review documentation
- Run the test suite: `python tests/test_all.py`
- Review error messages for specific guidance
- Ensure you're following security best practices

## 🎯 Advanced Usage

### Large Secrets
- Maximum secret length: 64 characters for splitting
- For longer secrets, consider splitting into chunks
- Alternative: Use generated secrets as encryption keys

### Automation Scripts
- Tool designed for interactive use
- For automation, ensure security requirements are maintained
- Consider using the core classes directly for custom implementations

### Multi-language Secrets
- Full Unicode support for international characters
- Emojis and special characters supported
- UTF-8 encoding used throughout

---

**Remember**: This tool handles extremely sensitive information. Always prioritize security over convenience!
