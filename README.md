# Secure and Resilient Earth Observation (EO) Data Pipeline
## Official Technical and Operational Manual

This document is a full technical manual for the Secure EO Pipeline simulation. It is written for two audiences at once:
- Readers who are new to secure data pipelines and need explicit explanations.
- Engineers and security professionals who want precise, technical detail.

If you are looking for a quick start, see the section "Quick Start".
For a line-by-line explanation of every source file, see `docs/LINE_BY_LINE.md`.

## 1. Mission Context and Goals
Earth observation data is a strategic asset. The pipeline in this repository simulates a secure ground segment that protects satellite data from the moment it arrives on Earth until it is archived and delivered to users.

Primary goals:
1. Confidentiality: Prevent unauthorized access to data at rest and during delivery.
2. Integrity: Detect any tampering or corruption of stored data.
3. Availability: Keep data accessible through redundancy and automated recovery.

## 2. What This Project Is (and Is Not)
This project is a high-fidelity educational prototype. It focuses on security logic and data lifecycle integrity, not on producing physically accurate satellite products.

This project is not:
1. A production-grade ground segment implementation.
2. A replacement for operational key management, identity providers, or hardware security modules.
3. A performance benchmark for large-scale processing.

## 3. Quick Start
### 3.1. Requirements
1. Python 3.8 or newer.
2. A POSIX-like shell is recommended, but Windows will also work.

### 3.2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.3. Run the Automated Demo
```bash
python main_demo.py
```

### 3.4. Run the Interactive Console
```bash
python main_interactive.py
```

## 4. System Architecture Overview
The pipeline is organized as a sequence of trust zones. Each zone represents a different security boundary.

Zones of trust:
1. Landing Zone (ingest): Raw data arrives from an untrusted external source.
2. Processing Staging: Data is validated and transformed into higher-level products.
3. Secure Archive: Data is encrypted and stored for long-term retention.
4. Backup Storage: A second encrypted copy is stored to enable recovery.
5. Access Gateway: Authentication and authorization control delivery.

## 5. Directory Structure
This is the expected repository structure. Some folders are generated at runtime.

- `secure_eo_pipeline/` Core pipeline package.
- `secure_eo_pipeline/components/` Ingestion, processing, storage, and access control logic.
- `secure_eo_pipeline/utils/` Cryptography and logging utilities.
- `secure_eo_pipeline/resilience/` Backup and recovery logic.
- `main_demo.py` Automated end-to-end scenario runner.
- `main_interactive.py` Interactive CLI for manual operation.
- `simulation_data/` Runtime-generated data folders and artifacts.
- `secret.key` Symmetric key used for encryption in this simulation.

## 6. Cryptography and Integrity Model
### 6.1. Encryption at Rest
This system uses the Fernet scheme from the `cryptography` library:
- Encryption: AES-128 in CBC mode.
- Authentication: HMAC-SHA256.
- Purpose: Confidentiality and tamper detection during decryption.

Design note:
- Fernet is chosen for simplicity and safety in a teaching context.
- In a production system, encryption keys would be stored in an HSM and rotated by policy.

### 6.2. Integrity (SHA-256 Hashing)
Every product is hashed during ingestion to establish a baseline integrity fingerprint. Processing generates a new hash because the data content changes.

Security properties:
1. Any modification to the data changes the hash.
2. Hashes are stored in metadata to preserve the chain of custody.

## 7. Identity and Access Management
Role-based access control (RBAC) is implemented in `secure_eo_pipeline/config.py`.

Roles:
1. `admin` Full control including key management and recovery.
2. `analyst` Can process and archive data, but cannot manage keys.
3. `user` Read-only access to final products.
4. `none` Explicitly blocked identity used to simulate a failed breach.

Authentication and authorization are enforced by `AccessController`.

## 8. Data Lifecycle (End-to-End)
This is the exact lifecycle implemented by the pipeline:
1. Generation: Simulated raw data and JSON metadata are created in the landing zone.
2. Ingestion: Metadata is validated and the data file is fingerprinted with SHA-256.
3. Processing: Integrity is verified, quality control is performed, and data is calibrated.
4. Archiving: The product is encrypted and stored in the secure archive.
5. Backup: The encrypted file is copied to the backup zone for resilience.
6. Delivery: Authorized users can request a decrypted copy.

## 9. Automated Demo Scenarios
Run `python main_demo.py` to execute all scenarios.

Scenario 1: Happy path
- Demonstrates a complete pipeline run with successful ingestion, processing, archiving, and delivery.

Scenario 2: Unauthorized access attempt
- Demonstrates that an unprivileged user is blocked by RBAC.

Scenario 3: Resilience and self-healing
- Simulates data corruption and demonstrates automatic recovery from backup.

## 10. Interactive Console Manual
Run `python main_interactive.py` and use these commands:

Commands:
1. `help` Show available commands.
2. `login` Authenticate as a known user.
3. `logout` End the current session.
4. `scan` Generate a new simulated product in the landing zone.
5. `ingest` Validate and fingerprint the product.
6. `process` Apply calibration and quality control.
7. `archive` Encrypt and vault the product.
8. `hack` Corrupt the archived product (simulation).
9. `recover` Validate and restore from backup (admin only).
10. `status` Show the current pipeline state.
11. `exit` Quit the console.

Suggested training flow:
1. `scan`
2. `login` as `emanuele_admin`
3. `ingest`
4. `process`
5. `archive`
6. `hack`
7. `recover`

## 11. Configuration Guide
Key configuration values live in `secure_eo_pipeline/config.py`.

You can change:
1. Directory names for each trust zone.
2. The list of users and their roles.
3. Role permissions.
4. The encryption key file path.

## 12. Logging and Audit Trail
All components log to a shared audit logger. This provides:
1. Accountability for user actions.
2. A timeline for incident response.
3. Evidence for non-repudiation.

Log format:
- Timestamp, component name, log level, and message.

## 13. Operational Notes and Limitations
1. This is a simulation. It uses local files instead of cloud object storage.
2. The encryption key is stored as a local file in this repository for demonstration.
3. The landing zone is treated as untrusted input, but this is not a full secure ingestion boundary.
4. The pipeline does not include network transport security; it focuses on at-rest protection and integrity.

## 14. Security Caveats (Important)
1. Do not commit real keys to version control. The `secret.key` file exists only for simulation.
2. In a real system, you would use a KMS or HSM for key storage and rotation.
3. Role assignments should be handled by an external identity provider.
4. Audit logs should be shipped to immutable storage or a SIEM.

## 15. Troubleshooting
Q: Where is my data saved?
A: All runtime artifacts are in `simulation_data/`.

Q: I deleted `secret.key`. What happens?
A: Encrypted files become unrecoverable, which is expected for strong symmetric encryption.

Q: Why are there many log lines?
A: The system logs every security-relevant event to create a complete audit trail.

## 16. Versioning
This project is a functional prototype. Version numbers indicate feature maturity, not operational readiness.

## 17. License and Attribution
Author: Emanuele Anzellotti / Jules AI
Version: 1.0.0
Target: ESA Ground Segment Security Prototype
