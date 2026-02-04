# Import configuration for User/Role definitions
from secure_eo_pipeline import config
# Import Logger
from secure_eo_pipeline.utils.logger import audit_log

# =============================================================================
# Access Control Component (RBAC)
# =============================================================================
# ROLE IN ARCHITECTURE:
# The "bouncer" at the club.
# It enforces POLICY.
#
# MODEL: Role-Based Access Control (RBAC).
# - Users are assigned ROLES (Admin, User, etc).
# - Roles have PERMISSIONS (Read, Write, Delete).
#
# WHY RBAC?
# It scales better than assigning permissions to every single user individually.
# =============================================================================

class AccessController:
    """
    Enforces RBAC policies.
    """

    def authenticate(self, username):
        """
        Validates ID.
        
        In simulation: Checks if username exists in config dictionary.
        In reality: Checks password hash, MFA token, or OIDC claim.
        """
        # Look up the user in the dictionary
        role = config.USERS.get(username)
        
        # If found...
        if role:
            # Login successful
            audit_log.info(f"[AUTH] User '{username}' authenticated as '{role}'.")
            return role
        else:
            # Login failed
            audit_log.warning(f"[AUTH] Failed authentication attempt for '{username}'.")
            return None

    def authorize(self, username, action):
        """
        Validates Permission.
        
        QUESTION: "Can 'username' do 'action'?"
        """
        # Step 1: Who are you? (Role Lookup)
        role_name = self.authenticate(username)
        
        # If user doesn't exist, they can't do anything
        if not role_name:
            return False
            
        # Special Case: The Unauthenticated User ("none")
        # Represents an attacker like "Eve"
        if role_name == "none":
            audit_log.warning(f"[ACCESS] DENIED: User '{username}' has no privileges.")
            return False
            
        # Step 2: What can your role do? (Permission Lookup)
        # Get the role definition from config
        role_def = config.ROLES.get(role_name)
        # Extract the list of permissions
        permissions = role_def.get("permissions", [])
        
        # Step 3: Match Action to Permissions
        # If the requested action is in the list...
        if action in permissions:
            audit_log.info(f"[ACCESS] GRANTED: {username} -> {action}")
            return True
        else:
            # If not...
            audit_log.warning(f"[ACCESS] DENIED: {username} -> {action}. Missing permission.")
            return False
