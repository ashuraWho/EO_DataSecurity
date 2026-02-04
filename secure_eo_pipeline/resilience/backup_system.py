# Import OS & Shutil for file ops
import os
import shutil
# Import time
import time
# Import Config
from secure_eo_pipeline import config
# Import Security (for Hashing)
from secure_eo_pipeline.utils import security
# Import Logger
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Resilience & Backup System
# =============================================================================
# ROLE IN ARCHITECTURE:
# The "Disaster Recovery" mechanism.
# Security is not just keeping hackers out; it's ensuring data SURVIVES.
#
# THREATS ADDRESSED:
# 1. Data Corruption (Bit Rot): Random flips in storage bits.
# 2. Ransomware/Deletion: Accidental or malicious deletion of primary copy.
# =============================================================================

class ResilienceManager:
    """
    Manages data redundancy and recovery operations.
    """

    def create_backup(self, product_id):
        """
        Creates a REDUNDANT copy.
        
        RATIONALE:
        "Two is one, one is none."
        If we only have one copy and the disk melts, the mission fails.
        """
        # Define source (Primary Archive)
        original_file = os.path.join(config.ARCHIVE_DIR, f"{product_id}.enc")
        # Define dest (Backup Vault)
        backup_file = os.path.join(config.BACKUP_DIR, f"{product_id}.enc")
        
        # Ensure backup dir exists
        if not os.path.exists(config.BACKUP_DIR):
            os.makedirs(config.BACKUP_DIR)
            
        # Check if source exists
        if os.path.exists(original_file):
            # We copy the ENCRYPTED file. 
            # The backup should also be encrypted for security.
            shutil.copy(original_file, backup_file)
            audit_log.info(f"[BACKUP] System backup created for {product_id}")
            return True
        else:
            audit_log.error(f"[BACKUP] FAILED: Original file not found for {product_id}")
            return False

    def verify_and_restore(self, product_id, expected_hash_fn=None):
        """
        The "Self-Healing" logic.
        
        FLOW:
        1. Calculate Hash of Primary File.
        2. Compare with Expected Hash.
        3. If Match -> Good.
        4. If Mismatch -> CORRUPTION DETECTED.
        5. Trigger Copy from Backup to overwrite bad file.
        """
        # Paths
        primary_file = os.path.join(config.ARCHIVE_DIR, f"{product_id}.enc")
        backup_file = os.path.join(config.BACKUP_DIR, f"{product_id}.enc")
        
        audit_log.info(f"[RESILIENCE] Checking integrity for {product_id}...")
        
        # 1. DIAGNOSIS
        if not os.path.exists(primary_file):
             # FILE MISSING
            audit_log.error(f"[RESILIENCE] CRITICAL: Primary file missing!")
            current_hash = None
        else:
            # CHECK INTEGRITY
            # Get the current fingerprint of the file
            current_hash = security.calculate_hash(primary_file)
            
        # Check against reference (provided by caller/metadata)
        # In a real system, this would come from a secure DB.
        if expected_hash_fn:
            known_good = expected_hash_fn(product_id)
            
            # Compare Current vs Good
            if current_hash != known_good:
                # -------------------------------------------------------------
                # TRIGGER DISASTER RECOVERY
                # -------------------------------------------------------------
                audit_log.error(f"[RESILIENCE] CORRUPTION DETECTED in Primary Storage!")
                audit_log.info(f"[RESILIENCE] Initiating automated recovery...")
                
                # Check if backup exists
                if os.path.exists(backup_file):
                    # RESTORE: Overwrite the bad file with the backup
                    shutil.copy(backup_file, primary_file)
                    audit_log.info(f"[RESILIENCE] SUCCESS: Data restored from backup.")
                    return True
                else:
                    audit_log.error(f"[RESILIENCE] FAILED: Backup not found. Data lost.")
                    return False
        
        # If we got here, everything is fine.
        audit_log.info(f"[RESILIENCE] Integrity Check Passed.")
        return True
