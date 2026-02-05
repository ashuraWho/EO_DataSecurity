# Secure and Resilient Earth Observation (EO) Data Pipeline
## Official Technical and Operational Manual

This repository is a high‑fidelity educational prototype of a secure ground‑segment data pipeline for Earth Observation missions. It demonstrates how raw satellite products can be ingested, validated, processed, archived, and recovered under a security‑first model.

The manual is written for two audiences at the same time:
1. Beginners who need explicit explanations and context.
2. Engineers and security practitioners who want precise technical detail, design rationale, and operational guidance.

If you want a quick start, go to "Quick Start". If you want a full system explanation, read from the top.

## 1. Mission Context and Goals
Earth Observation data is a strategic asset. Ground segments must ensure that data is:
1. Confidential: only authorized users can access it.
2. Intact: any tampering or corruption is detected.
3. Available: failures are recoverable without losing the dataset.

This project implements those goals using a simulation that mirrors real ground‑segment architectures.

## 2. What This Project Is
This project is:
1. A functional prototype of a secure EO data lifecycle.
2. A teaching tool for security concepts: integrity, encryption, RBAC, resilience.
3. A demonstrator for pipeline orchestration and audit logging.

## 3. What This Project Is Not
This project is not:
1. A production system.
2. A full satellite processing chain.
3. A replacement for enterprise IAM or KMS/HSM solutions.
4. A benchmark for performance at scale.

## 4. Quick Start
### 4.1. Requirements
1. Python 3.8+.
2. A terminal with standard shell tools.

### 4.2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.3. Run the Interactive Console
```bash
python main.py
```

### 4.4. Typical Demo Flow
1. `scan`
2. `login` as `emanuele_admin`
3. `ingest`
4. `process`
5. `archive`
6. `hack`
7. `recover`

## 5. Repository Structure
- `main.py` Interactive operator console (CLI).
- `secure_eo_pipeline/` Core pipeline package.
- `secure_eo_pipeline/components/` Data source, ingestion, processing, storage, and RBAC.
- `secure_eo_pipeline/resilience/` Backup and self‑healing logic.
- `secure_eo_pipeline/utils/` Cryptography and logging utilities.
- `secure_eo_pipeline/config.py` Central configuration and policy definitions.
- `simulation_data/` Runtime artifacts (generated).
- `secret.key` Symmetric encryption key used by the simulation.

## 6. System Architecture Overview
The pipeline is designed as a sequence of trust zones. Each zone reflects a security boundary with increasing trust:
1. Landing Zone (Ingest): Untrusted external data enters here.
2. Processing Staging: Trusted internal zone for validation and transformation.
3. Secure Archive: Encrypted long‑term storage.
4. Backup Storage: Redundant encrypted copy for disaster recovery.
5. Access Gateway: RBAC enforcement and controlled retrieval.

This architecture mirrors real‑world ground segment deployments where each zone is physically or logically separated.

## 7. Security Objectives and Rationale
### 7.1. Confidentiality
Goal: Prevent unauthorized access to mission data at rest.

Implementation:
1. Archive files are encrypted using Fernet (AES‑128‑CBC + HMAC‑SHA256).
2. The master archive is never decrypted in place; retrieval uses a cloned copy.

Rationale:
1. If disks are stolen, data remains unreadable without the key.
2. Fernet provides authenticated encryption, detecting tampering during decryption.

### 7.2. Integrity
Goal: Detect any modification or corruption of data.

Implementation:
1. SHA‑256 hashes are computed at ingestion and stored in metadata.
2. Processing verifies the ingestion hash before transforming data.
3. Processing creates a new hash after transformation.
4. Resilience checks compare current hashes to a known good reference.

Rationale:
1. Hashes provide a chain of custody.
2. Any single‑bit change results in a different hash.

### 7.3. Availability
Goal: Recover from corruption, accidental deletion, or hardware failure.

Implementation:
1. Encrypted products are copied to a backup vault.
2. Recovery logic verifies integrity and restores from backup on mismatch.

Rationale:
1. Redundancy reduces single‑point‑of‑failure risk.
2. Automated restoration reduces downtime.

## 8. Pipeline Data Lifecycle
### 8.1. Generation (Data Source)
- `EOSimulator` creates a synthetic Level‑0 data product.
- Two files are generated:
1. `.npy` binary data (NumPy array).
2. `.json` metadata describing the acquisition.

### 8.2. Ingestion
- `IngestionManager` validates required metadata fields.
- Computes SHA‑256 hash of the binary data.
- Copies files to the trusted processing staging zone.

### 8.3. Processing and Quality Control
- `ProcessingEngine` verifies the original hash.
- Rejects data if NaN values are found.
- Applies calibration to normalize values into [0.0, 1.0].
- Computes and stores a new processed hash.

### 8.4. Archiving
- `ArchiveManager` copies the product to the secure archive.
- Encrypts the archived copy in place.
- Writes a final metadata record into the archive.
- Optionally deletes cleartext staging data.

### 8.5. Backup
- `ResilienceManager` creates a redundant encrypted copy.

### 8.6. Retrieval
- Authorized users can request decrypted output.
- Decryption occurs only on a cloned copy, preserving archive integrity.

## 9. Cryptographic Model
### 9.1. Encryption
Library: `cryptography` Fernet.

Fernet provides:
1. AES‑128 in CBC mode for encryption.
2. HMAC‑SHA256 for authentication.
3. Automatic IV generation and integrity checks.

Key Management:
1. The symmetric key is stored in `secret.key`.
2. The key is generated if missing.
3. File permissions are restricted to owner where supported.

### 9.2. Hashing
Algorithm: SHA‑256 from Python’s `hashlib`.

Properties:
1. One‑way function.
2. Strong collision resistance for integrity use.
3. Efficient for large files using chunked reads.

## 10. Identity and Access Control (RBAC)
### 10.1. Roles and Permissions
Roles are defined in `secure_eo_pipeline/config.py`.

Default roles:
1. `admin`: Full permissions, including `manage_keys` and `process`.
2. `analyst`: Data processing and write access.
3. `user`: Read‑only access.
4. `none`: Explicitly blocked identity.

### 10.2. Authentication
`AccessController.authenticate` validates users against the configured map. Users with role `none` are rejected.

### 10.3. Authorization
`AccessController.authorize` checks whether a role contains the requested action.

Rationale:
1. RBAC centralizes policy.
2. Changes propagate immediately by modifying role definitions.

## 11. Logging and Audit Trail
All components share a centralized audit logger.

Log features:
1. Timestamped events for traceability.
2. Component names for attribution.
3. Severity levels (INFO, WARNING, ERROR).

Purpose:
1. Accountability.
2. Incident response reconstruction.
3. Non‑repudiation.

## 12. Directory Layout at Runtime
All runtime artifacts are created in `simulation_data/`.

Subfolders:
1. `ingest_landing_zone/` Incoming untrusted data.
2. `processing_staging/` Trusted processing area.
3. `secure_archive/` Encrypted vault.
4. `backup_storage/` Redundant encrypted copy.

These directories are created automatically when needed.

## 13. File Formats
1. `.npy` NumPy binary array for synthetic data.
2. `.json` metadata records used for validation, integrity, and provenance.
3. `.enc` Encrypted binary output stored in the archive and backup zones.

## 14. CLI Command Reference
All commands are available inside `main.py`.

Commands:
1. `help` Show command list.
2. `login` Authenticate a user.
3. `logout` End current session.
4. `scan` Generate a new synthetic product.
5. `ingest` Validate and fingerprint the product.
6. `process` Run QC and calibration.
7. `archive` Encrypt and vault the product.
8. `hack` Simulate archive corruption.
9. `recover` Verify and restore from backup.
10. `status` Show lifecycle status.
11. `exit` Quit the console.

## 15. Threat Model and Assumptions
This simulation assumes:
1. The landing zone is untrusted.
2. The processing and archive zones are trusted internal environments.
3. Attackers may corrupt storage or attempt unauthorized access.

Threats addressed:
1. Unauthorized access via RBAC.
2. Data corruption via hash verification.
3. Hardware failure via backup restoration.

Threats not addressed:
1. Network transport security.
2. Multi‑tenant isolation.
3. Real‑world key rotation policies.
4. Hardware security modules.

## 16. Operational Notes
1. `secret.key` is a sensitive file and should never be committed in real deployments.
2. Deleting `secret.key` makes encrypted files unrecoverable.
3. The system intentionally logs many events for traceability.

## 17. Extensibility Guidelines
If you extend this project:
1. Keep new data flows within defined trust zones.
2. Update metadata schema if you add new fields.
3. Extend RBAC roles only through `config.py`.
4. Add additional integrity checkpoints for new transformations.

## 18. Troubleshooting
Q: Where is the generated data stored?
A: In `simulation_data/`.

Q: I lost `secret.key`. Can I recover the data?
A: No. The encryption is symmetric and the key is required.

Q: Why does processing fail with a QC error?
A: The simulator may inject NaN values if a corrupted product is generated.

## 19. Versioning and Status
This repository is an educational prototype. Versioning indicates feature completeness, not production readiness.

## 20. License and Attribution
Author: Emanuele Anzellotti
Type: Educational / Concept Validation Prototype
Target Domain: EO Ground Segment Security
