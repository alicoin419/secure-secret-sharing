"""
Input validation utilities for secure secret sharing.

Provides comprehensive validation for user inputs and share data.
"""

import re
from typing import List, Tuple, Optional


class InputValidator:
    """Validates user inputs and share data for security and correctness."""
    
    @staticmethod
    def validate_secret_parameters(secret: str) -> Tuple[bool, str]:
        """
        Validate secret parameters.
        
        Args:
            secret: The secret to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(secret, str):
            return False, "Secret must be a string"
        
        if not secret:
            return False, "Secret cannot be empty"
        
        # Check for null bytes or control characters
        if '\x00' in secret:
            return False, "Secret cannot contain null bytes"
        
        if len(secret) > 50000:
            return False, "Secret too long (max 50,000 characters)"
        
        return True, ""
    
    @staticmethod
    def validate_share_counts(total_shares: int, threshold: int) -> Tuple[bool, str]:
        """
        Validate share count parameters.
        
        Args:
            total_shares: Total number of shares
            threshold: Threshold for reconstruction
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(total_shares, int) or not isinstance(threshold, int):
            return False, "Share counts must be integers"
        
        if total_shares < 2:
            return False, "Total shares must be at least 2"
        
        if total_shares > 20:
            return False, "Total shares cannot exceed 20"
        
        if threshold < 2:
            return False, "Threshold must be at least 2"
        
        if threshold > total_shares:
            return False, "Threshold cannot exceed total shares"
        
        return True, ""
    
    @staticmethod
    def validate_share_format(share: str) -> Tuple[bool, str]:
        """
        Validate share format.
        
        Args:
            share: Share string to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(share, str):
            return False, "Share must be a string"
        
        if not share:
            return False, "Share cannot be empty"
        
        # Check for Base62 format (alphanumeric with optional dash)
        # Format: XX-XXXXXXX or just XXXXXXX
        if '-' in share:
            parts = share.split('-')
            if len(parts) != 2:
                return False, "Share format invalid (too many dashes)"
            index_part, data_part = parts
            if not re.match(r'^[0-9A-Za-z]+$', index_part) or not re.match(r'^[0-9A-Za-z]+$', data_part):
                return False, "Share must contain only alphanumeric characters"
        else:
            if not re.match(r'^[0-9A-Za-z]+$', share):
                return False, "Share must contain only alphanumeric characters"
        
        if len(share) < 10:
            return False, "Share too short"
        
        return True, ""
    
    @staticmethod
    def validate_shares_list(shares: List[str]) -> Tuple[bool, str]:
        """
        Validate a list of shares.
        
        Args:
            shares: List of share strings
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(shares, list):
            return False, "Shares must be a list"
        
        if len(shares) < 2:
            return False, "At least 2 shares required"
        
        # Track share IDs to detect duplicates
        share_ids = set()
        
        for i, share in enumerate(shares):
            valid, error = InputValidator.validate_share_format(share)
            if not valid:
                return False, f"Share {i+1}: {error}"
            
            # Extract share ID if using format "XX-XXXXXX"
            if '-' in share:
                share_id = share.split('-')[0]
                if share_id in share_ids:
                    return False, f"Duplicate share ID: {share_id}"
                share_ids.add(share_id)
        
        return True, ""
    
    @staticmethod
    def parse_shares_from_text(text: str) -> List[str]:
        """
        Parse shares from text input.
        
        Args:
            text: Text containing shares
            
        Returns:
            list: List of extracted shares
        """
        if not isinstance(text, str):
            return []
        
        shares = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle "Share X: XXXXXXX" format
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    share = parts[1].strip()
                    if share:
                        shares.append(share)
            else:
                # Direct share format
                if re.match(r'^[0-9A-Za-z-]+$', line):
                    shares.append(line)
        
        return shares
    
    @staticmethod
    def sanitize_input_text(text: str) -> str:
        """
        Sanitize input text for security.
        
        Args:
            text: Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        if not isinstance(text, str):
            return ""
        
        # Remove any potential control characters but preserve normal whitespace
        sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        return sanitized
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength (if used).
        
        Args:
            password: Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(password, str):
            return False, "Password must be a string"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password too long (max 128 characters)"
        
        return True, ""
    
    @staticmethod
    def validate_file_path(path: str) -> Tuple[bool, str]:
        """
        Validate file path for security.
        
        Args:
            path: File path to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(path, str):
            return False, "Path must be a string"
        
        if not path:
            return False, "Path cannot be empty"
        
        # Check for potentially dangerous path components
        dangerous_patterns = ['..', '~', '$', '|', '&', ';', '`']
        for pattern in dangerous_patterns:
            if pattern in path:
                return False, f"Path contains dangerous pattern: {pattern}"
        
        return True, ""
