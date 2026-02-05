# 🌍 Secure & Resilient Earth Observation (EO) Data Pipeline  
### Security-by-Design Ground Segment Prototype

> *Earth Observation data is a strategic asset. Its protection is not optional — it is a mission requirement.*

---

## 1. Mission Context

Earth Observation (EO) missions rely on complex end-to-end data pipelines spanning the **Space Segment**, **Ground Segment**, and **User Segment**.  
Within this lifecycle, the Ground Segment plays a critical role in ensuring that satellite data remains **confidential, authentic, available, and trustworthy** from downlink to long-term archival and user delivery.

This repository contains a **high-fidelity educational prototype** that simulates a **secure and resilient EO Ground Segment data pipeline**, designed according to **security-by-design** and **defence-in-depth** principles commonly adopted in institutional space systems.

The prototype focuses exclusively on the **Ground Segment**, treating the Space Segment as an external and untrusted data source.

---

## 2. Project Objectives

### Primary Objectives
- Design an end-to-end EO data pipeline (ingestion → processing → archiving → access).
- Apply **Zero Trust principles adapted to EO Ground Segment constraints**.
- Demonstrate core information security properties:
  - **Confidentiality**
  - **Integrity**
  - **Availability**
- Implement resilience mechanisms for corruption detection and recovery.

### Secondary Objectives
- Illustrate cybersecurity risk management concepts in EO systems.
- Provide a reusable conceptual framework for secure EO data exploitation.
- Bridge system architecture, cybersecurity governance, and implementation logic.

---

## 3. What This Project Is (and Is Not)

### This project **is**:
- A **concept validation prototype** for secure EO data handling.
- A simulation of Ground Segment security logic and data lifecycle control.
- A demonstrator of governance-aware cybersecurity design.

### This project **is not**:
- A production-grade Ground Segment implementation.
- A replacement for operational IAM, KMS, or HSM infrastructures.
- A performance benchmark for large-scale EO processing.
- A physically accurate EO processing chain.

---

## 4. High-Level Architecture

The system is structured around **segmented trust zones**, enforcing strict security boundaries between pipeline stages.

[ Space Segment (Untrusted) ]
↓
[ Landing Zone ]
↓
[ Processing Staging ]
↓
[ Secure Archive ]
↓
[ Backup / Resilience ]
↓
[ Access Gateway ]

Data is never allowed to cross a trust boundary without validation and security checks.

---

## 5. Trust Zones Description

### 5.1 Landing Zone (Ingestion)
- **Role**: Reception of raw EO data products.
- **Trust Level**: LOW (untrusted input).
- **Controls**:
  - Metadata validation
  - Initial SHA-256 hashing
- **Security Purpose**: Establish the initial **chain of custody**.

---

### 5.2 Processing Staging
- **Role**: Scientific processing and quality control.
- **Trust Level**: MEDIUM.
- **Controls**:
  - Integrity re-validation before processing
  - Quality control (e.g. NaN detection)
- **Security Purpose**: Prevent propagation of corrupted or tampered data.

---

### 5.3 Secure Archive (Vault)
- **Role**: Long-term storage of finalized EO products.
- **Trust Level**: HIGH.
- **Controls**:
  - Encryption-at-rest
  - Secure deletion of cleartext
- **Security Purpose**: Guarantee confidentiality and integrity of stored assets.

---

### 5.4 Backup & Resilience Layer
- **Role**: Redundant copy of encrypted products.
- **Function**: Enables recovery and self-healing.
- **Security Purpose**: Ensure availability and operational resilience.

---

### 5.5 Access Gateway
- **Role**: Controlled delivery of EO products.
- **Controls**:
  - Authentication
  - Role-Based Access Control (RBAC)
- **Security Purpose**: Enforce least privilege and accountability.

---

## 6. Security Model

### 6.1 Confidentiality
- Encryption-at-rest using symmetric cryptography.
- Decryption allowed only to authorized roles.

### 6.2 Integrity
- SHA-256 cryptographic hashing at each lifecycle stage.
- Integrity verification before and after processing.
- Detection of corruption or tampering.

### 6.3 Availability & Resilience
- Redundant encrypted backups.
- Automated integrity audits.
- Recovery from trusted backup upon corruption detection.

### 6.4 Traceability & Auditability
- Centralized security logging.
- Full audit trail of:
  - ingestion
  - processing
  - archiving
  - access
  - recovery actions

---

## 7. Cryptography Design

### Encryption-at-Rest
- **Scheme**: Fernet (AES-128-CBC + HMAC-SHA256)
- **Purpose**: Confidentiality and authenticated encryption.
- **Design Note**:  
  Fernet is chosen for safety and simplicity in an educational context.  
  In operational systems, encryption keys would be managed via a **Key Management Service (KMS)** or **Hardware Security Module (HSM)**.

### Integrity
- **Algorithm**: SHA-256
- **Usage**:
  - Baseline fingerprint during ingestion
  - Recomputed after processing
- **Purpose**: Preserve chain of custody across trust zones.

---

## 8. Identity & Access Management

The system implements a simplified **Role-Based Access Control (RBAC)** model.

| Role   | Capabilities |
|------|--------------|
| Admin | Security management, recovery operations |
| Analyst | Processing and archiving |
| User | Read-only access to final products |
| None | Explicitly blocked identity (breach simulation) |

All operations require **authentication followed by authorization**.

---

## 9. Risk Management Perspective

The security logic is **conceptually aligned** with:
- ISO/IEC 27001 – Information Security Management Systems
- ISO/IEC 27005 – Information Security Risk Management
- EBIOS Risk Manager methodology
- ESA security and ground segment protection principles (conceptual reference)

Threat categories considered:
- Data tampering
- Unauthorized access
- Accidental corruption
- Operational misconfiguration

---

## 10. Repository Structure

EO_DATASECURITY
├── secure_eo_pipeline/
    ├── components/        # Ingestion, processing, storage, access control
    ├── resilience/        # Backup and recovery logic
    ├── utils/             # Cryptography and logging utilities
    ├── config.py          # Roles, permissions, paths
├── main.py                # Interactive CLI
├── secret.key             # Symmetric encryption key (simulation only)

---

## 11. Quick Start

### Requirements
- Python 3.8+

### Install
```bash pip install -r requirements.txt```

### Interactive Console
```python main.py```

---

## 12. Demo Scenarios

1.	**Happy Path**: Secure ingestion → processing → archiving → delivery.
2.	**Unauthorized Access Attempt**: RBAC blocks unprivileged access.
3.	**Resilience & Self-Healing**: Simulated corruption detected and recovered from backup.

---

## 13. Failure Philosophy

The system follows a Fail-Secure approach:
- On integrity mismatch or missing keys, execution halts.
- No unsafe fallback or silent recovery is attempted.
- Recovery is performed only from trusted backups.

---

## 14. Operational Limitations

- Local filesystem used instead of object storage.
- Encryption key stored locally for demonstration.
- No network transport security simulated.
- Not suitable for operational deployment.

---

## 15. Author & Classification

**Author**: Emanuele Anzellotti
**Type**: Educational / Concept Validation Prototype
**Classification**: PUBLIC
**Target Domain**: EO Ground Segment Security