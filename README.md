# Secure & Resilient Earth Observation Data Pipeline

**OFFICIAL PROJECT MANUAL**

| **Project Metadata** | |
| :--- | :--- |
| **Project Name** | Secure EO Data Pipeline Prototype |
| **Domain** | Space Systems / Ground Segment Engineering |
| **Focus Area** | Cyber Security, Data Integrity, Operational Resilience |
| **Target Audience** | ESA Trainees, Systems Engineers, Security Auditors |
| **Implementation Language** | Python 3.x |
| **Key Standards** | ISO 27000 Series (Information Security), CCSDS (Space Data Systems) |

---

## **1. Executive Summary**

This project serves as a **functional prototype** and **architectural reference** for a secure Earth Observation (EO) data handling system. In the context of modern ESA missions (like Copernicus Sentinel), data is not just "scientific output"; it is a critical asset that requires protection against:
1.  **Unauthorized Access** (Confidentiality Breaches).
2.  **Data Corruption/Tampering** (Integrity Violations).
3.  **System Failures/Data Loss** (Availability Threats).

This prototype simulates the entire lifecycle of a satellite product—from the moment it is received on the ground to its long-term archiving and retrieval—demonstrating how **Security-by-Design** principles are implemented in code.

---

## **2. Detailed System Architecture**

The system is architected as a modular pipeline, where each stage represents a distinct "Zone of Trust".

### **2.1. The Pipeline Components**

| Component | Responsibility | Security Control Implemented |
| :--- | :--- | :--- |
| **1. Data Source** | Simulates the satellite instrument (e.g., MSI on Sentinel-2). | *N/A (Source of inputs)* |
| **2. Ingestion** | The "Border Control". Receives external data. | **Schema Validation** (Is it valid JSON?) & **Baselining** (Calculate initial SHA-256 Hash). |
| **3. Processing** | Transforms raw L0 data to L1 science products. | **Provenance Tracking** (Updates metadata to link input -> output) & **QC** (Checks for corruption). |
| **4. Archiving** | The "Vault". Stores data for the long term. | **Encryption-at-Rest** (AES-256) ensures files are unreadable if the disk is stolen. |
| **5. Resilience** | The "Safety Net". Backups and Recovery. | **Redundancy** (Copy to separate location) & **Self-Healing** (Auto-restore on corruption). |
| **6. Access Control** | The "Gatekeeper". Manages user rights. | **RBAC** (Role-Based Access Control) to enforce Least Privilege. |

### **2.2. Data Flow Diagram**

```
[ SPACE SEGMENT ]              [ GROUND SEGMENT ]
       |
       v
(1) Raw Signal  ----->  [ INGESTION ZONE ] 
                        (Validate Format, Calc Hash)
                                |
                                v
                        [ PROCESSING ZONE ]
                        (Calibrate, QC Check)
                                |
                                v
                        [ SECURE ARCHIVE ]
                        (Encrypt with AES-256)  <====> [ BACKUP VAULT ]
                                |
                                v
                        [ ACCESS GATEWAY ]
                        (Authenticate & Decrypt)
                                |
                                v
                         [ END USER ]
```

---

## **3. Security Mechanisms Explained**

This section explains the *theory* behind the implementation choices.

### **3.1. Cryptography (Confidentiality)**
*   **Algorithm Used**: AES (Advanced Encryption Standard) in CBC mode (via Ferrnet).
*   **Why AES?**: It is the industry standard for symmetric encryption. It is fast enough to encrypt gigabytes of EO data without slowing down the pipeline.
*   **Key Management**: The system generates a `secret.key`. In this prototype, it is a file. In operations, this would be inside a Hardware Security Module (HSM).
*   **Implementation**: See `utils/security.py`.

### **3.2. Hashing (Integrity)**
*   **Algorithm Used**: SHA-256 (Secure Hash Algorithm 256-bit).
*   **Why?**: A hash acts as a "Digital Fingerprint". If even a single bit of a 10GB satellite image changes (due to cosmic radiation or a hacker), the SHA-256 hash changes completely.
*   **Workflow**:
    1.  Calculate Hash immediately upon arrival (Ingestion).
    2.  Store this Hash in the metadata (JSON).
    3.  Periodically recalculate the file's Hash and compare it to the metadata. Mismatch = Corruption.

### **3.3. Role-Based Access Control (Governance)**
*   **Why?**: Managing permissions for 1000 users individually is impossible. We assign permissions to **Roles** (Admin, Analyst, User).
*   **The Roles**:
    *   **Admin**: Can Manage Keys, Recover Data. (High Trust)
    *   **Analyst**: Can Process Data. (Medium Trust)
    *   **User**: Can only Read. (Low Trust)
*   **Implementation**: See `config.py` definitions and `components/access_control.py` logic.

---

## **4. Operational Manual**

### **4.1. Installation**
Prerequisites: Python 3.8+.
```bash
# 1. Install dependencies
pip install -r requirements.txt
```

### **4.2. Mode 1: Automated Demonstration**
Best for initial validation or presenting to stakeholders.
```bash
python main_demo.py
```
**What happens:**
1.  **Scenario 1 (Happy Path)**: The system generates a file, processes it, encrypts it, and lets an Admin read it. All green checks.
2.  **Scenario 2 (Intrusion)**: A user "Eve" tries to read a file. The system denies access.
3.  **Scenario 3 (Disaster Recovery)**: The script intentionally corrupts a file on disk. The Resilience Manager detects the hash mismatch and restores the file from backup automatically.

### **4.3. Mode 2: Interactive Console**
Best for training operators or exploring the system logic yourself.
```bash
python main_interactive.py
```
**Commands:**
*   `scan`: Triggers the `data_source` to create a new random product.
*   `ingest`: Moves the product from Landing Zone to Processing, validating it.
*   `process`: Runs the L0->L1 mathematics.
*   `archive`: Encrypts the file and moves it to the Secure Archive.
*   `hack`: **(Simulation)** Corrupts the encrypted file on the hard drive.
*   `recover`: Runs the integrity check and restores from backup if needed.
*   `login`: Switch users (e.g., `alice_admin`, `eve_hacker`).

---

## **5. File Structure & Code Guide**

A quick map of the codebase for developers.

*   **`main_demo.py`**: The "movie script" that runs the auto-demo.
*   **`main_interactive.py`**: The "video game" CLI for manual control.
*   **`simulation_data/`**: **(Generated Runtime Folder)**.
    *   This folder appears when you run the scripts. 
    *   It contains the simulated satellite files (`.npy`, `.json`, `.enc`) and backups.
    *   **Safe to Delete**: The scripts will automatically recreate it if missing.
*   **`secure_eo_pipeline/`**: The main package.
    *   **`config.py`**: **READ THIS FIRST**. Contains all directory paths, user accounts, and role definitions.
    *   **`utils/`**:
        *   `security.py`: The crypto engine (Hash/Encrypt/Decrypt).
        *   `logger.py`: The centralized audit logging tool.
    *   **`components/`**:
        *   `data_source.py`: Simulates the satellite.
        *   `ingestion.py`: Handles validation and initial hashing.
        *   `processing.py`: Handles data transformation and QC.
        *   `storage.py`: Handles encryption and file storage.
        *   `access_control.py`: The logic for RBAC (AuthN/AuthZ).
    *   **`resilience/`**:
        *   `backup_system.py`: The logic for backup replication and self-healing.

---

## **6. Conclusion**

This system demonstrates that **Security is not an add-on; it is a process.** 
By integrating validation, encryption, and hashing into the very lifecycle of the data, we ensure that ESA missions can trust the scientific data they produce, even in the face of cyber threats or hardware failures.