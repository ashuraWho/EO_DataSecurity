# Import OS for paths
import os
# Import JSON for metadata
import json
# Import shutil for copying
import shutil
# Import project config
from secure_eo_pipeline import config
# Import security utils (Encryption)
from secure_eo_pipeline.utils import security
# Import logger
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Secure Storage & Archiving Component
# =============================================================================
# ROLE IN ARCHITECTURE:
# The "Bank Vault".
# This is where data lives for the long term (10-50 years in ESA missions).
#
# KEY REQUIREMENT: Encryption at Rest.
# We must ensure that files on disk are physically unreadable without the key.
# =============================================================================

class ArchiveManager:
    """
    Manages the encrypted archive of EO products.
    """

    def archive_product(self, product_id):
        """
        Encrypts and stores a product.
        """
        # Determine Source Path (from Processing Staging)
        source_file = os.path.join(config.PROCESSING_DIR, f"{product_id}.npy")
        source_meta = os.path.join(config.PROCESSING_DIR, f"{product_id}.json")
        
        # Ensure Vault exists
        if not os.path.exists(config.ARCHIVE_DIR):
            os.makedirs(config.ARCHIVE_DIR)
            
        # Destination paths. Note the extension change to .enc (Encrypted)
        dest_file = os.path.join(config.ARCHIVE_DIR, f"{product_id}.enc")
        dest_meta = os.path.join(config.ARCHIVE_DIR, f"{product_id}.json")
        
        audit_log.info(f"[ARCHIVE] Archiving {product_id}...")
        
        # ---------------------------------------------------------------------
        # ENCRYPTION PHASE
        # ---------------------------------------------------------------------
        
        # Step 1: Copy the processing file to the archive folder.
        # We process the copy, leaving the original in staging (for now).
        shutil.copy(source_file, dest_file)
        
        # Step 2: IN-PLACE ENCRYPTION.
        # We call our security utility to scramble the bits on disk.
        # After this line runs, 'dest_file' is garbage to anyone without the key.
        security.encrypt_file(dest_file)
        
        # ---------------------------------------------------------------------
        # METADATA UPDATE
        # ---------------------------------------------------------------------
        # We generally DO NOT encrypt metadata. Why?
        # We need to be able to search the catalog ("Find images from 2024")
        # without decrypting petabytes of data first.
        
        # Load metadata
        with open(source_meta, "r") as f:
            meta = json.load(f)
            
        # Update status
        meta["status"] = "ARCHIVED"
        meta["archived_path"] = dest_file
        
        # Save metadata to archive folder
        with open(dest_meta, "w") as f:
            json.dump(meta, f, indent=4)
            
        audit_log.info(f"[ARCHIVE] SUCCESS: Product {product_id} encrypted and stored.")
        return dest_file

    def retrieve_product(self, product_id, output_path):
        """
        Retrieves a product for a user.
        
        LOGIC:
        The Archive is "Write-Encrypted".
        To read it, we must "Read-Decrypt".
        We never decrypt the file inside the archive (that would break security).
        Instead, we decrypt a COPY delivered to the user.
        """
        # Identify where the encrypted file is
        archive_file = os.path.join(config.ARCHIVE_DIR, f"{product_id}.enc")
        
        # Check if it exists
        if not os.path.exists(archive_file):
            audit_log.error(f"[ARCHIVE] ERROR: File not found {archive_file}")
            return False
            
        audit_log.info(f"[ARCHIVE] Retrieving and decrypting {product_id}...")
        
        # 1. Copy Encrypted file to User's location
        # This preserves the encrypted master copy.
        shutil.copy(archive_file, output_path)
        
        # 2. Decrypt the User's copy
        # This makes the file readable again.
        security.decrypt_file(output_path)
        
        return True
