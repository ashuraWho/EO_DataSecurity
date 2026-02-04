# Import logging library
import logging
# Import sys to handle standard output streams
import sys

# =============================================================================
# Logging & Audit Module
# =============================================================================
# PURPOSE:
# In high-security environments (ESA, Defense, Banking), "knowing what happened"
# is as important as preventing things from happening.
#
# This module provides a standardized "Audit Trail".
#
# SECURITY GOALS:
# 1. Non-repudiation: Users cannot deny their actions if logged.
# 2. Forensics: If a hack occurs, we analyze these logs to find the cause.
# =============================================================================

def setup_logger(name="EO_Pipeline"):
    """
    Configures the system-wide logger.
    
    DESIGN CHOICE:
    We stream logs to STDOUT (Console) for this demo.
    In a real system, we would stream to a WORM (Write Once Check Many) drive
    or a SIEM (Security Information and Event Management) system like Splunk.
    """
    # Get logger instance
    logger = logging.getLogger(name)
    # Set level to INFO (ignore DEBUG noise)
    logger.setLevel(logging.INFO)
    
    # Create the output handler (Where the logs go)
    # We send to console (sys.stdout)
    handler = logging.StreamHandler(sys.stdout)
    
    # Define the Log Format.
    # Structure: [TIMESTAMP] - [COMPONENT] - [SEVERITY] - [MESSAGE]
    # This structure allows automated parsing tools to read the logs later.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Apply format to handler
    handler.setFormatter(formatter)
    
    # Prevent adding duplicate handlers if this function is called multiple times.
    # Otherwise we'd see double or triple lines in the terminal.
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

# Global instance. 
# Other modules can just `from logger import audit_log` and start logging immediately.
audit_log = setup_logger()
