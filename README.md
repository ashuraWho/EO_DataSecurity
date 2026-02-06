# Secure and Resilient Earth Observation (EO) Data Pipeline
## Official Technical and Operational Manual

This repository is a high‑fidelity educational prototype of a secure ground‑segment pipeline for Earth Observation (EO) missions. The goal is not only to show **what** the system does, but to explain **why** every control exists and **how** it is implemented in code. The manual therefore includes both operational guidance and the underlying security theory that motivates each design decision.

Two audiences are assumed simultaneously:
1. Newcomers who need explicit definitions and a guided explanation.
2. Engineers and security practitioners who expect precise terminology, rationale, and architectural intent.

If you want a quick start, see "Quick Start". If you want the full conceptual and code‑level explanation, read from the top.

---

## 1. Mission Context and Strategic Objectives
Earth Observation data is not just scientific; it is strategic. It supports environmental monitoring, infrastructure planning, disaster response, and national security. The ground segment is responsible for protecting this data from the instant it is received to the moment it is delivered to an authorized user.

The system is engineered to satisfy the **CIA Triad**:
1. **Confidentiality**: unauthorized actors must not read or infer sensitive data.
2. **Integrity**: any modification, accidental or malicious, must be detectable.
3. **Availability**: data must remain recoverable and serviceable over time.

This repository implements these objectives explicitly and teaches how they map to concrete mechanisms: authenticated encryption, hashing, access control, redundancy, and audit logging.

---

## 2. What This Project Is
This project is:
1. A functional prototype of a secure EO data lifecycle.
2. A teaching system for security design patterns and operational safeguards.
3. A demonstration of how to align code with security goals and threat assumptions.

## 3. What This Project Is Not
This project is not:
1. A production‑grade ground segment.
2. A complete scientific processing chain.
3. A substitute for enterprise IAM (Identity and Access Management), key management, or HSM (Hardware Security Module) solutions.
4. A performance or scalability benchmark.

These exclusions are intentional. The prototype focuses on correctness of security logic and clarity of architecture.

---

## 4. Quick Start
### 4.1. Requirements
1. Python 3.8+.
2. A terminal shell.

### 4.2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.3. Run the Interactive Console
```bash
python main.py
```

### 4.4. Suggested Demo Flow
1. `scan`
2. `login`
3. `ingest`
4. `process`
5. `archive`
6. `hack`
7. `recover`

This sequence walks through acquisition → validation → processing → encryption → corruption → recovery.

---

## 5. Repository Structure
1. `main.py` Interactive operator console (CLI) and orchestration.
2. `secure_eo_pipeline/` Core pipeline package.
3. `secure_eo_pipeline/components/` Data source, ingestion, processing, storage, and RBAC.
4. `secure_eo_pipeline/resilience/` Backup and self‑healing logic.
5. `secure_eo_pipeline/utils/` Cryptography and logging utilities.
6. `secure_eo_pipeline/config.py` Central configuration and policy definitions.
7. `simulation_data/` Runtime artifacts (generated).
8. `secret.key` Symmetric encryption key for the simulation.

---

## 6. Architectural Model (Zones of Trust)
The pipeline is designed around **trust zones**. Each zone is a security boundary with a specific risk profile:

1. **Landing Zone (Ingest)**: untrusted entry point. Data is treated as hostile until verified.
2. **Processing Staging**: trusted internal zone for validation and scientific transformation.
3. **Secure Archive**: encrypted long‑term storage. Data here must be unreadable without a key.
4. **Backup Storage**: redundant encrypted copy, isolated for recovery.
5. **Access Gateway**: controlled retrieval enforcing authentication and authorization.

This mirrors operational ground segments, where physical and logical separation reduces attack surface and limits blast radius.

---

## 7. Security Theory and Design Rationale
This section explains the **theory** behind the controls, not just the controls themselves.

### 7.1. Confidentiality
Confidentiality protects against disclosure. In storage systems, the most common disclosure risks are:
1. Physical loss or theft of a disk.
2. Misconfigured access controls.
3. Insider misuse.

**Strategy:** Use encryption at rest with authenticated encryption to prevent exposure even when storage is compromised.

### 7.2. Integrity
Integrity means data is trustworthy. EO data is often used for critical decisions, so corruption must be detectable.

**Strategy:** Use cryptographic hashes as immutable fingerprints. Any modification, even a single bit flip, changes the hash (the avalanche effect). By storing hashes in metadata, we maintain a chain of custody across transformations.

### 7.3. Availability
Availability ensures data is recoverable in the face of failures or attacks.

**Strategy:** Maintain redundant copies in isolated zones and verify integrity before restoration.

### 7.4. Least Privilege and Role-Based Access Control (RBAC)
Least privilege reduces the potential damage of compromised accounts. RBAC formalizes this by assigning permissions to roles, not to individuals. This is more scalable and reduces policy drift.

### 7.5. Defense in Depth
Security is not a single mechanism but a layered system. If one control fails, another should still prevent catastrophic impact. This pipeline applies that principle by combining RBAC, encryption, hashing, and redundancy.

---

## 8. Cryptographic Model
### 8.1. Encryption
**Library:** `cryptography` (Fernet).

**Fernet properties:**
1. AES‑128 (Advanced Encryption Standard) in CBC (Cipher Block Chaining) mode for confidentiality.
2. HMAC‑SHA256 for integrity and authenticity.
3. Random IV (Initialization Vector) generation for semantic security.

**Why Fernet:** It is safe by default and reduces configuration errors in educational contexts. For production, AES‑GCM (Advanced Encryption Standard - Galois/Counter Mode) or envelope encryption would be preferred, but Fernet is sufficient to demonstrate authenticated encryption principles.

### 8.2. Key Management
1. Key stored in `secret.key`.
2. Generated automatically if missing.
3. File permissions restricted to owner where supported.

### 8.3. Hashing
**Algorithm:** SHA‑256 (Secure Hash Algorithm 256-bit).

**Rationale:** SHA‑256 is a widely accepted standard for integrity verification. Hashes are computed in chunks to allow processing of large data files without excessive memory use.

---

## 9. Data Lifecycle and Control Flow
### 9.1. Generation (Data Source)
The `EOSimulator` produces a synthetic Level‑0 product consisting of:
1. A `.npy` NumPy array (synthetic sensor data).
2. A `.json` metadata file (timestamp, sensor ID, orbit, cloud cover).

**Control intent:** Even simulated data is treated as untrusted to enforce correct pipeline logic.

### 9.2. Ingestion
The `IngestionManager`:
1. Validates metadata schema.
2. Computes SHA‑256 hash of the raw data.
3. Copies data into the trusted staging zone.

**Control intent:** Establishes the first chain‑of‑custody anchor and isolates untrusted inputs.

### 9.3. Processing and Quality Control
The `ProcessingEngine`:
1. Verifies integrity by comparing hashes.
2. Performs QC (rejects NaN values).
3. Normalizes values into 0.0–1.0 reflectance range.
4. Writes a new hash for the processed data.

**Control intent:** Ensures only verified data is processed and provenance is updated after transformation.

### 9.4. Archiving
The `ArchiveManager`:
1. Copies processed data into the archive.
2. Encrypts the archive copy in place.
3. Writes final metadata into the archive.
4. Optionally removes cleartext staging files.

**Control intent:** Protects confidentiality and minimizes exposure of cleartext data.

### 9.5. Backup and Recovery
The `ResilienceManager`:
1. Creates an encrypted backup copy.
2. Verifies integrity during recovery.
3. Restores from backup if mismatch is detected.

**Control intent:** Guarantees availability even if the primary archive is corrupted.

---

## 10. Codebase Walkthrough
This section explains each module and its role in the system. It is a conceptual walkthrough of the entire codebase.

### 10.1. `main.py`
Purpose: interactive CLI (Command Line Interface) that orchestrates all pipeline stages.

Key responsibilities:
1. Maintains session state and user identity.
2. Enforces pipeline order and authorization checks.
3. Provides operator commands (`scan`, `ingest`, `process`, `archive`, `hack`, `recover`).
4. Surfaces status and results in a user‑friendly interface.

Design rationale:
- Centralizing orchestration in a CLI mirrors mission control workflows, where operators progress data through controlled stages.

### 10.2. `secure_eo_pipeline/config.py`
Purpose: centralized configuration and policy definition.

Key responsibilities:
1. Defines filesystem layout for trust zones.
2. Defines RBAC roles and permissions.
3. Defines user‑to‑role mappings.

Design rationale:
- Central configuration prevents hardcoding and allows policy changes without modifying core logic.

### 10.3. `secure_eo_pipeline/components/data_source.py`
Purpose: data generation simulation.

Key responsibilities:
1. Creates synthetic data arrays.
2. Writes metadata with acquisition details.
3. Logs the creation for auditability.

Design rationale:
- Simulated data allows security logic to be tested without real mission datasets.

### 10.4. `secure_eo_pipeline/components/ingestion.py`
Purpose: secure entry point into the pipeline.

Key responsibilities:
1. Validates metadata schema.
2. Computes and stores SHA‑256 hash.
3. Moves data into trusted staging.

Design rationale:
- Establishes chain of custody and prevents malformed data from entering processing.

### 10.5. `secure_eo_pipeline/components/processing.py`
Purpose: data transformation with integrity protection.

Key responsibilities:
1. Verifies ingestion hash.
2. Performs QC (NaN rejection).
3. Normalizes data values.
4. Updates metadata and hash.

Design rationale:
- Prevents processing of tampered data and maintains provenance through transformation.

### 10.6. `secure_eo_pipeline/components/storage.py`
Purpose: secure archiving and retrieval.

Key responsibilities:
1. Encrypts processed products.
2. Writes archive metadata.
3. Optionally removes cleartext staging files.
4. Decrypts only cloned copies for delivery.

Design rationale:
- Protects confidentiality and ensures the archive remains immutable and trustworthy.

### 10.7. `secure_eo_pipeline/components/access_control.py`
Purpose: RBAC enforcement.

Key responsibilities:
1. Authenticate users.
2. Authorize actions based on role permissions.
3. Log security events.

Design rationale:
- Prevents unauthorized operations and supports auditability.

### 10.8. `secure_eo_pipeline/resilience/backup_system.py`
Purpose: redundancy and recovery.

Key responsibilities:
1. Copies encrypted data to backup zone.
2. Verifies integrity against a known good hash.
3. Restores corrupted data from backup.

Design rationale:
- Ensures availability and reduces operational risk.

### 10.9. `secure_eo_pipeline/utils/security.py`
Purpose: cryptographic utilities.

Key responsibilities:
1. Generate and load symmetric keys.
2. Encrypt and decrypt files.
3. Compute SHA‑256 hashes.

Design rationale:
- Centralizing cryptographic primitives reduces code duplication and mistakes.

### 10.10. `secure_eo_pipeline/utils/logger.py`
Purpose: unified audit logging.

Key responsibilities:
1. Configures a shared logger.
2. Enforces consistent format and severity.
3. Provides a system‑wide audit trail.

Design rationale:
- Auditability is a foundational security requirement for mission systems.

---

## 11. Step-by-Step Operational Flow (Mission Control Walkthrough)

This section describes **exactly what happens under the hood** when the operator launches the program (`main.py`) and how to interact with the system as a Mission Control operator.

It is intended to provide full operational transparency and reproducibility.

---

### 11.1. Program Startup and Initial Sanitization

When the operator runs:

```bash
python main.py
```

the system immediately performs a set of automated initialization tasks:

1. **Environment Reset**
	- The system checks for the existence of the `simulation_data/` directory.
	- If found, it is completely deleted.
	- This guarantees a clean, deterministic starting state (tabula rasa) for every execution, with no residual data from previous runs.

2. **Component Initialization**
    All core subsystems are instantiated:
	- EO Data Simulator
	- Secure Ingestion Module
	- Processing Engine
	- Secure Archive Manager
	- Access Control Engine
	- Backup & Resilience Manager

    This mirrors the initialization of services in a real EO Ground Segment.

3. **Operator Interface**
    - The terminal is cleared.
    - The system banner is displayed: ```SECURE EARTH OBSERVATION PIPELINE```
    - The system then enters Mission Control mode.

### 11.2.  Mission Control Console
The operator is presented with an interactive prompt: ```MISSION_CONTROL> _```

At this stage:
- The program is running inside an event loop, waiting for operator commands.
- No processing occurs until an explicit command is issued.
- The system is initially in anonymous mode, with no active identity.

### 11.3. Authentication (login)
Sensitive operations are protected by access control.
1. **Operator Action**: `login`
2. **System Behavior**:
    - The system displays the list of predefined identities (configured in `config.py`):

        | **User** | **Role** | **Description** |
        | :--- | :--- | :--- |
        | **emanuele_admin** | Admin | Full privileges, including disaster recovery |
        | **bob_analyst** | Analyst | Processing and archiving permissions |
        | **charlie_user** | User | Read-only access |
        | **eve_hacker** | None | Explicitly unauthorized identity |

    - The operator selects a username.
	- Authentication and role assignment are enforced.
	- All subsequent actions are authorized based on the assigned role.

### 11.4. EO Data Generation (scan)
This step simulates the arrival of EO data from the Space Segment.
1. **Operator Action**: `scan`
2. **System Behavior**:
    - Simulates a short downlink delay: ```Listening for satellite downlink...```
    - Generates a unique EO product identifier (e.g. Sentinel_2_XXXX).
    - Creates synthetic Level-0 raw data products in the `ingest_landing_zone/`.
    - The product lifecycle state becomes: ```GENERATED```

At this point, data exists but is **untrusted**.

### 11.5. Secure Ingestion (ingest)
The raw product must be validated before further processing.
1. **Operator Action**: `ingest`
2. **System Behavior**:
    - Verifies that the operator has processing privileges.
    - Validates metadata and file structure.
    - Computes a SHA-256 cryptographic hash, establishing the integrity baseline.
    - Registers the hash as part of the product’s chain of custody.
    - Lifecycle state transitions to: ```INGESTED```

### 11.6. Processing (process)
Raw EO data is transformed into a scientific product.
1. **Operator Action**: `process`
2. **System Behavior**:
    - Simulates computation latency (~1.5 seconds).
    - Symbolically converts data from Level-0 → Level-1C.
    - Executes quality control checks (e.g. NaN detection).
    - Moves the product to the processing staging area.
    - Generates a new integrity hash reflecting the modified content.
    - Lifecycle state transitions to: ```PROCESSED```

### 11.7. Secure Archiving (archive)
The finalized product is secured for long-term storage.
1. **Operator Action**: `archive`
2. **System Behavior**:
    - **Encryption**:
        - The product is encrypted using the Fernet scheme.
        - The encrypted file is unreadable without the secret key.
    - **Backup Creation**:
        - An identical encrypted copy is immediately stored in the backup zone.
    - **Vaulting**:
        - The encrypted product is transferred to the secure archive.
    - Lifecycle state transitions to: ```ARCHIVED```

At this point, confidentiality, integrity, and availability guarantees are enforced.

### 11.8. Attack and Defense Simulation (Optional)
The operator can simulate security incidents and recovery actions.

#### 11.8.1. Simulated Attack (hack)
```hack```
- The system intentionally corrupts the encrypted file in the primary archive.
- The product lifecycle state becomes:
```CORRUPTED```

This represents a disk-level or malicious tampering scenario.

#### 11.8.2. Recovery (recover) — Admin Only
```recover```
- The system compares the corrupted file against the trusted backup.
- Integrity mismatch is detected.
- The corrupted archive is automatically replaced with the clean backup copy.
- The product is restored to a secure state.

This demonstrates automated resilience and self-healing behavior.

### 11.9. Utility Commands

- `status` : Displays a summary table showing which lifecycle stages have been completed.
- `help` : Displays the full list of available commands.

### 11.10. Typical Operational Flow
A standard secure EO workflow follows this sequence:

`login` → `scan` → `ingest` → `process` → `archive`

Security testing can then be performed using:

`hack` → `recover`

---

## 12. Operational Threat Model
### 12.1. Threats Addressed
1. Unauthorized access → blocked via RBAC.
2. Data corruption or tampering → detected by hashing.
3. Hardware failure → mitigated with backup and recovery.

### 12.2. Threats Not Addressed
1. Network transport security.
2. Multi‑tenant isolation.
3. Key rotation policies.
4. External SIEM (Security Information and Event Management) integration.

Professional security design explicitly states both covered and uncovered risks.

---

## 13. Runtime Data Layout
All runtime artifacts live under `simulation_data/`:
1. `ingest_landing_zone/` untrusted input.
2. `processing_staging/` trusted processing workspace.
3. `secure_archive/` encrypted vault.
4. `backup_storage/` redundant encrypted copy.

---

## 14. File Formats
1. `.npy` NumPy binary arrays for synthetic sensor data.
2. `.json` metadata for validation and provenance.
3. `.enc` encrypted archive outputs.

---

## 15. CLI Command Reference
1. `help` Show command list.
2. `login` Authenticate a user.
3. `logout` End session.
4. `scan` Generate a synthetic product.
5. `ingest` Validate and fingerprint data.
6. `process` Run QC and calibration.
7. `archive` Encrypt and vault data.
8. `hack` Simulate corruption of archive data.
9. `recover` Verify and restore from backup.
10. `status` Show lifecycle status.
12. `exit` Quit the console.

---

## 16. Operational Notes and Caveats
1. `secret.key` is a sensitive asset. Do not commit real keys in production.
2. Deleting `secret.key` makes archive data unrecoverable.
3. Verbose logging is intentional for traceability and auditability.

---

## 17. Extensibility Guidelines
1. Maintain trust zone separation for new data flows.
2. Extend metadata schema in a backward‑compatible way.
3. Add new permissions only through `config.py`.
4. Add integrity checks after any new transformation.

---

## 18. Troubleshooting
**Q: Where is data stored?**  
A: Under `simulation_data/` in the zone directories.

**Q: I lost `secret.key`. Can I recover?**  
A: No. The encryption is symmetric; the key is mandatory.

**Q: Processing fails with QC errors. Why?**  
A: The data contains NaN values and is rejected to maintain data quality.

---

## 19. Versioning and Status
This repository is an educational prototype. Version numbers reflect feature maturity, not operational readiness.

---

## 20. Attribution
- **Author**: Emanuele Anzellotti 
- **Type**: Educational / Concept Validation Prototype 
- **Target Domain**: EO Ground Segment Security
