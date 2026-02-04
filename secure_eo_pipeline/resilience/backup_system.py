# Import the os module for filesystem operations (joining paths, checking existence)
import os
# Import shutil for high-level file operations (copying files for backups/restores)
import shutil
# Import time to simulate processing delays (makes the demo feel more realistic)
import time
# Import the central config module to locate ARCHIVE and BACKUP directories
from secure_eo_pipeline import config
# Import the security utility to perform integrity (hashing) checks
from secure_eo_pipeline.utils import security
# Import the shared audit logger to record recovery operations
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Resilience & Backup System - Line-by-Line Technical Explanation
# =============================================================================
# ROLE IN ARCHITECTURE:
# The "Immune System".
# Security is often thought of as "Keeping people out", but "Resilience" is
# about "Surviving when things go wrong".
#
# THREATS ADDRESSED:
# 1. Bit-Rot: Silent data corruption caused by aging hardware.
# 2. Ransomware: Malicious encryption or deletion of primary data.
# 3. Accidental Deletion: Human error by an administrator.
# =============================================================================

class ResilienceManager:
    """
    Manages data redundancy (Backups) and automated recovery (Self-Healing).
    """

    def create_backup(self, product_id):
        """
        Generates a redundant copy of an archived product.
        
        ARGUMENTS:
            product_id (str): The unique identifier of the product to back up.
            
        RATIONALE:
        In the space industry, we follow the 'redundancy' principle. We never
        trust a single storage device with irreplaceable satellite data.
        """
        # Step 1: Define where the original file is currently stored (The Source)
        original_file = os.path.join(config.ARCHIVE_DIR, f"{product_id}.enc")
        
        # Step 2: Define where the backup should be placed (The Destination)
        backup_file = os.path.join(config.BACKUP_DIR, f"{product_id}.enc")
        
        # Step 3: Safety check - Ensure the backup folder physically exists on disk
        if not os.path.exists(config.BACKUP_DIR):
            # Create the directory and any necessary parent directories
            os.makedirs(config.BACKUP_DIR)
            
        # Step 4: Verification - Can we find the original file?
        if os.path.exists(original_file):
            # If yes, execute the copy operation
            # Note: We are copying the ENCRYPTED (.enc) version.
            # RATIONALE: Backups must be just as secure as the primary archive.
            shutil.copy(original_file, backup_file)
            # Log the successful redundancy event
            audit_log.info(f"[BACKUP] SUCCESS: Redundant copy created for product {product_id}")
            return True
        else:
            # If the original is missing, we cannot back it up
            audit_log.error(f"[BACKUP] FAILED: Could not find source file {original_file} for backup.")
            return False

    def verify_and_restore(self, product_id, expected_hash_fn=None):
        """
        The "Self-Healing" logic. Detects corruption and automatically repairs it.
        
        ARGUMENTS:
            product_id (str): The product to check.
            expected_hash_fn (function): A callback to retrieve the "Source of Truth" hash.
            
        TECHNICAL FLOW:
        1. Calculate Hash of Primary File.
        2. Compare with Reference Hash.
        3. If Match -> All good.
        4. If Mismatch -> Data is broken. Copy from Backup to fix.
        """
        # Define paths to the primary and backup files
        primary_file = os.path.join(config.ARCHIVE_DIR, f"{product_id}.enc")
        backup_file = os.path.join(config.BACKUP_DIR, f"{product_id}.enc")
        
        # Log the start of the health check
        audit_log.info(f"[RESILIENCE] Initiating integrity audit for {product_id}...")
        
        # Step 1: Check for the existence of the primary file
        if not os.path.exists(primary_file):
            # If the file is physically missing, that is a critical failure
            audit_log.error(f"[RESILIENCE] ALERT: Primary file for {product_id} is MISSING from disk!")
            current_hash = None
        else:
            # If it exists, calculate its current SHA-256 fingerprint
            # RATIONALE: This detects even a single bit change (the 'Avalanche Effect').
            current_hash = security.calculate_hash(primary_file)
            
        # Step 2: Retrieve the "Known Good" hash for comparison
        # This hash was recorded during Ingestion or Processing and is our Ground Truth.
        if expected_hash_fn:
            # Call the provided function to get the reference hash
            known_good = expected_hash_fn(product_id)
            
            # Step 3: The Integrity Decision
            if current_hash != known_good:
                # -------------------------------------------------------------
                # THE HEALING PROCESS (Recovery)
                # -------------------------------------------------------------
                # If hashes don't match, the data is officially corrupted or tampered with.
                audit_log.error(f"[RESILIENCE] INTEGRITY FAILURE: Hash mismatch detected for {product_id}!")
                audit_log.info(f"[RESILIENCE] Attempting automated self-healing from backup...")
                
                # Step 4: Check if we have a healthy backup to restore from
                if os.path.exists(backup_file):
                    # Step 5: Execute the Restore (Overwrite the corrupted file with the good backup)
                    shutil.copy(backup_file, primary_file)
                    # Log the successful recovery
                    audit_log.info(f"[RESILIENCE] SUCCESS: Product {product_id} restored and healed.")
                    return True
                else:
                    # Case: Primary is broken AND Backup is missing. This is a disaster.
                    audit_log.error(f"[RESILIENCE] CRITICAL: Backup also missing. Data loss is permanent.")
                    return False
        
        # If the hashes matched, log that the system is healthy
        audit_log.info(f"[RESILIENCE] INTEGRITY VERIFIED: {product_id} is healthy.")
        return True
