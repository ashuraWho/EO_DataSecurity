import os
import re
from typing import List, Dict, Optional
from secure_eo_pipeline import config

class IntrusionDetectionSystem:
    """
    Analyzes system logs to detect suspicious patterns and potential security breaches.
    Acts as a "Log Hunter" or SIEM (Security Information and Event Management) lite.
    """

    def __init__(self, log_path: str = "audit.log"):
        self.log_path = log_path

    def analyze_audit_log(self) -> List[Dict[str, str]]:
        """
        Scans the audit log for predefined threat signatures.
        
        RETURNS:
            List[Dict]: A list of detected incidents, each with 'severity', 'type', and 'details'.
        """
        if not os.path.exists(self.log_path):
            return [{"severity": "LOW", "type": "System Check", "details": "Audit log not found. System may be fresh."}]

        incidents = []
        
        # Threat Counters
        failed_logins = 0
        consecutive_failures = 0
        
        try:
            with open(self.log_path, "r") as f:
                lines = f.readlines()
        except Exception as e:
            return [{"severity": "CRITICAL", "type": "IDS Failure", "details": f"Could not read audit log: {e}"}]

        # --- SIGNATURE ANALYSIS ---
        for line in lines:
            line = line.strip()
            
            # Signature 1: Known Malicious Actor
            if "hacker" in line:
                incidents.append({
                    "severity": "HIGH",
                    "type": "Insider Threat",
                    "details": f"Activity detected from banned user 'hacker': {line}"
                })

            # Signature 2: Brute Force Detection (Simple Pattern)
            if "Access Denied" in line or "FAILURE" in line:
                consecutive_failures += 1
            else:
                # Reset counter on success or neutral log (simplification)
                # In a real system, we'd track per-IP or per-User.
                if "SUCCESS" in line:
                    consecutive_failures = 0

            if consecutive_failures >= 3:
                incidents.append({
                    "severity": "CRITICAL", 
                    "type": "Brute Force Attack",
                    "details": "Multiple consecutive authentication failures detected."
                })
                consecutive_failures = 0 # Reset to avoid spamming the same incident

            # Signature 3: Data Tampering
            if "Attack successful" in line:
                 incidents.append({
                    "severity": "CRITICAL",
                    "type": "Data Integirty Breach",
                    "details": "CONFIRMED: Primary archive data corruption event."
                })

            # Signature 4: Unauthorized Resource Access
            if "Unauthorized" in line and "lacks" in line:
                 incidents.append({
                    "severity": "MEDIUM",
                    "type": "Privilege Escalation Attempt",
                    "details": f"User attempted action without permission: {line}"
                })

        return incidents
