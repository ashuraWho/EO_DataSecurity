# Import the os module to handle file paths in an operating-system-agnostic way (works on Windows, Linux, and macOS)
import os

# =============================================================================
# Secure EO Pipeline - Configuration Module
# =============================================================================
# PURPOSE:
# This module acts as the "Central Nervous System" for project settings.
# It defines the file system structure, security parameters, and access policies.
#
# DESIGN RATIONALE:
# By centralizing configuration, we avoid "Hardcoding" (typing paths directly
# into scripts). This makes the system more maintainable, scalable, and secure.
# =============================================================================

# -----------------------------------------------------------------------------
# 1. FILE SYSTEM ARCHITECTURE
# -----------------------------------------------------------------------------
# We simulate a ground segment environment using specialized directories.
# In a real mission, these would be distributed across different servers or clouds.
# -----------------------------------------------------------------------------

# Base directory for all simulation artifacts. 
# Using a relative path ("simulation_data") keeps the project portable.
BASE_DIR = "simulation_data"  # Defines `BASE_DIR` as the root of runtime data

# [Landing Zone]
# Where raw satellite data first arrives. 
# SECURITY LEVEL: LOW (External data is untrusted and must be validated).
# os.path.join() is used to construct the path correctly for any OS.
INGEST_DIR = os.path.join(BASE_DIR, "ingest_landing_zone")  # Defines `INGEST_DIR` path

# [Processing Staging]
# A temporary workspace where data is transformed.
# SECURITY LEVEL: MEDIUM (Data is within the security boundary but not yet archived).
PROCESSING_DIR = os.path.join(BASE_DIR, "processing_staging")  # Defines `PROCESSING_DIR` path.

# [Secure Archive]
# The final storage for verified products.
# SECURITY LEVEL: HIGH (Data here MUST be encrypted-at-rest and checked for integrity).
ARCHIVE_DIR = os.path.join(BASE_DIR, "secure_archive")  # Defines `ARCHIVE_DIR` path

# [Resilience Backup]
# A redundant copy of the archive kept in a separate logical/physical location.
# PURPOSE: Disaster Recovery. If the Archive is corrupted, we restore from here.
BACKUP_DIR = os.path.join(BASE_DIR, "backup_storage")  # Defines `BACKUP_DIR` path

# Path to the symmetric encryption key file.
# WARNING: This is a critical security asset. In this simulation, it's a local file.
# In a real system, this would be managed by an HSM (Hardware Security Module).
KEY_PATH = "secret.key"  # Defines `KEY_PATH` for the encryption key

# Helper list of all system directories.
# The application uses this list to automatically create the folder structure at startup.
directories = [INGEST_DIR, PROCESSING_DIR, ARCHIVE_DIR, BACKUP_DIR]  # Defines `directories` list of paths

# -----------------------------------------------------------------------------
# 2. IDENTITY & ACCESS MANAGEMENT (IAM)
# -----------------------------------------------------------------------------
# We implement a Role-Based Access Control (RBAC) model.
# Principle: "Least Privilege" -> Users only get what they absolutely need to work.
# -----------------------------------------------------------------------------

# Define the Roles and their associated permissions
ROLES = {
    # 'admin' role: The highest level of trust. Can manage the security core itself.
    "admin": {
        "description": "Full system control including security management",
        "permissions": ["read", "write", "delete", "manage_keys"]
    },
    # 'analyst' role: Trusted to process and view data, but cannot delete archives.
    "analyst": {
        "description": "Data processing and quality control specialist",
        "permissions": ["read", "write", "process"]
    },
    # 'user' role: Least trusted. Can only view the final products.
    "user": {
        "description": "Standard end user with read-only access",
        "permissions": ["read"]
    }
}

# -----------------------------------------------------------------------------
# 3. USER DATABASE (MOCK)
# -----------------------------------------------------------------------------
# This maps specific user identities to their assigned roles.
# In a real environment, this data would come from Active Directory.
# -----------------------------------------------------------------------------
USERS = {
    # 'emanuele_admin' is assigned the 'admin' role (Full Power)
    "emanuele_admin": "admin",      
    # 'bob_analyst' is assigned the 'analyst' role (Can process data)
    "bob_analyst": "analyst",    
    # 'charlie_user' is assigned the 'user' role (Can only read)
    "charlie_user": "user",      
    # 'eve_hacker' has no valid role, representing an unauthorized intruder
    "eve_hacker": "none"         
}
