# Import OS module to handle file paths in an operating-system-agnostic way
import os

# =============================================================================
# Secure EO Pipeline - Configuration Module
# =============================================================================
# PURPOSE:
# This module acts as the "Central Nervous System" for configuration.
# It defines:
# 1. File Paths (Where data lives)
# 2. Security Parameters (Where keys live)
# 3. Access Control Policies (Who can do what)
#
# DESIGN RATIONALE:
# Hardcoding paths in random scripts is bad practice (Security & Maintainability).
# By centralizing them here, we can easily switch between "Dev", "Test", and "Prod" environments.
# =============================================================================

# -----------------------------------------------------------------------------
# 1. FILE SYSTEM ARCHITECTURE
# -----------------------------------------------------------------------------
# We simulate a distributed ground segment using local folders.
# In a real ESA mission, these might be:
# - INGEST_DIR -> An S3 Bucket or FTP Landing Zone
# - ARCHIVE_DIR -> A Tape Library or Glacier Storage
# -----------------------------------------------------------------------------

# Base directory for all simulation artifacts. 
# Using a relative path keeps the project portable.
BASE_DIR = "simulation_data"

# [Landing Zone]
# Where raw satellite data "lands" first. 
# Security Level: LOW (Untrusted content).
# We use os.path.join to ensure this works on Windows and Linux/Mac.
INGEST_DIR = os.path.join(BASE_DIR, "ingest_landing_zone")

# [Processing Staging]
# Temporary workspace for computation.
# Security Level: MEDIUM (Data is being modified).
PROCESSING_DIR = os.path.join(BASE_DIR, "processing_staging")

# [Secure Archive]
# The final resting place for products.
# Security Level: HIGH (Data must be Encrypted & Immutable).
ARCHIVE_DIR = os.path.join(BASE_DIR, "secure_archive")

# [Resilience Backup]
# A physically separate copy of the data.
# Security Level: HIGH (Must be kept completely independent of Archive to survive disaster).
BACKUP_DIR = os.path.join(BASE_DIR, "backup_storage")

# Path to the symmetric encryption key.
# CRITICAL SECURITY ASSET: If this is lost, all data in ARCHIVE_DIR is unreadable.
# In production, this path would point to a hardware device (HSM) or Vault reference.
KEY_PATH = "secret.key"

# Helper list to ensure these exist at startup
# The application will loop through this and create them if missing.
directories = [INGEST_DIR, PROCESSING_DIR, ARCHIVE_DIR, BACKUP_DIR]

# -----------------------------------------------------------------------------
# 2. IDENTITY & ACCESS MANAGEMENT (IAM)
# -----------------------------------------------------------------------------
# We implement a simplified Role-Based Access Control (RBAC) model.
# Principle: "Least Privilege" -> Users only get the permissions they absolutely need.
# -----------------------------------------------------------------------------

ROLES = {
    # The 'God Mode' role. 
    # Can manage encryption keys (very dangerous) and delete data.
    "admin": {
        "description": "Full system control",
        "permissions": ["read", "write", "delete", "manage_keys"]
    },
    # The Scientist/Engineer role.
    # Can create and view data, but CANNOT delete critical archives or touch keys.
    "analyst": {
        "description": "Data processing and quality control",
        "permissions": ["read", "write", "process"]
    },
    # The Consumer role.
    # Can only VIEW data. Cannot modify or delete anything.
    "user": {
        "description": "End user consuming EO products",
        "permissions": ["read"]
    }
}

# -----------------------------------------------------------------------------
# 3. USER DATABASE (MOCK)
# -----------------------------------------------------------------------------
# In a real system, this would be replaced by LDAP, Active Directory, or OIDC.
# Here, we map usernames directly to roles for demonstration.
# -----------------------------------------------------------------------------
USERS = {
    "emanuele_admin": "admin",      # Has full power
    "bob_analyst": "analyst",    # Can process data
    "charlie_user": "user",      # Read-only
    "eve_hacker": "none"         # Represents an intruder with no valid account
}
