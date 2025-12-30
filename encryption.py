"""
Database and field-level encryption module.

Provides:
- SQLCipher encrypted database connections
- Field-level AES-256 encryption for sensitive data
- Automatic encryption/decryption on operations
"""

import os
import logging
import hashlib
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class FieldEncryption:
    """Handles field-level encryption/decryption of sensitive data."""
    
    def __init__(self, key=None):
        """Initialize with encryption key from environment or parameter."""
        if key is None:
            key = os.getenv('FIELD_ENCRYPTION_KEY')
        
        if not key:
            raise ValueError(
                'FIELD_ENCRYPTION_KEY not set in environment. '
                'Generate with: python -c "from cryptography.fernet import Fernet; '
                'print(Fernet.generate_key().decode())"'
            )
        
        try:
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            raise ValueError(f'Invalid FIELD_ENCRYPTION_KEY format: {e}')
    
    def encrypt(self, plaintext):
        """Encrypt plaintext. Returns None if input is None."""
        if plaintext is None or plaintext == '':
            return None
        
        try:
            encrypted = self.cipher.encrypt(str(plaintext).encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f'Encryption failed: {e}')
            raise
    
    def decrypt(self, ciphertext):
        """Decrypt ciphertext. Returns None if input is None."""
        if ciphertext is None or ciphertext == '':
            return None
        
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except InvalidToken:
            logger.error('Decryption failed: Invalid token (wrong key?)')
            raise ValueError('Failed to decrypt field - wrong encryption key?')
        except Exception as e:
            logger.error(f'Decryption failed: {e}')
            raise
    
    def is_encrypted(self, value):
        """Check if a value appears to be encrypted (for validation)."""
        if value is None:
            return False
        try:
            # Encrypted values start with 'gAAAAAB' (Fernet format)
            return isinstance(value, str) and value.startswith('gAAAAAB')
        except:
            return False
    
    @staticmethod
    def hash_for_search(plaintext):
        """Create a searchable hash of plaintext for name lookups.
        
        Uses SHA-256 for consistent hashing. This allows searching encrypted
        names without storing plaintext or using expensive decryption.
        """
        if plaintext is None or plaintext == '':
            return None
        
        try:
            # Normalize: lowercase and strip whitespace for consistent matching
            normalized = str(plaintext).strip().lower()
            # Create SHA-256 hash
            hash_digest = hashlib.sha256(normalized.encode()).hexdigest()
            return hash_digest
        except Exception as e:
            logger.error(f'Name hashing failed: {e}')
            raise
    
    @staticmethod
    def generate_name_tokens(name):
        """Generate searchable tokens for partial name matching.
        
        For "John Smith", generates tokens for:
        - Full name: "john smith"
        - First name parts: "john", "joh", "jo"
        - Last name parts: "smith", "smit", "smi", "sm"
        
        Returns a set of tokens for tokenized search.
        """
        if not name:
            return set()
        
        try:
            # Normalize: lowercase and strip whitespace
            normalized = str(name).strip().lower()
            tokens = set()
            
            # Add full name
            tokens.add(normalized)
            
            # Split into words and generate prefix tokens for each word
            words = normalized.split()
            for word in words:
                tokens.add(word)  # Full word
                # Add prefixes (2+ characters)
                for i in range(2, len(word) + 1):
                    tokens.add(word[:i])
            
            return tokens
        except Exception as e:
            logger.error(f'Token generation failed: {e}')
            raise
    
    @staticmethod
    def hash_name_tokens(name):
        """Generate hashes for all name tokens.
        
        Returns a list of SHA-256 hashes for all tokens of the name.
        This enables partial name search while maintaining encryption.
        """
        if not name:
            return []
        
        try:
            tokens = FieldEncryption.generate_name_tokens(name)
            hashes = []
            for token in tokens:
                hash_digest = hashlib.sha256(token.encode()).hexdigest()
                hashes.append(hash_digest)
            return hashes
        except Exception as e:
            logger.error(f'Token hashing failed: {e}')
            raise


class DatabaseEncryption:
    """SQLCipher database encryption wrapper."""
    
    @staticmethod
    def get_encryption_key():
        """Get and validate DB encryption key from environment."""
        key = os.getenv('DB_ENCRYPTION_KEY')
        
        if not key:
            raise ValueError(
                'DB_ENCRYPTION_KEY not set in environment. '
                'Generate with: openssl rand -hex 32'
            )
        
        # Validate hex key length (should be 32 chars = 16 bytes)
        if len(key) < 32:
            raise ValueError(f'DB_ENCRYPTION_KEY too short. Need 32+ chars (got {len(key)})')
        
        return key
    
    @staticmethod
    def validate_keys():
        """Validate that encryption keys are properly configured."""
        try:
            db_key = DatabaseEncryption.get_encryption_key()
            field_key = os.getenv('FIELD_ENCRYPTION_KEY')
            
            if not field_key:
                raise ValueError('FIELD_ENCRYPTION_KEY not set')
            
            # Test field encryption
            fe = FieldEncryption(field_key)
            test_data = 'test'
            encrypted = fe.encrypt(test_data)
            decrypted = fe.decrypt(encrypted)
            
            if decrypted != test_data:
                raise ValueError('Field encryption test failed')
            
            logger.info('Encryption keys validated successfully')
            return True
        except Exception as e:
            logger.error(f'Encryption key validation failed: {e}')
            raise


def get_encrypted_db_connection():
    """
    Create an SQLCipher-encrypted database connection.
    
    Requires: DB_ENCRYPTION_KEY environment variable
    
    Returns: sqlite3 connection with encryption enabled
    """
    try:
        # Import here to avoid hard dependency
        from sqlcipher3 import dbapi2 as sqlite3
    except ImportError:
        raise ImportError(
            'sqlcipher3-binary not installed. '
            'Install with: pip install sqlcipher3-binary'
        )
    
    db_path = os.path.join('data', 'checkin.db')
    encryption_key = DatabaseEncryption.get_encryption_key()
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Set encryption parameters
    conn.execute(f"PRAGMA key = '{encryption_key}'")
    conn.execute("PRAGMA cipher = 'aes-256-cbc'")
    conn.execute("PRAGMA kdf_iter = 64000")  # PBKDF2 iterations for key derivation
    
    # Test connection
    try:
        conn.execute("SELECT 1")
        logger.info('SQLCipher encrypted database connection established')
    except Exception as e:
        logger.error(f'Failed to initialize encrypted database: {e}')
        raise
    
    return conn


# Convenience function for app.py
def init_encryption():
    """Initialize and validate encryption at app startup."""
    DatabaseEncryption.validate_keys()
    logger.info('Encryption module initialized')
