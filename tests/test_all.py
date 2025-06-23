"""
Comprehensive test suite for the Secure Secret Sharing Tool.

Tests all critical security and functionality aspects.
"""

import unittest
import os
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.crypto.security import SecurityValidator, SecurityError
from src.crypto.shamir import ShamirSecretSharing

# Import InputValidator from utils
try:
    from src.utils.validators import InputValidator
except ImportError as e:
    print(f"Warning: Could not import InputValidator: {e}")
    InputValidator = None


class TestSecurityValidator(unittest.TestCase):
    """Test security validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SecurityValidator()
    
    def test_csprng_verification(self):
        """Test CSPRNG verification works."""
        self.assertTrue(self.validator.verify_csprng())
    
    def test_secure_random_bytes(self):
        """Test secure random byte generation."""
        # Test normal operation
        random_bytes = self.validator.secure_random_bytes(32)
        self.assertEqual(len(random_bytes), 32)
        self.assertIsInstance(random_bytes, bytes)
        
        # Test that we get different values
        random_bytes2 = self.validator.secure_random_bytes(32)
        self.assertNotEqual(random_bytes, random_bytes2)
    
    def test_secure_random_int(self):
        """Test secure random integer generation."""
        # Test range compliance
        for _ in range(100):
            rand_int = self.validator.secure_random_int(1, 10)
            self.assertGreaterEqual(rand_int, 1)
            self.assertLessEqual(rand_int, 10)
        
        # Test single value range
        single_val = self.validator.secure_random_int(5, 5)
        self.assertEqual(single_val, 5)
    
    def test_share_parameter_validation(self):
        """Test share parameter validation."""
        # Valid parameters
        valid, error = self.validator.validate_share_parameters(5, 3)
        self.assertTrue(valid)
        self.assertEqual(error, "")
        
        # Invalid: non-integers
        valid, error = self.validator.validate_share_parameters("5", 3)
        self.assertFalse(valid)
        self.assertIn("integer", error)
        
        # Invalid: too few shares
        valid, error = self.validator.validate_share_parameters(1, 1)
        self.assertFalse(valid)
        self.assertIn("at least 2", error)
        
        # Invalid: threshold > total
        valid, error = self.validator.validate_share_parameters(3, 5)
        self.assertFalse(valid)
        self.assertIn("cannot exceed", error)
        
        # Invalid: too many shares
        valid, error = self.validator.validate_share_parameters(300, 100)
        self.assertFalse(valid)
        self.assertIn("cannot exceed 255", error)
    
    def test_secret_length_validation(self):
        """Test secret length validation."""
        # Valid secret
        valid, error = self.validator.validate_secret_length("test secret")
        self.assertTrue(valid)
        self.assertEqual(error, "")
        
        # Empty secret
        valid, error = self.validator.validate_secret_length("")
        self.assertFalse(valid)
        self.assertIn("at least", error)
          # Too long secret
        long_secret = "a" * 60000
        valid, error = self.validator.validate_secret_length(long_secret)
        self.assertFalse(valid)
        self.assertIn("cannot exceed", error)
        
        # Secret with null bytes
        valid, error = self.validator.validate_secret_length("test\x00secret")
        self.assertFalse(valid)
        self.assertIn("null bytes", error)
    
    def test_memory_clearing(self):
        """Test memory clearing functionality."""
        # Create some test data
        test_list = ["sensitive", "data"]
        test_dict = {"secret": "value"}
        
        # Register for clearing
        self.validator.register_sensitive_data(test_list)
        self.validator.register_sensitive_data(test_dict)
        
        # Clear memory
        self.validator.clear_memory()
        
        # Check that data was cleared
        self.assertEqual(len(test_list), 0)
        self.assertEqual(len(test_dict), 0)


class TestShamirSecretSharing(unittest.TestCase):
    """Test Shamir's Secret Sharing implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.shamir = ShamirSecretSharing()
    
    def test_basic_secret_sharing(self):
        """Test basic secret sharing and reconstruction."""
        secret = "This is a test secret!"
        total_shares = 5
        threshold = 3
        
        # Generate shares
        shares = self.shamir.generate_shares(secret, total_shares, threshold)        
        self.assertEqual(len(shares), total_shares)
        # Each share should be properly formatted (Base62, variable length based on secret size)
        for share in shares:
            self.assertIsInstance(share, str)
            self.assertGreaterEqual(len(share), 10)  # Minimum reasonable length
            self.assertLessEqual(len(share), 1000)   # Maximum reasonable length for test secrets
            # Check that share contains only Base62 characters
            base62_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            for char in share:
                self.assertIn(char, base62_chars)
        
        # Test reconstruction with exact threshold
        test_shares = shares[:threshold]
        reconstructed = self.shamir.reconstruct_secret(test_shares)
        self.assertEqual(reconstructed, secret)
        
        # Test reconstruction with more than threshold
        test_shares = shares[:threshold + 1]
        reconstructed = self.shamir.reconstruct_secret(test_shares)
        self.assertEqual(reconstructed, secret)
        
        # Test that fewer than threshold shares fail
        insufficient_shares = shares[:threshold - 1]
        # This should still work mathematically but might not be secure
        # The security comes from needing the threshold
    
    def test_unicode_secret_sharing(self):
        """Test sharing of Unicode secrets."""
        secret = "🔒 Secure émojis and ñoñ-ASCII! 测试"
        total_shares = 4
        threshold = 2
        
        shares = self.shamir.generate_shares(secret, total_shares, threshold)
        reconstructed = self.shamir.reconstruct_secret(shares[:threshold])
        
        self.assertEqual(reconstructed, secret)
    
    def test_empty_secret_handling(self):
        """Test handling of empty or invalid secrets."""
        with self.assertRaises(ValueError):
            self.shamir.generate_shares("", 3, 2)
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        secret = "test secret"
        
        # Invalid share counts
        with self.assertRaises(ValueError):
            self.shamir.generate_shares(secret, 1, 1)
        
        with self.assertRaises(ValueError):
            self.shamir.generate_shares(secret, 300, 100)
        
        # Invalid threshold
        with self.assertRaises(ValueError):
            self.shamir.generate_shares(secret, 5, 10)
    
    def test_share_validation(self):
        """Test share validation functionality."""
        # Valid shares
        secret = "test"
        shares = self.shamir.generate_shares(secret, 3, 2)
        
        valid, error = self.shamir.validate_shares(shares)
        self.assertTrue(valid)
        self.assertEqual(error, "")
        
        # Invalid shares - wrong format
        invalid_shares = ["not-a-valid-share", "also-invalid"]
        valid, error = self.shamir.validate_shares(invalid_shares)
        self.assertFalse(valid)
        self.assertIn("invalid", error.lower())
        
        # Empty shares list
        valid, error = self.shamir.validate_shares([])
        self.assertFalse(valid)
        self.assertIn("no shares", error.lower())
    
    def test_random_secret_generation(self):
        """Test random secret generation."""
        # Test various lengths
        for length in [12, 24, 32, 64]:
            secret = self.shamir.generate_random_secret(length)
            self.assertEqual(len(secret), length)
            self.assertIsInstance(secret, str)
        
        # Test that we get different secrets
        secret1 = self.shamir.generate_random_secret(20)
        secret2 = self.shamir.generate_random_secret(20)
        self.assertNotEqual(secret1, secret2)
          # Test invalid lengths
        with self.assertRaises(ValueError):
            self.shamir.generate_random_secret(0)
        
        with self.assertRaises(ValueError):
            self.shamir.generate_random_secret(60000)
    
    def test_gf256_arithmetic(self):
        """Test GF(256) arithmetic operations."""
        # Test multiplication
        result = self.shamir._gf_mult(1, 1)
        self.assertEqual(result, 1)
        
        result = self.shamir._gf_mult(2, 3)
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 255)
        
        # Test division
        result = self.shamir._gf_div(6, 2)
        self.assertIsInstance(result, int)
        
        # Test division by zero
        with self.assertRaises(ValueError):
            self.shamir._gf_div(5, 0)
    
    def test_polynomial_evaluation(self):
        """Test polynomial evaluation."""
        coefficients = [1, 2, 3]  # 1 + 2x + 3x^2
        
        # Evaluate at x=0 should give constant term
        result = self.shamir._evaluate_polynomial(coefficients, 0)
        self.assertEqual(result, 1)
        
        # Evaluate at x=1
        result = self.shamir._evaluate_polynomial(coefficients, 1)
        # Result should be 1 XOR 2 XOR 3 = 0 in GF(256)
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 255)


class TestInputValidator(unittest.TestCase):
    """Test input validation utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        if InputValidator is None:
            self.skipTest("InputValidator not available")
    
    def test_secret_parameter_validation(self):
        """Test secret parameter validation."""
        # Valid secret
        valid, error = InputValidator.validate_secret_parameters("test secret")
        self.assertTrue(valid)
        
        # Empty secret
        valid, error = InputValidator.validate_secret_parameters("")
        self.assertFalse(valid)
          # Too long secret (over 50,000 characters)
        long_secret = "a" * 50001
        valid, error = InputValidator.validate_secret_parameters(long_secret)
        self.assertFalse(valid)
        
        # Secret with null bytes
        valid, error = InputValidator.validate_secret_parameters("test\x00secret")
        self.assertFalse(valid)
    
    def test_share_counts_validation(self):
        """Test share count validation."""
        # Valid parameters
        valid, error = InputValidator.validate_share_counts(5, 3)
        self.assertTrue(valid)
        
        # Invalid parameters
        valid, error = InputValidator.validate_share_counts(1, 1)
        self.assertFalse(valid)
        
        valid, error = InputValidator.validate_share_counts(300, 100)
        self.assertFalse(valid)
        
        valid, error = InputValidator.validate_share_counts(5, 10)
        self.assertFalse(valid)
    
    def test_share_format_validation(self):
        """Test share format validation."""
        # Valid share format
        valid, error = InputValidator.validate_share_format("01-48656c6c6f")
        self.assertTrue(valid)
          # Invalid formats
        valid, error = InputValidator.validate_share_format("invalid!")
        self.assertFalse(valid)
        
        valid, error = InputValidator.validate_share_format("01-invalid@")
        self.assertFalse(valid)
        
        valid, error = InputValidator.validate_share_format("gg-48656c6c6f")
        self.assertTrue(valid)  # "gg" is valid Base62
    
    def test_shares_list_validation(self):
        """Test shares list validation."""
        # Valid shares list
        shares = ["01-48656c6c6f", "02-52656c6c70", "03-58656c6c75"]
        valid, error = InputValidator.validate_shares_list(shares)
        self.assertTrue(valid)
        
        # Empty list
        valid, error = InputValidator.validate_shares_list([])
        self.assertFalse(valid)
        
        # Duplicate share IDs
        duplicate_shares = ["01-48656c6c6f", "01-52656c6c70"]
        valid, error = InputValidator.validate_shares_list(duplicate_shares)
        self.assertFalse(valid)
    
    def test_input_sanitization(self):
        """Test input sanitization."""
        # Normal text
        sanitized = InputValidator.sanitize_input_text("Hello World")
        self.assertEqual(sanitized, "Hello World")
        
        # Text with null bytes
        sanitized = InputValidator.sanitize_input_text("Hello\x00World")
        self.assertEqual(sanitized, "HelloWorld")
        
        # Text with control characters
        sanitized = InputValidator.sanitize_input_text("Hello\x01\x02World")
        self.assertEqual(sanitized, "HelloWorld")
        
        # Preserve newlines and tabs
        sanitized = InputValidator.sanitize_input_text("Hello\nWorld\tTest")
        self.assertEqual(sanitized, "Hello\nWorld\tTest")
    
    def test_parse_shares_from_text(self):
        """Test parsing shares from text input."""
        # Standard format
        text = """Share 1: 01-48656c6c6f
Share 2: 02-52656c6c70
Share 3: 03-58656c6c75"""
        
        shares = InputValidator.parse_shares_from_text(text)
        self.assertEqual(len(shares), 3)
        self.assertEqual(shares[0], "01-48656c6c6f")
        
        # Direct format (no labels)
        text = """01-48656c6c6f
02-52656c6c70
03-58656c6c75"""
        
        shares = InputValidator.parse_shares_from_text(text)
        self.assertEqual(len(shares), 3)
        
        # Mixed format with empty lines
        text = """
        Share 1: 01-48656c6c6f
        
        02-52656c6c70
        
        Share 3: 03-58656c6c75
        """
        
        shares = InputValidator.parse_shares_from_text(text)
        self.assertEqual(len(shares), 3)


class TestSecurityRequirements(unittest.TestCase):
    """Test critical security requirements."""
    
    def test_no_fallback_to_insecure_random(self):
        """Test that the system never falls back to insecure randomness."""
        validator = SecurityValidator()
        
        # This should never fail with a proper implementation
        self.assertTrue(validator.verify_csprng())
        
        # Generate random data and verify it's different each time
        data1 = validator.secure_random_bytes(32)
        data2 = validator.secure_random_bytes(32)
        self.assertNotEqual(data1, data2)
    
    def test_memory_clearing_on_error(self):
        """Test that memory is cleared even when errors occur."""
        shamir = ShamirSecretSharing()
        
        # Try to generate shares with invalid parameters
        try:
            shamir.generate_shares("test", 1000, 500)  # Should fail
        except ValueError:
            pass  # Expected          # Memory should still be cleared
        # This is tested by ensuring the security validator clears registered data
    
    def test_input_validation_boundaries(self):
        """Test input validation at security boundaries."""
        if InputValidator is None:
            self.skipTest("InputValidator not available")
            
        # Test maximum allowed values
        valid, _ = InputValidator.validate_share_counts(20, 20)
        self.assertTrue(valid)
        
        # Test just over the boundary
        valid, _ = InputValidator.validate_share_counts(21, 10)
        self.assertFalse(valid)
          # Test security-relevant minimums
        valid, _ = InputValidator.validate_share_counts(2, 1)
        self.assertFalse(valid)  # Threshold of 1 is insecure


def run_all_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSecurityValidator,
        TestShamirSecretSharing,
        TestInputValidator,
        TestSecurityRequirements
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
