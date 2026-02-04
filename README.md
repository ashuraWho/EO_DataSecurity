# Secure & Resilient Earth Observation (EO) Data Pipeline
## **OFFICIAL TECHNICAL & OPERATIONAL MANUAL**

---

## **1. Introduction & Mission Context**

### **1.1. Project Overview**
The **Secure EO Pipeline** is a high-fidelity functional prototype designed to simulate the ground segment of a modern satellite mission (e.g., ESA's Copernicus Sentinel series). In these missions, data is more than just scientific information—it is a critical geopolitical and environmental asset. This system demonstrates how to protect that asset from its arrival on Earth until its final delivery to scientists.

### **1.2. The Three Pillars of Data Security**
This project is built around the "CIA Triad," the foundational model for information security:
1.  **Confidentiality**: Ensuring only authorized personnel can view the satellite images (Implemented via **AES-256 Encryption**).
2.  **Integrity**: Ensuring the data hasn't been modified by hackers or hardware errors (Implemented via **SHA-256 Hashing**).
3.  **Availability**: Ensuring the data is always accessible, even after a disaster (Implemented via **Automated Redundancy & Self-Healing**).

---

## **2. System Architecture**

The pipeline is organized into distinct "Zones of Trust," mirroring the architecture of professional ground segments.

### **2.1. Logic Flow (The Lifecycle)**
1.  **Landing Zone (Ingest)**: Unfiltered data arrives. It is considered "Untrusted."
2.  **Secure Processing Zone**: Data is verified and transformed into Level-1 products.
3.  **Encrypted Vault (Archive)**: Products are scrambled with a secret key and stored long-term.
4.  **Resilience Layer (Backup)**: A mirrored copy is kept to repair potential corruption.
5.  **Access Gateway**: Authentication and Role-Based Access Control (RBAC) manage user retrieval.

### **2.2. Directory Structure**
- `secure_eo_pipeline/`: The core engine.
  - `components/`: Business logic for Ingestion, Processing, and Storage.
  - `utils/`: Low-level cryptographic and logging tools.
  - `resilience/`: Self-healing and backup logic.
- `main_demo.py`: Automated end-to-end demonstration.
- `main_interactive.py`: Full-featured CLI for manual operations.
- `simulation_data/`: (Generated at runtime) Local database containing all files.

---

## **3. Technical Deep-Dive: Security Mechanisms**

### **3.1. Cryptography (AES-256)**
We utilize **Fernet (Symmetric Encryption)**, which is built on top of AES in CBC mode with 128-bit blocks.
- **Why?**: AES is the global standard used by governments. It provides high performance and unbeatable security.
- **Key Management**: The system generates a `secret.key`. In a real mission, this key would reside in an HSM (Hardware Security Module), physically inaccessible to software.

### **3.2. Data Integrity (SHA-256)**
Every file is "fingerprinted" using the Secure Hash Algorithm 256.
- **The Avalanche Effect**: If even 1 bit of a 100MB file changes, the entire hash string changes completely.
- **Chain of Custody**: We calculate the hash at Ingestion and Processing, storing them in the metadata to ensure the file remains authentic throughout its life.

### **3.3. Role-Based Access Control (RBAC)**
Instead of individual permissions, we use a role hierarchy:
- **Admin**: Has 'God-Mode' rights. Can manage encryption keys and trigger recovery.
- **Analyst**: Can process data and perform Quality Control.
- **User**: Read-only access to final products.
- **Intruder**: No credentials (simulation of a failed breach).

---

## **4. Operational Guide**

### **4.1. Installation**
1.  Ensure Python 3.8+ is installed.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### **4.2. Running the Automated Demo**
This is the best way to see the system in action without typing commands.
```bash
python main_demo.py
```
**Watch for these Scenarios:**
- **The Happy Path**: Success from satellite to user.
- **The Security Breach**: Watch the RBAC system block `eve_hacker`.
- **The Self-Healing**: Watch the system detect a corrupted file and restore it from backup.

### **4.3. Using the Interactive Console**
For manual control and training, use the interactive CLI.
```bash
python main_interactive.py
```
**Workflow to test the system:**
1.  `scan`: Find a signal.
2.  `login`: Login as `emanuele_admin`.
3.  `ingest`: Secure the data.
4.  `process`: Create the L1 product.
5.  `archive`: Encrypt and vault the product.
6.  `hack`: Intentionally corrupt the data on the disk!
7.  `recover`: Watch the system heal the corruption using the backup.

---

## **5. Troubleshooting & FAQ**

**Q: Where is my data saved?**
A: Everything is inside the `simulation_data/` folder. You can safely delete this folder to reset the entire simulation.

**Q: What happens if I lose the `secret.key`?**
A: In this system, and in real life, the data is lost forever. AES encryption is "mathematically perfect" and cannot be bypassed without the key.

**Q: Why do I see so many log lines?**
A: Every action is recorded in the **Audit Log**. This is a legal requirement for satellite missions to provide "Non-Repudiation" (proving who did what).

---

## **6. Advanced Configuration**
You can modify the system behavior in `secure_eo_pipeline/config.py`:
- Change user roles.
- Add new permissions.
- Change the directory names.

---
**Author**: Emanuele Anzellotti / Jules AI
**Version**: 1.0.0
**Target**: ESA Ground Segment Security Prototype
