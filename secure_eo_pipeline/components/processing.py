# Import OS module for path handling
import os
# Import JSON for metadata modification
import json
# Import NumPy for data processing
import numpy as np
# Import project configuration
from secure_eo_pipeline import config
# Import security utils (for re-hashing)
from secure_eo_pipeline.utils import security
# Import logger
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Processing & Quality Control Component
# =============================================================================
# ROLE IN ARCHITECTURE:
# The "Factory".
# Takes validated raw data and transforms it into useful scientific products.
#
# SECURITY IMPLICATION:
# When we process data, we change it. This changes its Hash.
# Therefore, we must:
# 1. Verify input integrity (Is it still valid?)
# 2. Process/Transform
# 3. Calculate NEW integrity (Provenance)
# =============================================================================

class ProcessingEngine:
    """
    Handles data processing and Quality Control (QC).
    """

    def process_product(self, product_id):
        """
        Simulates Level-0 to Level-1 processing.
        """
        # Define paths to input files (in Processing Staging)
        input_file = os.path.join(config.PROCESSING_DIR, f"{product_id}.npy")
        input_meta = os.path.join(config.PROCESSING_DIR, f"{product_id}.json")
        
        audit_log.info(f"[PROCESS] Starting processing for {product_id}")
        
        # 1. LOAD DATA
        try:
            # Load the binary numpy array
            data = np.load(input_file)
        except Exception as e:
            # Handle load errors (e.g., file lock, missing)
            audit_log.error(f"[PROCESS] ERROR: Could not load {product_id}. {e}")
            return None
            
        # ---------------------------------------------------------------------
        # QUALITY CONTROL (QC) PHASE
        # ---------------------------------------------------------------------
        # In EO, sensors can fail, clouds can block view, or cosmic rays can hit bits.
        # We must check if the data is "Science Ready".
        
        # Check: Are there any "Not a Number" values?
        # a 'NaN' usually indicates a missing pixel or sensor error
        if np.isnan(data).any():
            audit_log.warning(f"[QC] FAILED: Data corruption detected in {product_id} (NaN values found).")
            # FAIL-SAFE: We return None. We stop the pipeline. 
            # We do NOT pass bad data to the archive.
            return None
            
        # ---------------------------------------------------------------------
        # TRANSFORMATION PHASE
        # ---------------------------------------------------------------------
        # Simulation: Simple division (Radiometric Calibration)
        # We convert "Digital Numbers" (DN) to "Top of Atmosphere Reflectance"
        processed_data = data / 255.0
        
        # OVERWRITE the file with the new version
        np.save(input_file, processed_data)
        
        # ---------------------------------------------------------------------
        # PROVENANCE TRACKING
        # ---------------------------------------------------------------------
        # We must document that this file has changed.
        
        # Load the metadata
        with open(input_meta, "r") as f:
            meta = json.load(f)
            
        # Update metadata fields
        meta["processing_timestamp"] = "NOW"
        meta["processing_level"] = "L1" # It has leveled up
        meta["status"] = "PROCESSED"
        
        # IMPORTANT: Calculate a NEW hash for the NEW content.
        # This creates a "Chain of Custody". The old hash is for the old file.
        new_hash = security.calculate_hash(input_file)
        meta["processed_hash"] = new_hash
        
        # Save updated metadata
        with open(input_meta, "w") as f:
            json.dump(meta, f, indent=4)
            
        # Log success
        audit_log.info(f"[PROCESS] SUCCESS: Product {product_id} processed to Level-1.")
        # Return path
        return input_file
