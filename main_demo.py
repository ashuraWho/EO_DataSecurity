# Import standard python libraries
import sys
import os
import time
# Import Rich library for UI (Panels, Tables, Progress Bars)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from rich.style import Style

# Project Imports - These are the modules we wrote!
# Import configuration (paths, keys)
from secure_eo_pipeline import config
# Component: Simulates data source
from secure_eo_pipeline.components.data_source import EOSimulator
# Component: Handles Ingestion
from secure_eo_pipeline.components.ingestion import IngestionManager
# Component: Handles Processing
from secure_eo_pipeline.components.processing import ProcessingEngine
# Component: Handles Archive/Encryption
from secure_eo_pipeline.components.storage import ArchiveManager
# Component: Handles Authentication
from secure_eo_pipeline.components.access_control import AccessController
# Component: Handles Backup/Resilience
from secure_eo_pipeline.resilience.backup_system import ResilienceManager
# Utility: Security/Integrity functions
from secure_eo_pipeline.utils import security

# Initialize Rich Console (The UI manager)
console = Console()

# =============================================================================
# Helper Functions for UI (Visualization Logic)
# =============================================================================

def print_header(title, subtitle):
    """
    Draws a big fancy header box at the start of a scenario.
    """
    console.print(Panel.fit(
        f"[bold white]{subtitle}[/bold white]",
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))

def print_step(step_num, description, color="blue"):
    """
    Prints a uniform section header (Step 1, Step 2, etc).
    """
    console.print(f"\n[bold {color}]Step {step_num}:[/bold {color}] {description}")

def print_status(component, status, details, success=True):
    """
    Prints a status table row showing success/failure state.
    This creates the nice 'Component | Status | Details' output.
    """
    # Determine color: Green for good, Red for bad
    color = "green" if success else "red"
    # Choose icon
    symbol = "✅" if success else "❌"
    
    # Create a borderless table
    table = Table(show_header=False, box=None)
    table.add_column("Component", style="bold white", width=15)
    table.add_column("Status", style=color, width=10)
    table.add_column("Details", style="dim white")
    
    # Add the data row
    table.add_row(f"[{component}]", f"{symbol} {status}", details)
    console.print(table)

def print_explanation(text):
    """
    Prints a user-friendly 'Beginner Mode' explanation box.
    Explains the 'Why', not just the 'What'.
    """
    console.print(f"[dim white italic]   ℹ {text}[/dim white italic]\n")

# =============================================================================
# SCENARIO 1: THE HAPPY PATH
# =============================================================================
# GOAL:
# Demonstrate the system working exactly as designed from end-to-end.
# Flow: Source -> Ingest -> Process -> Archive -> Backup -> User Access
# =============================================================================

def run_scenario_1_happy_path():
    # Clear screen for fresh start
    console.clear()
    print_header("SCENARIO 1", "Nominal Operations (Happy Path)\nGoal: Ingest -> Process -> Archive -> Access")
    
    # Initialize all our System Components
    source = EOSimulator()
    ingest = IngestionManager()
    processor = ProcessingEngine()
    archive = ArchiveManager()
    ac = AccessController()
    backup = ResilienceManager()
    
    # Define a unique Product ID for this run
    pid = "Sentinel_2_T32TQC_DEMO"
    
    # --- Step 1: Generation ---
    print_step(1, "Satellite Data Acquisition (Simulation)", "cyan")
    print_explanation("We simulate a satellite (like Sentinel-2) capturing an image of Earth.\n   At this stage, it's just raw digital signals (ones and zeros) being beamed down to Earth.")
    
    # Show loading spinner
    with console.status("[bold cyan]Simulating satellite downlink...", spinner="earth"):
        time.sleep(1.5) # Fake delay
        source.generate_product(pid)
        
    print_status("DATA SOURCE", "GENERATED", f"Product ID: {pid}", success=True)
    
    # --- Step 2: Ingestion ---
    print_step(2, "Secure Ingestion & Validation", "cyan")
    print_explanation("The data lands at our ground station.\n   Think of this as 'Border Control'. We immediately check:\n   1. Is the file format correct?\n   2. Is the passport (metadata) valid?\n   3. We take a 'digital fingerprint' (Hash) to ensure no one changes it later.")
    
    with console.status("[bold cyan]Ingesting product...", spinner="dots"):
        time.sleep(1)
        # Call the actual ingestion logic
        ingested_path = ingest.ingest_product(pid)
    
    if ingested_path:
        print_status("INGESTION", "VALIDATED", "Format OK | Schema OK | Hash Calculated", success=True)
    else:
        print_status("INGESTION", "FAILED", "Validation Failed", success=False)
        return # Stop if failed
    
    # --- Step 3: Processing ---
    print_step(3, "Processing & Quality Control (L0 -> L1)", "cyan")
    print_explanation("Raw data is hard to read. We process it to make it useful (Level-1).\n   Crucially, we check for errors (Quality Control). If the data is garbage (e.g., sensor error), we reject it here so it doesn't pollute the archive.")
    
    with console.status("[bold cyan]Processing L0 -> L1...", spinner="dots"):
        time.sleep(1.5)
        # Call processing logic
        processed_path = processor.process_product(pid)
    
    if processed_path:
         print_status("PROCESSING", "COMPLETED", "Quality Control Passed | Metadata Updated", success=True)
    else:
        print_status("PROCESSING", "QC FAILED", "Data Corruption Detected", success=False)
        return
    
    # --- Step 4: Archiving ---
    print_step(4, "Secure Storage (Encryption at Rest)", "cyan")
    print_explanation("Now we store the valuable processed data.\n   We use AES Encryption (like a digital safe). If a hacker steals the hard drive,\n   all they will see is scrambled noise. Only the key can unlock it.")
    
    with console.status("[bold cyan]Encrypting...", spinner="dots"):
        time.sleep(1)
        # Call archiving logic (Encryption happens here)
        archived_path = archive.archive_product(pid)
        
    print_status("ARCHIVE", "SECURED", "File Encrypted (AES) | Stored", success=True)
    
    # --- Step 5: Backup ---
    print_step(5, "Resilience Layer (Backup)", "cyan")
    print_explanation("Hard drives fail. Buildings catch fire. \n   To be 'Resilient', we immediately make a copy to a separate secure location.\n   This ensures Availability.")
    
    # Create the backup
    backup.create_backup(pid)
    print_status("BACKUP", "REPLICATED", "Copy created in Backup Zone", success=True)
    
    # --- Step 6: Access ---
    print_step(6, "User Access & Delivery", "cyan")
    user = "alice_admin"
    print_explanation(f"User '{user}' wants the file.\n   The system checks her ID card (Authentication) and her permissions (Authorization).\n   Since she is an Admin, we decrypt the file just for her.")
    
    # Check permission
    if ac.authorize(user, "read"):
        print_status("ACCESS CONTROL", "AUTHORIZED", f"Role '{config.USERS[user]}' permitted", success=True)
        # Retrieve and Decrypt
        outfile = "retrieved_product.npy"
        with console.status("[bold green]Decrypting and delivering product...", spinner="dots"):
            time.sleep(1)
            archive.retrieve_product(pid, outfile)
        
        print_status("DELIVERY", "SUCCESS", f"Decrypted to {outfile}", success=True)
        # Cleanup the delivered file to keep folder clean
        if os.path.exists(outfile): os.remove(outfile) 
    else:
        print_status("ACCESS CONTROL", "DENIED", "Insufficient Permissions", success=False)

    console.print(Panel("[bold green]SCENARIO 1 COMPLETED SUCCESSFULLY[/bold green]", border_style="green"))


# =============================================================================
# SCENARIO 2: UNAUTHORIZED ACCESS
# =============================================================================
# GOAL:
# Demonstrate RBAC blocking a hacker.
# =============================================================================

def run_scenario_2_unauthorized_access():
    print("\n\n")
    print_header("SCENARIO 2", "Security Breach Attempt\nGoal: Block unauthorized user accessing Archive")
    
    ac = AccessController()
    hacker = "eve_hacker"
    
    # --- Step 1: Login Try ---
    print_step(1, "Authentication Attempt", "red")
    print_explanation(f"An unknown user '{hacker}' tries to log in.\n   Imagine a stranger trying to enter a secure facility without a badge.")
    
    ac.authenticate(hacker) # This will log a warning
    
    # --- Step 2: Access Try ---
    print_step(2, "Authorization Check", "red")
    print_explanation(f"'{hacker}' tries to grab a sensitive file.\n   The system checks the Access Control List (ACL). She is NOT on the list.\n   The door remains locked.")
    
    # Try to authorize
    authorized = ac.authorize(hacker, "read")
    
    if authorized:
        print_status("SECURITY", "BREACHED", "CRITICAL FAILURE: Unauthorized access granted!", success=False)
    else:
         print_status("ACCESS CONTROL", "BLOCKED", f"User '{hacker}' has NO PERMISSIONS. Access Denied.", success=True)
         
    console.print(Panel("[bold green]SCENARIO 2 COMPLETED: SYSTEM SECURE[/bold green]", border_style="green"))


# =============================================================================
# SCENARIO 3: RESILIENCE (SELF-HEALING)
# =============================================================================
# GOAL:
# Demonstrate detection of corruption (Simulated Hack) and restoration from backup.
# =============================================================================

def run_scenario_3_resilience():
    print("\n\n")
    print_header("SCENARIO 3", "Data Integrity & Recovery\nGoal: Detect bit-rot/corruption and auto-heal")
    
    pid = "Resilience_Test_Product"
    
    # Re-initialize components
    source = EOSimulator()
    ingest = IngestionManager()
    processor = ProcessingEngine()
    archive = ArchiveManager()
    backup = ResilienceManager()
    
    # --- Setup Phase (Fast Forward) ---
    console.print("[dim]Setting up: Creating valid product and backup...[/dim]")
    source.generate_product(pid)
    ingest.ingest_product(pid)
    processor.process_product(pid)
    archived_path = archive.archive_product(pid)
    backup.create_backup(pid)
    
    # Capture the "Good" Hash for verification later
    good_hash = security.calculate_hash(archived_path)
    console.print(f"[green]Original Healthy Hash: {good_hash}[/green]")
    
    # --- Step 1: Attack (Corruption) ---
    print_step(1, "Simulating Cyber/Physical Attack", "red")
    print_explanation("We simulate a disk failure or a cyber-attack.\n   We are intentionally writing garbage data over the good file.\n   This represents 'Bit Rot' or data corruption.")
    
    console.print(Panel("[bold red]ALERT: DATA CORRUPTION INJECTED[/bold red]\nWriting garbage bytes to the primary storage disk...", border_style="red"))
    
    # Manually overwrite the file with junk
    with open(archived_path, "wb") as f:
        f.write(b"CORRUPTED_DATA_BLOCK_000000")
    
    # Verify it is bad
    bad_hash = security.calculate_hash(archived_path)
    console.print(f"[red]Corrupted Hash:        {bad_hash}[/red]")
    
    # --- Step 2: Recovery ---
    print_step(2, "System Integrity Verification", "blue")
    print_explanation("Our automated 'Health Check' process scans the file.\n   It compares the current fingerprint (Hash) with the original one.\n   They don't match! The system realizes the file is broken.")
    
    # Helper to mimic the system knowing what the hash 'should' be
    def get_expected_hash(p):
        return good_hash
    
    # Trigger Auto-Recovery
    with console.status("[bold red]integrity check running...", spinner="weather"):
        time.sleep(1)
        recovered = backup.verify_and_restore(pid, expected_hash_fn=get_expected_hash)
    
    if recovered:
         print_status("RESILIENCE", "RECOVERED", "Corruption detected -> Backup Restored", success=True)
         print_explanation("Result: The system automatically fetched the good copy from the Backup.\n   The user never even knew there was a problem. This is 'Resilience'.")
    
    # Verify the file is good again
    final_hash = security.calculate_hash(archived_path)
    # Check if we back to the start
    if final_hash == good_hash:
         console.print(Panel("[bold green]SCENARIO 3 COMPLETED: SELF-HEALING SUCCESSFUL[/bold green]", border_style="green"))

# Entry point
if __name__ == "__main__":
    # Ensure a clean state (Remove old data)
    if os.path.exists("simulation_data"):
        import shutil
        shutil.rmtree("simulation_data")
        
    # Run Scenarios in order
    run_scenario_1_happy_path()
    time.sleep(2)
    run_scenario_2_unauthorized_access()
    time.sleep(2)
    run_scenario_3_resilience()
