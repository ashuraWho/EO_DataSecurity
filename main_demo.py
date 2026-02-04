# Import standard python libraries for system-level operations and timing
import sys
# os is used for checking file existence and managing paths
import os
# time is used to insert realistic delays into the demonstration flow
import time
# Import components from the Rich library to create a beautiful and professional terminal UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from rich.style import Style

# PROJECT IMPORTS - Bringing in the secure pipeline architecture we built
# Import configuration (directories, roles, user database)
from secure_eo_pipeline import config
# Component: EOSimulator (Simulates the satellite's instrument output)
from secure_eo_pipeline.components.data_source import EOSimulator
# Component: IngestionManager (Validates incoming data at the ground station)
from secure_eo_pipeline.components.ingestion import IngestionManager
# Component: ProcessingEngine (Transforms raw signals into scientific products)
from secure_eo_pipeline.components.processing import ProcessingEngine
# Component: ArchiveManager (Handles AES encryption and long-term storage)
from secure_eo_pipeline.components.storage import ArchiveManager
# Component: AccessController (Enforces Identity & Role-Based Access Control)
from secure_eo_pipeline.components.access_control import AccessController
# Component: ResilienceManager (Handles automated backups and self-healing)
from secure_eo_pipeline.resilience.backup_system import ResilienceManager
# Utility: security (Provides the low-level crypto and hashing algorithms)
from secure_eo_pipeline.utils import security

# Initialize the Rich Console - This is our global UI manager
console = Console()

# =============================================================================
# UI HELPER FUNCTIONS - Making the demonstration readable
# =============================================================================

def print_header(title, subtitle):
    """
    Renders a styled header panel at the start of each demonstration scenario.
    """
    # Create a panel that fits the content width
    console.print(Panel.fit(
        f"[bold white]{subtitle}[/bold white]",
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))

def print_step(step_num, description, color="blue"):
    """
    Displays a standardized step header to track pipeline progress.
    """
    # Print the step number in the chosen color and the description
    console.print(f"\n[bold {color}]Step {step_num}:[/bold {color}] {description}")

def print_status(component, status, details, success=True):
    """
    Renders a status row in a table format to show if a component succeeded or failed.
    """
    # Use green for success and red for failure to provide immediate visual feedback
    color = "green" if success else "red"
    # Choose the appropriate icon for the status
    symbol = "✅" if success else "❌"
    
    # Create a minimalist, borderless table for alignment
    table = Table(show_header=False, box=None)
    # Define columns with fixed widths for a consistent look
    table.add_column("Component", style="bold white", width=15)
    table.add_column("Status", style=color, width=10)
    table.add_column("Details", style="dim white")
    
    # Insert the status information as a row
    table.add_row(f"[{component}]", f"{symbol} {status}", details)
    # Output the table to the terminal
    console.print(table)

def print_explanation(text):
    """
    Prints a dim, italicized box explaining the 'Security Rationale' of a step.
    This helps beginners understand WHY the code is doing what it's doing.
    """
    # Prefix with an information icon and use a subtle style
    console.print(f"[dim white italic]   ℹ {text}[/dim white italic]\n")

# =============================================================================
# SCENARIO 1: THE HAPPY PATH (NOMINAL OPERATIONS)
# =============================================================================
# GOAL:
# Walk the user through a perfect end-to-end data lifecycle.
# Lifecycle: Acquisition -> Ingestion -> Processing -> Archiving -> Backup -> Access.
# =============================================================================

def run_scenario_1_happy_path():
    # Step 1: Clear the terminal to focus the user's attention
    console.clear()
    # Step 2: Show the scenario introduction
    print_header("SCENARIO 1", "Nominal Operations (Happy Path)\nGoal: Ingest -> Process -> Archive -> Access")
    
    # Step 3: Instantiate all System Components
    # We create local instances of each class to use their methods
    source = EOSimulator()
    ingest = IngestionManager()
    processor = ProcessingEngine()
    archive = ArchiveManager()
    ac = AccessController()
    backup = ResilienceManager()
    
    # Step 4: Define a unique Product ID for this simulation run
    pid = "Sentinel_2_T32TQC_DEMO"
    
    # --- STEP 1: GENERATION ---
    print_step(1, "Satellite Data Acquisition (Simulation)", "cyan")
    print_explanation("We simulate a satellite capturing an image. At this stage, it's just raw digital signals.")
    
    # Use a Rich status spinner to simulate the time it takes for a downlink
    with console.status("[bold cyan]Simulating satellite downlink...", spinner="earth"):
        time.sleep(1.5) # Artificial pause for realism
        source.generate_product(pid)
        
    # Report that the data has been created successfully
    print_status("DATA SOURCE", "GENERATED", f"Product ID: {pid}", success=True)
    
    # --- STEP 2: INGESTION ---
    print_step(2, "Secure Ingestion & Validation", "cyan")
    print_explanation("The 'Border Control' check. We validate formats and take a SHA-256 fingerprint (Hash).")
    
    with console.status("[bold cyan]Ingesting product...", spinner="dots"):
        time.sleep(1) # Fake processing time
        # Call the actual ingestion component we built
        ingested_path = ingest.ingest_product(pid)
    
    # Check if the ingestion logic returned a valid path (success) or None (failure)
    if ingested_path:
        print_status("INGESTION", "VALIDATED", "Format OK | Schema OK | Hash Calculated", success=True)
    else:
        print_status("INGESTION", "FAILED", "Validation Failed", success=False)
        return # Exit the scenario early on failure
    
    # --- STEP 3: PROCESSING ---
    print_step(3, "Processing & Quality Control (L0 -> L1)", "cyan")
    print_explanation("Raw data is calibrated into science products. We check for 'NaN' values (sensor errors).")
    
    with console.status("[bold cyan]Processing L0 -> L1...", spinner="dots"):
        time.sleep(1.5) # Fake heavy computation delay
        # Call the processing engine
        processed_path = processor.process_product(pid)
    
    if processed_path:
         print_status("PROCESSING", "COMPLETED", "Quality Control Passed | Metadata Updated", success=True)
    else:
        print_status("PROCESSING", "QC FAILED", "Data Corruption Detected", success=False)
        return
    
    # --- STEP 4: ARCHIVING ---
    print_step(4, "Secure Storage (Encryption at Rest)", "cyan")
    print_explanation("We use AES-256 encryption. Even if the disk is stolen, the data is unreadable.")
    
    with console.status("[bold cyan]Encrypting...", spinner="dots"):
        time.sleep(1) # Fake encryption delay
        # Call the archiving manager to encrypt and vault the file
        archived_path = archive.archive_product(pid)
        
    print_status("ARCHIVE", "SECURED", "File Encrypted (AES) | Stored", success=True)
    
    # --- STEP 5: BACKUP ---
    print_step(5, "Resilience Layer (Backup)", "cyan")
    print_explanation("To ensure 'Availability', we immediately clone the encrypted data to a backup zone.")
    
    # Execute the backup replication
    backup.create_backup(pid)
    print_status("BACKUP", "REPLICATED", "Copy created in Backup Zone", success=True)
    
    # --- STEP 6: ACCESS ---
    print_step(6, "User Access & Delivery", "cyan")
    # Simulate an administrator user
    user = "emanuele_admin"
    print_explanation(f"User '{user}' requests access. We check Authentication and Authorization before decrypting.")
    
    # Call the Access Controller to verify if this user is allowed to 'read'
    if ac.authorize(user, "read"):
        print_status("ACCESS CONTROL", "AUTHORIZED", f"Role '{config.USERS[user]}' permitted", success=True)
        # Define the local filename for the delivered product
        outfile = "retrieved_product.npy"
        with console.status("[bold green]Decrypting and delivering product...", spinner="dots"):
            time.sleep(1) # Fake decryption delay
            # Fetch, decrypt, and deliver the file
            archive.retrieve_product(pid, outfile)
        
        # Report delivery success
        print_status("DELIVERY", "SUCCESS", f"Decrypted to {outfile}", success=True)
        # CLEANUP: Remove the delivered file so we don't clutter the user's workspace
        if os.path.exists(outfile): os.remove(outfile) 
    else:
        print_status("ACCESS CONTROL", "DENIED", "Insufficient Permissions", success=False)

    # Display a final success banner
    console.print(Panel("[bold green]SCENARIO 1 COMPLETED SUCCESSFULLY[/bold green]", border_style="green"))


# =============================================================================
# SCENARIO 2: UNAUTHORIZED ACCESS (SECURITY BREACH)
# =============================================================================
# GOAL:
# Prove that our Role-Based Access Control (RBAC) stops hackers.
# =============================================================================

def run_scenario_2_unauthorized_access():
    # Insert vertical spacing
    print("\n\n")
    # Show the scenario header
    print_header("SCENARIO 2", "Security Breach Attempt\nGoal: Block unauthorized user accessing Archive")
    
    # Initialize the Access Controller component
    ac = AccessController()
    # Define the intruder identity
    hacker = "eve_hacker"
    
    # --- STEP 1: LOGIN ---
    print_step(1, "Authentication Attempt", "red")
    print_explanation(f"User '{hacker}' attempts to log in to the system.")
    
    # Attempt to authenticate (this will log a warning in the audit trail)
    ac.authenticate(hacker) 
    
    # --- STEP 2: ACCESS ---
    print_step(2, "Authorization Check", "red")
    print_explanation(f"'{hacker}' tries to read a sensitive product. The system blocks her.")
    
    # Attempt to authorize the 'read' action
    authorized = ac.authorize(hacker, "read")
    
    # Branching logic based on security result
    if authorized:
        # This branch should never be reached in a secure system
        print_status("SECURITY", "BREACHED", "CRITICAL FAILURE: Unauthorized access granted!", success=False)
    else:
        # Success: The system blocked the unauthorized user
         print_status("ACCESS CONTROL", "BLOCKED", f"User '{hacker}' has NO PERMISSIONS. Access Denied.", success=True)
         
    # Show the scenario completion banner
    console.print(Panel("[bold green]SCENARIO 2 COMPLETED: SYSTEM SECURE[/bold green]", border_style="green"))


# =============================================================================
# SCENARIO 3: RESILIENCE (SELF-HEALING)
# =============================================================================
# GOAL:
# Demonstrate how the system detects and repairs "Bit Rot" or data corruption.
# =============================================================================

def run_scenario_3_resilience():
    # Insert vertical spacing
    print("\n\n")
    # Show the scenario header
    print_header("SCENARIO 3", "Data Integrity & Recovery\nGoal: Detect bit-rot/corruption and auto-heal")
    
    # Define a test product ID
    pid = "Resilience_Test_Product"
    
    # Re-initialize all necessary components
    source = EOSimulator()
    ingest = IngestionManager()
    processor = ProcessingEngine()
    archive = ArchiveManager()
    backup = ResilienceManager()
    
    # --- FAST-FORWARD SETUP ---
    # We automatically perform the ingest -> process -> archive -> backup steps
    console.print("[dim]Setting up: Creating valid product and backup...[/dim]")
    source.generate_product(pid)
    ingest.ingest_product(pid)
    processor.process_product(pid)
    archived_path = archive.archive_product(pid)
    backup.create_backup(pid)
    
    # Capture the "Healthy" Hash from the file for our reference
    good_hash = security.calculate_hash(archived_path)
    console.print(f"[green]Original Healthy Hash: {good_hash}[/green]")
    
    # --- STEP 1: ATTACK (CORRUPTION) ---
    print_step(1, "Simulating Physical Data Corruption", "red")
    print_explanation("We intentionally write garbage data to the encrypted file. This simulates hardware failure.")
    
    # Visual alert
    console.print(Panel("[bold red]ALERT: DATA CORRUPTION INJECTED[/bold red]\nWriting garbage bytes to the primary storage disk...", border_style="red"))
    
    # Step 1: Open the encrypted file and overwrite it with junk bytes
    with open(archived_path, "wb") as f:
        f.write(b"CORRUPTED_DATA_BLOCK_X_000")
    
    # Step 2: Recalculate the hash to prove it has changed
    bad_hash = security.calculate_hash(archived_path)
    console.print(f"[red]Corrupted Hash (Now):  {bad_hash}[/red]")
    
    # --- STEP 2: RECOVERY ---
    print_step(2, "System Integrity Verification & Healing", "blue")
    print_explanation("The system runs a health check, finds the mismatch, and pulls the backup.")
    
    # Define a helper function to simulate a secure Hash Catalog
    def get_expected_hash(p):
        return good_hash # Returns the hash we saved earlier
    
    # Trigger the Resilience Manager's verification and restoration logic
    with console.status("[bold red]Integrity check running...", spinner="weather"):
        time.sleep(1) # Fake audit time
        # This will detect the error and restore from backup automatically
        recovered = backup.verify_and_restore(pid, expected_hash_fn=get_expected_hash)
    
    # Step 3: Verify the outcome
    if recovered:
         # Log the successful healing
         print_status("RESILIENCE", "RECOVERED", "Corruption detected -> Backup Restored", success=True)
         print_explanation("The system automatically repaired itself using the backup. The user is unaffected.")
    
    # Step 4: Final Integrity Check
    final_hash = security.calculate_hash(archived_path)
    # If the hash is back to the 'Good' one, we are fully restored
    if final_hash == good_hash:
         console.print(Panel("[bold green]SCENARIO 3 COMPLETED: SELF-HEALING SUCCESSFUL[/bold green]", border_style="green"))

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Step 1: Clean start - Remove any old data from previous runs
    if os.path.exists("simulation_data"):
        # Import and use rmtree to delete the entire directory tree
        import shutil
        shutil.rmtree("simulation_data")
        
    # Step 2: Execute the scenarios in sequence
    # Run Scenario 1: Nominal Flow
    run_scenario_1_happy_path()
    time.sleep(2) # Pause so the user can read the success message
    
    # Run Scenario 2: Security check
    run_scenario_2_unauthorized_access()
    time.sleep(2)
    
    # Run Scenario 3: Recovery check
    run_scenario_3_resilience()
