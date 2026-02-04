import os
# Import hashlib for SHA-256 Hashing
import hashlib
# Import Fernet from cryptography library for AES Encryption
from cryptography.fernet import Fernet
# Import config to get access to paths (like KEY_PATH)
from secure_eo_pipeline import config

# =============================================================================
# Security Utilities Module
# =============================================================================
# PURPOSE:
# This module encapsulates the low-level cryptographic operations.
# It ensures that other components don't need to know *how* AES works, 
# only *how to use it*. This is "Abstraction".
#
# STANDARDS:
# - Encryption: AES-128/256 (via Fernet implementation)
# - Hashing: SHA-256 (NIST standard for integrity)
# =============================================================================

def generate_key():
    """
    Generates a new symmetric encryption key.
    
    RATIONALE:
    Encryption requires a secret. This function creates that secret.
    """
    # Fernet.generate_key() produces a URL-safe base64-encoded 32-byte key.
    # This is a random string of bytes suitable for AES.
    key = Fernet.generate_key()
    
    # Open the file defined in config.KEY_PATH in 'write bytes' (wb) mode
    # We write it to disk so we can use it again next time.
    with open(config.KEY_PATH, "wb") as key_file:
        key_file.write(key)
    
    # We print to console so the operator knows a critical security event happened.
    print(f"[SECURITY CORE] New encryption key generated: {config.KEY_PATH}")


def load_key():
    """
    Loads the symmetric encryption key from storage.
    
    RETURNS:
        bytes: The raw key bytes required for encryption/decryption.
        
    LOGIC:
    Checks if the key exists. If not, it self-initializes by creating one.
    This prevents the system from crashing on first run ("Secure Default").
    """
    # Check: Does the key file exist on disk?
    if not os.path.exists(config.KEY_PATH):
        # If not, generate one immediately.
        generate_key()
        
    # Read the file in 'read bytes' (rb) mode and return the content
    return open(config.KEY_PATH, "rb").read()


def encrypt_file(file_path):
    """
    Encrypts a file IN-PLACE using AES (Fernet).
    
    ARGUMENTS:
        file_path (str): Absolute path to the cleartext file.
        
    GOAL: Confidentiality.
    After this function runs, the file content is indistinguishable from random noise.
    """
    # 1. Fetch the secret (The Key).
    key = load_key()
    # 2. Initialize the Fernet engine with the key
    f = Fernet(key)
    
    # 3. Read the Sensitive Data into memory.
    # Note: For massive EO files (GBs), we would use stream processing (chunking).
    # For this simulation, reading all at once is fine.
    with open(file_path, "rb") as file:
        file_data = file.read()
        
    # 4. Perform the Mathematical Operation (Encryption).
    # This transforms the readable bytes into encrypted bytes.
    encrypted_data = f.encrypt(file_data)
    
    # 5. Overwrite the original file with the scrambled version.
    with open(file_path, "wb") as file:
        file.write(encrypted_data)
        
    # No console output here to avoid spamming logs; handled by the caller.


def decrypt_file(file_path):
    """
    Decrypts a file IN-PLACE.
    
    ARGUMENTS:
        file_path (str): Absolute path to the encrypted file.
        
    GOAL: Access.
    Reverses the encryption process to make data usable again for authorized users.
    """
    # 1. Fetch the key
    key = load_key()
    # 2. Init engine
    f = Fernet(key)
    
    # 3. Read the encrypted garbage from disk
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
        
    # 4. Decrypt
    # The decrypt() method will raise an InvalidToken exception if the key is wrong
    # or if the data has been tampered with (Authenticated Encryption).
    decrypted_data = f.decrypt(encrypted_data)
    
    # 5. Write the original clean data back to disk
    with open(file_path, "wb") as file:
        file.write(decrypted_data)


def calculate_hash(file_path):
    """
    Calculates the SHA-256 digital fingerprint (hash) of a file.
    
    GOAL: Integrity.
    A "Hash" is a one-way mathematical summary of a file.
    - If you change ONE byte in the file, the Hash changes completely.
    - By storing the hash separately, we can always prove if the file was altered.
    
    RETURNS:
        str: The hexadecimal string of the hash (e.g., "a3f5...").
    """
    # Create a SHA-256 Hasher object
    sha256_hash = hashlib.sha256()
    
    # We read in 4KB chunks.
    # PRO TIP: This is memory-efficient. Even if the file is 100GB,
    # we only ever hold 4KB in memory at a time.
    with open(file_path, "rb") as f:
        # Loop through the file until EOF
        for byte_block in iter(lambda: f.read(4096), b""):
            # Feed the chunk to the hasher
            sha256_hash.update(byte_block)
            
    # Return the digest as a hex string
    return sha256_hash.hexdigest()
