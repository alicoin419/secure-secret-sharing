# Contributing to CryptoVault

Thank you for your interest in contributing to CryptoVault! This project prioritizes security, accuracy, and privacy.

## Development Guidelines

### Security First
- All contributions must maintain the air-gapped design principle
- No network dependencies should be introduced
- All cryptographic functions must use secure random generators
- Code changes affecting cryptography require comprehensive testing

### Code Quality
- Follow PEP 8 style guidelines
- Include comprehensive tests for new features
- Maintain 100% accuracy in secret reconstruction
- Document security implications of changes

### Testing Requirements
- All tests must pass: `python run_tests.py`
- New features require corresponding test cases
- Accuracy tests must maintain 100% success rate

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Verify all tests pass
5. Submit pull request with detailed description

## Security Reporting

For security vulnerabilities, please:
1. Do NOT create public issues
2. Contact maintainers directly
3. Provide detailed reproduction steps
4. Allow time for responsible disclosure

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
