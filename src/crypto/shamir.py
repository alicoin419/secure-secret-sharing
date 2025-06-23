"""
Shamir's Secret Sharing Implementation

Implements Shamir's Secret Sharing scheme for splitting secrets into shares
and reconstructing them. Uses finite field arithmetic over GF(256) with Base62 encoding.
"""

import secrets
from typing import List, Tuple, Optional
from .security import SecurityValidator, SecurityError


class ShamirSecretSharing:
    """
    Implements Shamir's Secret Sharing scheme using GF(256) finite field arithmetic
    with Base62 encoding for share formatting.
    """
    
    # Irreducible polynomial for GF(256): x^8 + x^4 + x^3 + x + 1
    _POLYNOMIAL = 0x11b
    
    # Base62 alphabet for encoding (letters + numbers)
    _BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    
    def __init__(self):
        """Initialize the Shamir Secret Sharing instance."""
        self.security = SecurityValidator()
        self._log_table = [0] * 256
        self._exp_table = [0] * 256
        self._build_tables()
    
    def _build_tables(self) -> None:
        """Build logarithm and exponential tables for GF(256) arithmetic."""
        # Initialize tables
        self._exp_table = [0] * 256
        self._log_table = [0] * 256
        
        # Build exponential table: exp[i] = 3^i in GF(256)
        # 3 is a primitive element for GF(256) with polynomial 0x11b
        x = 1
        for i in range(255):
            self._exp_table[i] = x
            x = self._gf_mult_basic(x, 3)  # Use 3 as primitive element
        self._exp_table[255] = self._exp_table[0]  # For overflow protection
        
        # Build logarithm table: log[exp[i]] = i
        for i in range(255):
            self._log_table[self._exp_table[i]] = i
        # Note: log[0] remains 0 but should never be used
    
    def _gf_mult_basic(self, a: int, b: int) -> int:
        """Basic multiplication in GF(256) using the irreducible polynomial."""
        result = 0
        while b:
            if b & 1:
                result ^= a
            a <<= 1
            if a & 0x100:
                a ^= self._POLYNOMIAL
            b >>= 1
        return result & 0xff
    
    def _gf_mult(self, a: int, b: int) -> int:
        """Fast multiplication in GF(256) using lookup tables."""
        if a == 0 or b == 0:
            return 0
        return self._exp_table[(self._log_table[a] + self._log_table[b]) % 255]
    
    def _gf_div(self, a: int, b: int) -> int:
        """Division in GF(256)."""
        if a == 0:
            return 0
        if b == 0:
            raise ValueError("Division by zero in GF(256)")
        return self._exp_table[(self._log_table[a] - self._log_table[b]) % 255]
    
    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """Evaluate a polynomial at point x using Horner's method."""
        result = 0
        for coeff in reversed(coefficients):
            result = self._gf_mult(result, x) ^ coeff
        return result
    
    def _lagrange_interpolation(self, points: List[Tuple[int, int]], x: int = 0) -> int:
        """
        Perform Lagrange interpolation to find the value at x.
        
        Args:
            points: List of (x, y) coordinate tuples
            x: Point to evaluate at (default 0 for secret recovery)
            
        Returns:
            int: Interpolated value at x
        """
        if not points:
            raise ValueError("No points provided for interpolation")
        
        result = 0
        
        for i, (xi, yi) in enumerate(points):
            # Calculate Lagrange basis polynomial L_i(x)
            li = 1
            
            for j, (xj, _) in enumerate(points):
                if i != j:
                    # L_i(x) *= (x - xj) / (xi - xj)
                    # In GF(256), subtraction is XOR
                    if xi == xj:
                        raise ValueError("Duplicate x-coordinates in interpolation points")
                    
                    numerator = x ^ xj
                    denominator = xi ^ xj
                    li = self._gf_mult(li, self._gf_div(numerator, denominator))
            
            # Add yi * L_i(x) to result
            result = result ^ self._gf_mult(yi, li)
        
        return result
    
    def _encode_base62(self, data: bytes) -> str:
        """
        Encode binary data to Base62 string (0-9, A-Z, a-z).
        
        Args:
            data: Binary data to encode
            
        Returns:
            str: Base62 encoded string
        """
        if not data:
            return ""
        
        # Convert bytes to big integer
        num = int.from_bytes(data, byteorder='big')
        
        if num == 0:
            return self._BASE62_ALPHABET[0]
        
        result = ""
        while num > 0:
            result = self._BASE62_ALPHABET[num % 62] + result
            num //= 62
        
        return result
    
    def _decode_base62(self, encoded: str) -> bytes:
        """
        Decode Base62 string back to binary data.
        
        Args:
            encoded: Base62 encoded string
            
        Returns:
            bytes: Decoded binary data
        """
        if not encoded:
            return b""
        
        num = 0
        for char in encoded:
            if char not in self._BASE62_ALPHABET:
                raise ValueError(f"Invalid Base62 character: {char}")
            num = num * 62 + self._BASE62_ALPHABET.index(char)
        
        # Convert back to bytes (determine byte length from original data size)
        if num == 0:
            return b"\x00"
        
        byte_length = (num.bit_length() + 7) // 8
        return num.to_bytes(byte_length, byteorder='big')
    
    def _format_share_with_original_length(self, share_id: int, share_data: bytes, original_secret_length: int) -> str:
        """
        Format a share using Base62 encoding with original secret length stored.
        This allows proper reconstruction with padding removal.
        
        Args:
            share_id: Share identifier (1-255)
            share_data: Raw share data bytes (may include padding)
            original_secret_length: Length of original secret before padding
            
        Returns:
            str: Formatted share string (minimum 250 characters)
        """
        # Store both the padded data length and original secret length
        padded_length = len(share_data)
        
        # Create header: share_id (1 byte) + original_secret_length (2 bytes) + padded_length (2 bytes)
        header = bytes([share_id]) + original_secret_length.to_bytes(2, 'big') + padded_length.to_bytes(2, 'big')
        base_data = header + share_data
        
        # Encode with Base62
        encoded = self._encode_base62(base_data)
        
        # Ensure minimum share length of 250 characters
        if len(encoded) < 250:
            # Add additional secure random padding to reach 250 characters
            padding_needed = 250 - len(encoded)
            
            # Generate additional random data and encode it
            additional_padding = bytearray()
            for _ in range(padding_needed // 3 + 10):  # Extra bytes to ensure we reach 250+
                additional_padding.append(self.security.secure_random_int(1, 255))
            
            # Encode additional padding and append
            padding_encoded = self._encode_base62(bytes(additional_padding))
            encoded = encoded + padding_encoded
            
            # Trim to exactly 250 characters if we went over
            if len(encoded) > 250:
                encoded = encoded[:250]
        
        return encoded

    def _parse_base62_share(self, share_str: str) -> Tuple[int, List[int]]:
        """
        Parse a Base62 encoded share string with padding support.
        
        Args:
            share_str: Base62 encoded share string
            
        Returns:
            tuple: (share_id, share_values) - only original secret data, padding removed
        """
        try:
            # Decode Base62 string to bytes
            decoded_bytes = self._decode_base62(share_str)
            
            if len(decoded_bytes) < 5:  # Need at least header (5 bytes)
                # Try old format for backward compatibility
                if len(decoded_bytes) >= 2:
                    share_id = decoded_bytes[0]
                    original_length = decoded_bytes[1]
                    
                    if share_id >= 1 and share_id <= 255:
                        share_values = list(decoded_bytes[2:2+original_length])
                        return share_id, share_values
                
                raise ValueError("Share too short")
            
            # Parse new format header: share_id (1) + original_length (2) + padded_length (2)
            share_id = decoded_bytes[0]
            original_length = int.from_bytes(decoded_bytes[1:3], 'big')
            padded_length = int.from_bytes(decoded_bytes[3:5], 'big')
            
            if share_id < 1 or share_id > 255:
                raise ValueError(f"Invalid share ID: {share_id}")
            
            # Extract share data
            share_data = decoded_bytes[5:]
            
            if len(share_data) != padded_length:
                raise ValueError("Share data length mismatch")
            
            # Return only original secret data (remove padding)
            share_values = list(share_data[:original_length])
            
            return share_id, share_values            
        except Exception as e:
            raise ValueError(f"Failed to parse share: {e}")

    def generate_shares(self, secret: str, total_shares: int, threshold: int) -> List[str]:
        """
        Generate shares for a secret using Shamir's Secret Sharing.
        Each share will be at least 250 characters for security.
        
        Args:
            secret: The secret to share
            total_shares: Total number of shares to generate
            threshold: Minimum number of shares needed for reconstruction
            
        Returns:
            List[str]: List of Base62 encoded shares (minimum 250 characters each)
            
        Raises:
            SecurityError: If security validation fails
            ValueError: If parameters are invalid
        """
        # Validate parameters
        valid, error = self.security.validate_share_parameters(total_shares, threshold)
        if not valid:
            raise ValueError(error)
        
        valid, error = self.security.validate_secret_length(secret, max_length=10000)
        if not valid:
            raise ValueError(error)
        
        # Convert secret to bytes
        secret_bytes = secret.encode('utf-8')
        original_length = len(secret_bytes)
          # Calculate minimum bytes needed for ~250 character Base62 output
        # Base62 encoding efficiency: roughly 6 bits per character (log2(62) ≈ 5.95)
        # For 250 characters we need about 250 * 5.95 / 8 ≈ 186 bytes minimum
        # Add buffer to ensure we always reach 250+ characters 
        min_bytes_for_250_chars = 200  # Conservative estimate to ensure 250+ character shares
        
        # Add secure random padding if the secret is too short
        if len(secret_bytes) < min_bytes_for_250_chars:
            padding_needed = min_bytes_for_250_chars - len(secret_bytes)
            
            # Generate cryptographically secure random padding
            padding = bytearray()
            for _ in range(padding_needed):
                # Generate secure random bytes (1-255, avoiding 0 for security)
                padding.append(self.security.secure_random_int(1, 255))
            
            # Combine original secret with padding
            secret_bytes = secret_bytes + bytes(padding)
            
            # Register padding for secure cleanup
            self.security.register_sensitive_data(padding)
        
        shares = []
        
        try:
            # Process each byte of the padded secret
            for byte_index in range(len(secret_bytes)):
                byte_value = secret_bytes[byte_index]
                
                # Generate polynomial coefficients
                coefficients = [byte_value]  # Secret is the constant term
                
                # Generate random coefficients for polynomial of degree (threshold - 1)
                for _ in range(threshold - 1):
                    # Ensure coefficient is not zero
                    coeff = self.security.secure_random_int(1, 255)
                    coefficients.append(coeff)
                
                # Register coefficients for memory clearing
                self.security.register_sensitive_data(coefficients)
                
                # Generate shares for this byte
                for share_index in range(1, total_shares + 1):
                    share_value = self._evaluate_polynomial(coefficients, share_index)
                    
                    # Store share (first iteration creates the share structure)
                    if byte_index == 0:
                        shares.append([share_index, share_value])
                    else:
                        shares[share_index - 1].append(share_value)
            
            # Encode shares as strings with Base62 encoding
            encoded_shares = []
            for share in shares:
                share_id = share[0]
                share_values = share[1:]
                
                # Convert share values to bytes
                share_bytes = bytes(share_values)
                  # Format with Base62 encoding - now includes original length for proper reconstruction
                encoded_share = self._format_share_with_original_length(share_id, share_bytes, original_length)
                encoded_shares.append(encoded_share)
            
            return encoded_shares
            
        finally:
            # Clear sensitive data
            self.security.clear_memory()
    
    def reconstruct_secret(self, shares: List[str]) -> str:
        """
        Reconstruct the secret from shares.
        
        Args:
            shares: List of encoded shares
            
        Returns:
            str: The reconstructed secret            
        Raises:
            ValueError: If shares are invalid or insufficient
        """
        if not shares:
            raise ValueError("No shares provided")
        
        # Parse shares
        parsed_shares = []
        secret_length = None
        
        for share_str in shares:
            try:
                # Try Base62 format first (new format)
                share_id, values = self._parse_base62_share(share_str)
                
                if secret_length is None:
                    secret_length = len(values)
                elif len(values) != secret_length:
                    # Handle padding by truncating to expected length
                    if len(values) > secret_length:
                        values = values[:secret_length]
                    else:
                        raise ValueError("Inconsistent share lengths")
                
                parsed_shares.append((share_id, values))
                
            except ValueError:
                # Fallback to old hex format for backward compatibility
                try:
                    if '-' not in share_str:
                        raise ValueError("Invalid share format")
                    
                    share_id_hex, values_hex = share_str.split('-', 1)
                    share_id = int(share_id_hex, 16)
                    
                    if share_id < 1 or share_id > 255:
                        raise ValueError(f"Invalid share ID: {share_id}")
                    
                    # Parse hex values
                    if len(values_hex) % 2 != 0:
                        raise ValueError("Invalid share values length")
                    
                    values = []
                    for i in range(0, len(values_hex), 2):
                        value = int(values_hex[i:i+2], 16)
                        values.append(value)
                    
                    if secret_length is None:
                        secret_length = len(values)
                    elif len(values) != secret_length:
                        raise ValueError("Inconsistent share lengths")
                    
                    parsed_shares.append((share_id, values))
                    
                except Exception as e:
                    raise ValueError(f"Failed to parse share: {e}")
        
        if not parsed_shares:
            raise ValueError("No valid shares found")
        
        try:
            # Reconstruct each byte of the secret
            secret_bytes = []
            
            for byte_index in range(secret_length):
                # Collect points for this byte position
                points = []
                for share_id, values in parsed_shares:
                    points.append((share_id, values[byte_index]))
                
                # Register points for memory clearing
                self.security.register_sensitive_data(points)
                
                # Interpolate to find the secret byte (evaluate at x=0)
                secret_byte = self._lagrange_interpolation(points, 0)
                secret_bytes.append(secret_byte)
            
            # Convert bytes back to string
            secret = bytes(secret_bytes).decode('utf-8')
            return secret
            
        except UnicodeDecodeError:
            raise ValueError("Reconstructed data is not valid UTF-8")
        finally:
            # Clear sensitive data
            self.security.clear_memory()
    
    def generate_random_secret(self, length: int) -> str:
        """
        Generate a cryptographically secure random secret.
        
        Args:
            length: Length of the secret to generate
            
        Returns:
            str: Random secret string
              Raises:
            SecurityError: If CSPRNG is not available
            ValueError: If length is invalid
        """
        if length < 1 or length > 50000:
            raise ValueError("Secret length must be between 1 and 50000 characters")
        
        # Character set for generated secrets (alphanumeric + some symbols)
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        
        try:
            secret = ''.join(secrets.choice(chars) for _ in range(length))
            return secret
        except Exception as e:
            raise SecurityError("Failed to generate random secret") from e
    
    def validate_shares(self, shares: List[str]) -> Tuple[bool, str]:
        """
        Validate that shares are properly formatted and consistent.
        
        Args:
            shares: List of share strings to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not shares:
            return False, "No shares provided"
        
        if len(shares) < 2:
            return False, "At least 2 shares required"
        
        try:
            # Parse and validate each share
            parsed_shares = []
            secret_length = None
            share_ids = set()
            
            for i, share_str in enumerate(shares):
                if not isinstance(share_str, str):
                    return False, f"Share {i+1} is not a string"
                
                try:
                    # Try Base62 format first
                    share_id, values = self._parse_base62_share(share_str)
                    
                    if share_id in share_ids:
                        return False, f"Duplicate share ID: {share_id}"
                    share_ids.add(share_id)
                    
                    if secret_length is None:
                        secret_length = len(values)
                    elif len(values) != secret_length:
                        return False, f"Share {i+1} has inconsistent length"
                    
                    parsed_shares.append((share_id, values))
                    
                except ValueError:
                    # Try old hex format
                    if '-' not in share_str:
                        return False, f"Share {i+1} has invalid format"
                    
                    parts = share_str.split('-', 1)
                    if len(parts) != 2:
                        return False, f"Share {i+1} has invalid format"
                    
                    share_id_hex, values_hex = parts
                    
                    # Validate share ID
                    try:
                        share_id = int(share_id_hex, 16)
                    except ValueError:
                        return False, f"Share {i+1} has invalid ID format"
                    
                    if share_id < 1 or share_id > 255:
                        return False, f"Share {i+1} has invalid ID: {share_id}"
                    
                    if share_id in share_ids:
                        return False, f"Duplicate share ID: {share_id}"
                    share_ids.add(share_id)
                    
                    # Validate values
                    if len(values_hex) % 2 != 0:
                        return False, f"Share {i+1} has invalid values length"
                    
                    if len(values_hex) == 0:
                        return False, f"Share {i+1} has no values"
                    
                    try:
                        values = []
                        for j in range(0, len(values_hex), 2):
                            value = int(values_hex[j:j+2], 16)
                            values.append(value)
                    except ValueError:
                        return False, f"Share {i+1} has invalid hex values"
                    
                    if secret_length is None:
                        secret_length = len(values)
                    elif len(values) != secret_length:
                        return False, f"Share {i+1} has inconsistent length"
                    
                    parsed_shares.append((share_id, values))
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
