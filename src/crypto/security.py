"""
Security Utilities and Validation

Provides security validation, CSPRNG verification, and memory management utilities.
"""

import os
import sys
import secrets
import gc
from typing import Optional

# Try to import psutil, provide fallback if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class SecurityValidator:
    """Handles security validation and memory management."""
    
    def __init__(self):
        """Initialize the security validator."""
        self._sensitive_data_refs = []
    
    def verify_csprng(self) -> bool:
        """
        Verify that a cryptographically secure random number generator is available.
        
        Returns:
            bool: True if CSPRNG is available and working, False otherwise
        """
        try:
            # Test Python's secrets module
            test_bytes = secrets.token_bytes(32)
            
            # Verify we got the expected length
            if len(test_bytes) != 32:
                return False
            
            # Test that we get different values (basic entropy check)
            test_bytes2 = secrets.token_bytes(32)
            if test_bytes == test_bytes2:
                # This is extremely unlikely with a proper CSPRNG
                return False
            
            # Clear test data            del test_bytes, test_bytes2
            
            return True
            
        except Exception:
            return False
    
    def check_network_isolation(self) -> bool:
        """
        Basic check for network interfaces (air-gap verification).
        
        Returns:
            bool: True if no active network interfaces found, False otherwise
        """
        if not HAS_PSUTIL:
            # Can't check without psutil, assume network might be present
            return False
            
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            
            # Check for active interfaces (excluding loopback)
            for interface_name, addresses in interfaces.items():
                if interface_name.lower() != 'loopback' and addresses:
                    # Check if interface has non-loopback addresses
                    for addr in addresses:
                        if addr.address and not addr.address.startswith('127.'):
                            return False
            
            return True
            
        except Exception:
            # If we can't check, assume network might be present
            return False
    
    def secure_random_bytes(self, length: int) -> bytes:
        """
        Generate cryptographically secure random bytes.
        
        Args:
            length: Number of bytes to generate
            
        Returns:
            bytes: Cryptographically secure random bytes
            
        Raises:
            SecurityError: If CSPRNG is not available
        """
        if not self.verify_csprng():
            raise SecurityError("Cryptographically secure random number generator not available")
        
        return secrets.token_bytes(length)
    
    def secure_random_int(self, min_val: int, max_val: int) -> int:
        """
        Generate a cryptographically secure random integer in range [min_val, max_val].
        
        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)
            
        Returns:
            int: Cryptographically secure random integer
            
        Raises:
            SecurityError: If CSPRNG is not available
        """
        if not self.verify_csprng():
            raise SecurityError("Cryptographically secure random number generator not available")
        
        return secrets.randbelow(max_val - min_val + 1) + min_val
    
    def register_sensitive_data(self, data_ref) -> None:
        """
        Register a reference to sensitive data for later clearing.
        
        Args:
            data_ref: Reference to sensitive data object
        """
        self._sensitive_data_refs.append(data_ref)
    
    def clear_memory(self) -> None:
        """
        Attempt to clear sensitive data from memory.
        
        Note: This is a best-effort approach. Complete memory clearing
        requires system-level controls.
        """
        # Clear registered sensitive data references
        for ref in self._sensitive_data_refs:
            try:
                if hasattr(ref, 'clear'):
                    ref.clear()
                elif isinstance(ref, (list, dict)):
                    ref.clear()
                elif hasattr(ref, '__dict__'):
                    for attr_name in list(ref.__dict__.keys()):
                        if attr_name.startswith('_secret') or 'secret' in attr_name.lower():
                            setattr(ref, attr_name, None)
            except Exception:
                pass  # Ignore errors in clearing
        
        # Clear the references list
        self._sensitive_data_refs.clear()
        
        # Force garbage collection
        gc.collect()
    
    def validate_share_parameters(self, total_shares: int, threshold: int) -> tuple[bool, str]:
        """
        Validate Shamir's Secret Sharing parameters.
        
        Args:
            total_shares: Total number of shares to generate
            threshold: Minimum shares needed for reconstruction
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(total_shares, int) or not isinstance(threshold, int):
            return False, "Share parameters must be integers"
        
        if total_shares < 2:
            return False, "Total shares must be at least 2"
        
        if total_shares > 255:
            return False, "Total shares cannot exceed 255"
        
        if threshold < 2:
            return False, "Threshold must be at least 2"
        
        if threshold > total_shares:
            return False, "Threshold cannot exceed total shares"
        
        return True, ""
    
    def validate_secret_length(self, secret: str, min_length: int = 1, max_length: int = 50000) -> tuple[bool, str]:
        """
        Validate secret length and content.
        
        Args:
            secret: The secret to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(secret, str):
            return False, "Secret must be a string"
        
        if len(secret) < min_length:
            return False, f"Secret must be at least {min_length} characters"
        
        if len(secret) > max_length:
            return False, f"Secret cannot exceed {max_length} characters"
        
        # Check for potentially problematic characters
        if '\x00' in secret:
            return False, "Secret cannot contain null bytes"
        
        return True, ""


class SecurityError(Exception):
    """Raised when a security validation fails."""
    pass
