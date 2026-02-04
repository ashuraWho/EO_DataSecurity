# Import the central configuration module to access the USERS and ROLES dictionaries
from secure_eo_pipeline import config
# Import the shared audit log utility to record security events (Success/Failure)
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Access Control Component (RBAC) - Line-by-Line Explanation
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

class AccessController:
    """
    Enforces the security policies defined in config.py.
    Provides two distinct services: Authentication (Who are you?) and Authorization (What can you do?).
    """

    def authenticate(self, username):
        """
        Validates the identity of the user.
        
        ARGUMENTS:
            username (str): The identifier provided by the user.
            
        LOGIC:
        Checks the mock 'database' in config.py.
        - If found: returns the user's role.
        - If not found: returns None (Access Denied).
        """
        # Step 1: Query the user dictionary for the provided username
        # .get() is safer than direct access because it doesn't crash if the key is missing
        role = config.USERS.get(username)
        
        # Step 2: Treat missing or explicitly unprivileged roles as authentication failures
        if not role or role == "none":
            # Case A: User is unknown or explicitly blocked
            # RATIONALE: Warning logs alert security admins of potential intrusion.
            audit_log.warning(f"[AUTH] FAILURE: Invalid login attempt for '{username}'.")
            # Return None to indicate identity could not be verified
            return None
        
        # Case B: User is known and has a valid role. Log success.
        audit_log.info(f"[AUTH] SUCCESS: User '{username}' identified as '{role}'.")
        # Return the role string (e.g., 'admin', 'analyst')
        return role

    def authorize(self, username, action):
        """
        Validates if an authenticated user has the right to perform a specific action.
        
        ARGUMENTS:
            username (str): The identity to check.
            action (str): The operation (e.g., 'read', 'write', 'process', 'manage_keys').
            
        GOAL:
        Enforce the principle of "Least Privilege".
        """
        # Step 1: Who is this? We call authenticate() to get their role.
        role_name = self.authenticate(username)
        
        # Step 2: Immediate denial if authentication failed (No ID = No Access)
        if not role_name:
            # Return False to the calling function (Operation Blocked)
            return False
            
        # Step 3: Map the Role Name to its detailed definition in the config
        # This tells us exactly what permissions this role holds.
        role_def = config.ROLES.get(role_name)
        
        # Step 4: Safety check. If the role exists in USERS but not in ROLES (misconfiguration)
        if not role_def:
            # Log a system error
            audit_log.error(f"[ACCESS] CONFIG ERROR: Role '{role_name}' is not defined in the master policy.")
            return False
            
        # Step 5: Extract the list of allowed actions for this role
        # If the 'permissions' key is missing, default to an empty list (Secure Fail)
        permissions = role_def.get("permissions", [])
        
        # Step 6: The Core Permission Check
        # Does the list of allowed permissions contain the requested action?
        if action in permissions:
            # ACCESS GRANTED
            # RATIONALE: Logging successful access creates a clear audit trail.
            audit_log.info(f"[ACCESS] GRANTED: {username} ({role_name}) is authorized for '{action}'.")
            return True
        else:
            # ACCESS DENIED
            # RATIONALE: This log is critical for detecting 'Privilege Escalation' attempts.
            audit_log.warning(f"[ACCESS] DENIED: {username} ({role_name}) missing required permission: '{action}'.")
            return False
