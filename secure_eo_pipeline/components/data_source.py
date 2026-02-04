# Import OS module
import os
# Import JSON for metadata handling
import json
# Import time for timestamps
import time
# Import NumPy for heavy math/data simulation
import numpy as np
# Import project config
from secure_eo_pipeline import config
# Import audit logger
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Data Source Component (Simulator)
# =============================================================================
# ROLE IN ARCHITECTURE:
# This component acts as the "Satellite" or "Instrument".
# It creates the raw data that feeds the rest of the pipeline.
#
# WHY SIMULATE?
# Real satellite data (like Sentinel-2) is massive (GBs) and complex.
# For observing security behavior, we only need a "representative" file structure
# (Binary Data + JSON Metadata).
# =============================================================================

class EOSimulator:
    """
    Simulates the creation of EO products (Mission Data).
    """

    def __init__(self):
        # Ensure the landing zone exists so we have somewhere to put the data.
        # If the folder is missing, we create it.
        if not os.path.exists(config.INGEST_DIR):
            os.makedirs(config.INGEST_DIR)
            
    def generate_product(self, product_id, corrupted=False):
        """
        Generates a synthetic EO product.
        
        ARGUMENTS:
            product_id: Unique name (e.g., "S1A_20240101...").
            corrupted: Boolean flag. If True, we intentionally break the data
                       to test if the system detects it later.
        """
        # Log the start of the event
        audit_log.info(f"[SOURCE] Generating EO product: {product_id} (Corrupted={corrupted})")
        
        # 1. CREATE BINARY DATA (The "Image")
        # We use NumPy to create a 3D Matrix (100x100 pixels, 3 bands/colors).
        # This mimics the structure of a multi-spectral image.
        data = np.random.rand(100, 100, 3).astype(np.float32)
        
        # SIMULATION TRICK:
        # If 'corrupted' is requested, we inject 'NaN' (Not a Number).
        # This mimics a "Dead Pixel" or "Sensor Malfunction".
        if corrupted:
            data[50, 50, 0] = np.nan 
            
        # 2. DEFINE PATHS
        # We save two files: .npy (the heavy data) and .json (the description)
        file_name = f"{product_id}.npy"
        # Join path with Ingest Directory
        file_path = os.path.join(config.INGEST_DIR, file_name)
        meta_path = os.path.join(config.INGEST_DIR, f"{product_id}.json")
        
        # 3. WRITE TO DISK
        # Save the numpy array
        np.save(file_path, data)
        
        # 4. CREATE METADATA
        # Metadata is CRITICAL for security. It tells us:
        # - WHEN data was created (Timestamp)
        # - WHO created it (Sensor ID)
        # - WHERE it is (Orbit)
        # Without metadata, a binary file is meaningless blob.
        metadata = {
            "product_id": product_id,
            "timestamp": time.time(),
            "sensor": "Simulated-MSI",
            "orbit": 1234,
            # Fake scientific attribute
            "cloud_cover_percentage": np.random.uniform(0, 100)
        }
        
        # Write metadata JSON
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=4)
            
        # Log success
        audit_log.info(f"[SOURCE] Product generated and landed at: {file_path}")
        # Return path so other components know where to find it
        return file_path
