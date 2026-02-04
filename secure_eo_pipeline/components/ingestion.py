# Import os for file management
import os
# Import json for reading schemas
import json
# Import shutil for moving files
import shutil
# Import project config
from secure_eo_pipeline import config
# Import security utils for Hashing
from secure_eo_pipeline.utils import security
# Import logging
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Secure Ingestion Component
# =============================================================================
# ROLE IN ARCHITECTURE:
# The "Border Guard".
# Data arriving from the satellite (Source) is "Untrusted" until verified.
# This component validates it before letting it enter the internal implementation.
#
# SECURITY PRINCIPLES:
# 1. Input Validation: Check schemas and formats.
# 2. Integrity Baselining: Capture the Hash NOW so we can detect changes later.
# =============================================================================

class IngestionManager:
    """
    Handles the secure intake of new EO products.
    """

    def ingest_product(self, product_id):
        """
        Validates and registers a product.
        
        FLOW:
        1. Check existence -> 2. Check Schema -> 3. Hash -> 4. Move to Process
        """
        
        audit_log.info(f"[INGEST] Starting ingestion for {product_id}")
        
        # Define paths in the Landing Zone (Ingest Dir)
        source_file = os.path.join(config.INGEST_DIR, f"{product_id}.npy")
        source_meta = os.path.join(config.INGEST_DIR, f"{product_id}.json")
        
        # ---------------------------------------------------------------------
        # VALIDATION PHASE
        # ---------------------------------------------------------------------
        
        # Check 1: Do files actually exist?
        if not os.path.exists(source_file) or not os.path.exists(source_meta):
            # Error if missing
            audit_log.error(f"[INGEST] FAILED: Missing files for {product_id}")
            return None
            
        # Check 2: Schema Validation (Is the JSON structured correctly?)
        try:
            with open(source_meta, "r") as f:
                meta = json.load(f)
                # Define list of fields that MUST be there
                required_keys = ["product_id", "timestamp", "sensor"]
                # If any key is missing, REJECT the file.
                if not all(key in meta for key in required_keys):
                    raise ValueError("Missing required metadata fields")
        except Exception as e:
            # Catch bad JSON or missing fields
            audit_log.error(f"[INGEST] FAILED: Invalid metadata for {product_id}. Error: {e}")
            return None

        # ---------------------------------------------------------------------
        # INTEGRITY BASELINING PHASE
        # ---------------------------------------------------------------------
        
        # Check 3: Calculate the "Source of Truth" Hash.
        # We do this immediately. This hash is our reference for the rest of eternity.
        file_hash = security.calculate_hash(source_file)
        
        # We store this hash IN the metadata.
        # This binds the data content to its description.
        meta["original_hash"] = file_hash
        meta["status"] = "INGESTED"
        
        # ---------------------------------------------------------------------
        # TRANSFER PHASE
        # ---------------------------------------------------------------------
        
        # Ensure destination exists
        if not os.path.exists(config.PROCESSING_DIR):
            os.makedirs(config.PROCESSING_DIR)
            
        # Describe where the files are going (Processing Staging)
        dest_file = os.path.join(config.PROCESSING_DIR, f"{product_id}.npy")
        dest_meta = os.path.join(config.PROCESSING_DIR, f"{product_id}.json")
        
        # Move files from "Untrusted" (Ingest) to "Trusted" (Processing)
        shutil.copy(source_file, dest_file)
        
        # Save updated metadata (now containing the Hash)
        with open(dest_meta, "w") as f:
            json.dump(meta, f, indent=4)
            
        # Log Success
        audit_log.info(f"[INGEST] SUCCESS: Product {product_id} ingested. Hash: {file_hash}")
        # Return path to the moved file
        return dest_file
