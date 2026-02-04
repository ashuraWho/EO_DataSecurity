# Import the os module for interacting with the filesystem (finding files, joining paths)
import os
# Import json for reading and updating the product's metadata record
import json
# Import NumPy to perform mathematical operations on the scientific data
import numpy as np
# Import the central configuration to access the processing directory path
from secure_eo_pipeline import config
# Import the security utility to verify and update data integrity hashes
from secure_eo_pipeline.utils import security
# Import the shared audit logger to record processing milestones
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Processing & Quality Control Component - Line-by-Line Explanation
# =============================================================================
# ROLE IN ARCHITECTURE:
# The "Scientific Factory".
# This component takes raw Level-0 data (raw signals) and converts them into
# Level-1 products (calibrated reflectance values).
#
# SECURITY & TRUST:
# Processing is the moment where data changes. In a secure pipeline, we must
# ensure that the data we are processing hasn't been tampered with since ingestion.
#
# QC (QUALITY CONTROL):
# We check for sensor malfunctions (NaN values) to ensure data 'Cleanliness'.
# =============================================================================

class ProcessingEngine:
    """
    Handles the scientific transformation and quality assurance of EO data.
    """

    def process_product(self, product_id):
        """
        Executes a Level-0 to Level-1 processing chain.

        ARGUMENTS:
            product_id (str): The unique ID of the product currently in staging.
        """
        # Step 1: Define paths to the input files within the Processing Staging area
        input_file = os.path.join(config.PROCESSING_DIR, f"{product_id}.npy")
        input_meta = os.path.join(config.PROCESSING_DIR, f"{product_id}.json")

        # Step 2: Log the start of the processing session
        audit_log.info(f"[PROCESS] START: Processing Level-0 -> Level-1 for {product_id}")

        # ---------------------------------------------------------------------
        # PHASE 1: INTEGRITY VERIFICATION (Chain of Custody)
        # ---------------------------------------------------------------------
        # Before we touch the data, we must prove it is the SAME data that was ingested.
        try:
            # Step 1: Read the metadata to find the "Expected Hash"
            with open(input_meta, "r") as f:
                meta = json.load(f)

            # Step 2: Retrieve the hash recorded by the Ingestion component
            expected_hash = meta.get("original_hash")

            # Step 3: Calculate the ACTUAL hash of the file right now
            actual_hash = security.calculate_hash(input_file)

            # Step 4: Compare. If they don't match, someone edited the file illegally!
            if actual_hash != expected_hash:
                audit_log.error(f"[PROCESS] SECURITY ALERT: Input integrity mismatch for {product_id}!")
                # STOP: Do not process tampered data.
                return None
        except Exception as e:
            # Handle cases where files are missing or metadata is corrupted
            audit_log.error(f"[PROCESS] FAILED: Could not verify input integrity. Error: {e}")
            return None

        # ---------------------------------------------------------------------
        # PHASE 2: DATA LOADING & QUALITY CONTROL (QC)
        # ---------------------------------------------------------------------
        try:
            # Step 1: Load the binary scientific data into memory (as a NumPy array)
            data = np.load(input_file)

            # Step 2: Perform the "Cleanliness" Check (Quality Control)
            # Sensors sometimes fail and produce 'Not a Number' (NaN) values.
            # RATIONALE: We don't want to waste storage space on garbage data.
            if np.isnan(data).any():
                # If even one pixel is NaN, we flag it as a Quality Failure.
                audit_log.warning(f"[QC] REJECTED: Sensor corruption (NaN) detected in product {product_id}.")
                # Fail the processing step.
                return None

        except Exception as e:
            # Handle file read errors or memory issues
            audit_log.error(f"[PROCESS] FAILED: Data load error for {product_id}. Error: {e}")
            return None

        # ---------------------------------------------------------------------
        # PHASE 3: SCIENTIFIC TRANSFORMATION
        # ---------------------------------------------------------------------
        # Simulation: Radiometric Calibration.
        # We assume the raw data is in 8-bit integers (0-255).
        # We normalize this to a percentage reflectance (0.0 to 1.0).
        processed_data = data / 255.0

        # Step 1: Overwrite the binary file in the staging area with the NEW processed version.
        np.save(input_file, processed_data)

        # ---------------------------------------------------------------------
        # PHASE 4: PROVENANCE TRACKING (Updating the Record)
        # ---------------------------------------------------------------------
        # Since the file content has changed, we must document the transformation.

        # Step 1: Record the new processing level and status
        meta["processing_level"] = "Level-1C" # The product has been calibrated
        meta["status"] = "PROCESSED"
        meta["qc_status"] = "PASSED"

        # Step 2: CALCULATE A NEW HASH.
        # RATIONALE: The old hash is no longer valid because the content is different.
        # We need a new "Digital Signature" for the Level-1 product.
        new_hash = security.calculate_hash(input_file)
        # We store this as the "Processed Hash" to maintain the Chain of Custody.
        meta["processed_hash"] = new_hash

        # Step 3: Save the updated metadata back to disk
        with open(input_meta, "w") as f:
            json.dump(meta, f, indent=4)

        # Step 4: Finalize the log for the audit trail
        audit_log.info(f"[PROCESS] SUCCESS: {product_id} is now Level-1 certified. New Hash: {new_hash}")

        # Return the path to the processed product
        return input_file
