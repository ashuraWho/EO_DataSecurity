from secure_eo_pipeline import config  # For users and roles
from secure_eo_pipeline.utils.logger import audit_log  # For security events

# =============================================================================
# Access Control Component (RBAC)
# =============================================================================
# ROLE IN ARCHITECTURE:
# This is the "Security Gateway". It sits between the User and the Data.
#
# MODEL: Role-Based Access Control (RBAC).
# - We do NOT assign permissions to people.
# - We assign permissions to ROLES.
# - We then assign ROLES to people.
#
# WHY THIS IS SECURE:
# This ensures "Consistency". If we update the 'Analyst' role, 1000 analysts 
# get the update immediately without manual error.
# =============================================================================

import bcrypt  # For password verification

class AccessController:
    
    """
    Enforces the security policies defined in config.py.
    Provides two distinct services: Authentication (Who are you?) and Authorization (What can you do?).
    """

    def authenticate(self, username, password):
        
        """
        Validates the identity of the user.
        
        ARGUMENTS:
            username (str): The identifier provided by the user.
            password (str): The secret password to verify.
            
        LOGIC:
        Checks the mock 'database' in config.py.
        - If user not found: Fail.
        - If password hash mismatch: Fail.
        - If verified: Return role.
        """
        
        # Step 1: Query the user database for the provided username
        user_record = config.USERS_DB.get(username)
        
        # Step 2: Treat missing users as authentication failures
        if not user_record:
            # Case A: User is unknown
            # RATIONALE: We use generic error messages in logs? No, logs should be specific.
            # User facing errors should be generic ("Invalid credentials") to prevent enumeration.
            audit_log.warning(f"[AUTH] FAILURE: Unknown user '{username}'.")
            return None
            
        # Step 3: Verify the password against the stored bcrypt hash
        stored_hash = user_record["hash"].encode('utf-8')
        role = user_record["role"]
        
        if role == "none":
             audit_log.warning(f"[AUTH] FAILURE: User '{username}' is disabled/banned.")
             return None

        # Check password
        # bcrypt.checkpw requires bytes for both arguments
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            # Case B: Password matches. Log success.
            audit_log.info(f"[AUTH] SUCCESS: User '{username}' identified as '{role}'.")
            return role
        else:
            # Case C: Password mismatch
            audit_log.warning(f"[AUTH] FAILURE: Invalid password for '{username}'.")
            return None



    def authorize(self, username, action):
        
        """
        Validates if an authenticated user has the right to perform a specific action.
        
        ARGUMENTS:
            username (str): The identity to check.
            action (str): The operation (e.g., 'read', 'write', 'process', 'manage_keys').
            
        GOAL:
        Enforce the principle of "Least Privilege".
        """
        
        # NOTE: In a stateful session (like CLI), we usually don't re-authenticate with password
        # for every single action. We trust the 'current_role' stored in session (main.py).
        # However, for this specific class design, we need to look up the role from the username.
        
        # Lookup role directly from DB (simulating a session token check)
        user_record = config.USERS_DB.get(username)
        
        if not user_record:
            return False
            
        role_name = user_record["role"]
        
        # Step 3: Map the Role Name to its detailed definition in the config
        # This tells us exactly what permissions this role holds.
        role_def = config.ROLES.get(role_name)  # Looks up the role definition
        
        # Step 4: Safety check. If the role exists in USERS but not in ROLES (misconfiguration)
        if not role_def:
            # Log a system error
            audit_log.error(f"[ACCESS] CONFIG ERROR: Role '{role_name}' is not defined in the master policy.")  # Logs error if role is undefined
            return False
            
        # Step 5: Extract the list of allowed actions for this role
        # If the 'permissions' key is missing, default to an empty list (Secure Fail)
        permissions = role_def.get("permissions", [])  # Gets the permission list, defaulting to empty
        
        # Step 6: The Core Permission Check
        # Does the list of allowed permissions contain the requested action?
        if action in permissions:  # Checks if the action is allowed
            # ACCESS GRANTED
            # RATIONALE: Logging successful access creates a clear audit trail.
            audit_log.info(f"[ACCESS] GRANTED: {username} ({role_name}) is authorized for '{action}'.")  # Logs access granted and returns True
            return True
        else:
            # ACCESS DENIED
            # RATIONALE: This log is critical for detecting 'Privilege Escalation' attempts.
            audit_log.warning(f"[ACCESS] DENIED: {username} ({role_name}) missing required permission: '{action}'.")  # Logs access denied and returns False
            return False
