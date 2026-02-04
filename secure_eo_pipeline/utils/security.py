# Import the os module to interact with the operating system (e.g., checking file existence)
import os
# Import hashlib to provide secure hash algorithms like SHA-256 for data integrity checks
import hashlib
# Import Fernet from the cryptography library to implement symmetric encryption
from cryptography.fernet import Fernet
# Import the local config module to access global settings like file paths and keys
from secure_eo_pipeline import config

# =============================================================================
# Security Utilities Module - Line-by-Line Technical Explanation
# =============================================================================
# PURPOSE:
# This module acts as the "Cryptographic Engine" for the entire pipeline.
# It abstracts complex mathematical operations into simple function calls.
#
# DESIGN RATIONALE:
# In Earth Observation, data integrity is paramount. If a single bit is flipped
# during transmission or storage, scientific results could be invalid.
# Encryption ensures that sensitive or proprietary data remains confidential.
# =============================================================================

def generate_key():
    """
    Generates a new 256-bit symmetric encryption key and saves it to a file.
    
    RATIONALE:
    Symmetric encryption uses the same key for both locking and unlocking data.
    Generating a fresh, cryptographically secure random key is the first step in
    securing any system.
    """
    # Use Fernet's built-in generator to create a secure, random key.
    # Fernet uses AES-128 in CBC mode for encryption and HMAC-SHA256 for authentication.
    key = Fernet.generate_key()
    
    # Open the designated key file path in 'wb' (write binary) mode
    # Using 'with' ensures the file is properly closed even if an error occurs
    with open(config.KEY_PATH, "wb") as key_file:
        # Write the raw bytes of the key into the file
        key_file.write(key)
    
    # Tighten file permissions where the OS allows it (best-effort on non-POSIX systems)
    try:
        os.chmod(config.KEY_PATH, 0o600)
    except Exception:
        pass
    
    # Output a notification to the console for the system operator
    # In a real environment, this would be a high-priority security audit log
    print(f"[SECURITY CORE] SUCCESS: A new encryption key was written to: {config.KEY_PATH}")


def load_key():
    """
    Retrieves the existing encryption key from the filesystem.
    
    RETURNS:
        bytes: The raw cryptographic key.
        
    SECURITY LOGIC:
    This function implements a "Secure Default" pattern. If the key doesn't exist,
    it creates one instead of crashing, ensuring the system is always protected.
    """
    # Check if the key file exists at the path defined in our central config
    if not os.path.exists(config.KEY_PATH):
        # If the file is missing, trigger the generation of a new key immediately
        generate_key()
        
    try:
        # Open the key file in 'rb' (read binary) mode
        with open(config.KEY_PATH, "rb") as key_file:
            # Read all bytes from the file and return them to the caller
            return key_file.read()
    except Exception as e:
        # If a hardware or permission error occurs, report it precisely
        print(f"[SECURITY CORE] FATAL ERROR: Could not read key file. Details: {e}")
        # Re-raise the exception to stop execution; continuing without a key is unsafe
        raise


def encrypt_file(file_path):
    """
    Transforms a readable file into an encrypted blob of data.
    
    ARGUMENTS:
        file_path (str): The location of the file to be scrambled.
        
    TECHNICAL FLOW:
    Read Plaintext -> Load Key -> Apply Encryption Algorithm -> Write Ciphertext
    """
    # Step 1: Call our internal load_key() to get the secret bytes
    key = load_key()
    
    # Step 2: Initialize the Fernet encryption object with the secret key
    # This object contains the logic for the Fernet encryption scheme
    f = Fernet(key)
    
    try:
        # Step 3: Open the target file in 'rb' mode to read the original scientific data
        with open(file_path, "rb") as file:
            # Load the entire content into memory (Buffer)
            file_data = file.read()
            
        # Step 4: Execute the encryption transformation
        # This adds a 128-bit IV (Initialization Vector) and a 256-bit HMAC (Signature)
        encrypted_data = f.encrypt(file_data)
        
        # Step 5: Open the SAME file in 'wb' mode to overwrite it
        with open(file_path, "wb") as file:
            # Write the encrypted 'ciphertext' back to disk
            file.write(encrypted_data)
    except FileNotFoundError:
        # Handle cases where the requested file doesn't exist
        print(f"[SECURITY CORE] ERROR: Encryption failed. File {file_path} not found.")
    except Exception as e:
        # Handle unexpected errors (e.g., disk full, permission denied)
        print(f"[SECURITY CORE] ERROR: Unexpected encryption failure for {file_path}. {e}")


def decrypt_file(file_path):
    """
    Restores an encrypted file back to its original readable state.
    
    ARGUMENTS:
        file_path (str): The location of the scrambled file.
        
    SECURITY NOTE:
    Fernet decryption also verifies the HMAC signature. If the file was
    tampered with by even one bit, decryption will fail (Authenticated Encryption).
    """
    # Step 1: Retrieve the required secret key
    key = load_key()
    
    # Step 2: Initialize the cryptographic engine
    f = Fernet(key)
    
    try:
        # Step 3: Read the encrypted 'ciphertext' from the storage medium
        with open(file_path, "rb") as file:
            # Load the scrambled bytes into the memory buffer
            encrypted_data = file.read()
            
        # Step 4: Perform the decryption operation
        # This removes the IV and verifies the HMAC before returning the original data
        decrypted_data = f.decrypt(encrypted_data)
        
        # Step 5: Overwrite the file with the clean 'plaintext' bytes
        with open(file_path, "wb") as file:
            # Data is now usable for scientific processing again
            file.write(decrypted_data)
    except Exception as e:
        # Log decryption failures (often caused by wrong keys or corrupted files)
        print(f"[SECURITY CORE] ERROR: Decryption failed for {file_path}. Reason: {e}")
        # We re-raise to ensure the caller knows the data is still unreadable
        raise


def calculate_hash(file_path):
    """
    Generates a SHA-256 'Digital Fingerprint' of any file.
    
    ARGUMENTS:
        file_path (str): The file to be fingerprinted.
        
    WHY SHA-256?
    SHA-256 is a 'One-Way' function. You can easily get a hash from a file,
    but you can never recreate the file from the hash. It is the gold standard
    for verifying that data has not been modified (Integrity).
    
    RETURNS:
        str: A 64-character hexadecimal string.
    """
    # Initialize the SHA-256 hashing engine from the hashlib library
    sha256_engine = hashlib.sha256()
    
    try:
        # Step 1: Open the file for reading in binary mode
        with open(file_path, "rb") as f:
            # Step 2: Read the file in small 4KB (4096 bytes) chunks
            # RATIONALE: Reading a 10GB satellite image at once would crash the RAM.
            # Chunking allows us to process files of any size efficiently.
            for byte_block in iter(lambda: f.read(4096), b""):
                # Step 3: Feed each chunk into the hashing engine sequentially
                sha256_engine.update(byte_block)
                
        # Step 4: Finalize the calculation and return the result as a hex string
        # hexdigest() provides a human-readable representation of the binary hash
        return sha256_engine.hexdigest()
    except FileNotFoundError:
        # If the file isn't there, we can't hash it
        print(f"[SECURITY CORE] ERROR: Cannot calculate hash. {file_path} not found.")
        return None
