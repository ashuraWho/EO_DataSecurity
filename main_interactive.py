# Import the standard sys module for system-specific parameters and functions (like exit)
import sys
# Import the os module for interacting with the operating system (files, directories)
import os
# Import time to add realistic delays into the command execution flow
import time
# Import random to generate unpredictable product identifiers
import random
# Import components from the Rich library to build a modern terminal user interface
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.layout import Layout
from rich.live import Live

# Import the project's central configuration settings
from secure_eo_pipeline import config
# Import the Satellite Simulator component
from secure_eo_pipeline.components.data_source import EOSimulator
# Import the Secure Ingestion component
from secure_eo_pipeline.components.ingestion import IngestionManager
# Import the L0->L1 Processing component
from secure_eo_pipeline.components.processing import ProcessingEngine
# Import the Encrypted Archive component
from secure_eo_pipeline.components.storage import ArchiveManager
# Import the RBAC Access Controller component
from secure_eo_pipeline.components.access_control import AccessController
# Import the Resilience and Backup component
from secure_eo_pipeline.resilience.backup_system import ResilienceManager
# Import cryptographic and hashing utilities
from secure_eo_pipeline.utils import security

# Instantiate a global Rich Console for all printing operations
console = Console()

class InteractiveSession:
    """
    Controller class that manages the state and command loop of the CLI application.
    """

    def __init__(self):
        """
        Initializes the session state and instantiates all system components.
        """
        # --- SESSION STATE ---
        self.current_user = None  # Stores the username of the logged-in operator
        self.current_role = None  # Stores the RBAC role (admin/analyst/user)
        self.active_product = None  # Stores the ID of the product currently being processed

        # --- COMPONENT INSTANTIATION ---
        # We rename these attributes to avoid shadowing the command methods (e.g., self.ingest())
        self.source_tool = EOSimulator()
        self.ingest_tool = IngestionManager()
        self.processor_tool = ProcessingEngine()
        self.archive_tool = ArchiveManager()
        self.ac_tool = AccessController()
        self.backup_tool = ResilienceManager()

        # --- PIPELINE TRACKING ---
        # This dictionary tracks the completion status of each lifecycle stage
        self.state = {
            "generated": False,  # Step 1: Raw data created
            "ingested": False,   # Step 2: Validated and fingerprinted
            "processed": False,  # Step 3: Calibrated and QC checked
            "archived": False,   # Step 4: Encrypted and vaulted
            "hacked": False      # Simulation status: Data corrupted on disk
        }

    def clear(self):
        """
        Refreshes the terminal screen and repaints the application header.
        """
        # Standard Rich clear command
        console.clear()
        # Repaint the top banner
        self.print_banner()

    def print_banner(self):
        """
        Displays the main application branding and real-time session status.
        """
        # Render the main project title in a cyan panel
        console.print(Panel(
            "[bold cyan]SECURE EARTH OBSERVATION PIPELINE[/bold cyan]\n"
            "[italic white]Interactive Operator Console (V1.0)[/italic white]",
            border_style="cyan",
            expand=False
        ))

        # --- DYNAMIC STATUS BAR ---
        # Format the user display based on login status
        user_display = f"[green]{self.current_user}[/green]" if self.current_user else "[red]Not Logged In[/red]"
        role_display = f"({self.current_role})" if self.current_role else ""

        # Format the product display
        product_display = f"[blue]{self.active_product}[/blue]" if self.active_product else "[dim]None[/dim]"

        # Create an invisible grid for aligned layout
        grid = Table.grid(expand=True)
        grid.add_column()  # Column for User info
        grid.add_column(justify="right")  # Column for Product info

        # Add the status row to the grid
        grid.add_row(
            f"User: {user_display} {role_display}",
            f"Active Target: {product_display}"
        )

        # Wrap the grid in a dim white panel for visual separation
        console.print(Panel(grid, style="dim white"))

    def help_menu(self):
        """
        Prints the command reference table for the operator.
        """
        # Create a table to organize commands and descriptions
        table = Table(title="Available Operator Commands", box=None)

        # Define the header columns
        table.add_column("Command", style="bold cyan")
        table.add_column("Description", style="white")

        # Populate the table with system capabilities
        table.add_row("login", "Authenticate with your mission credentials")
        table.add_row("logout", "Terminate the current secure session")
        table.add_row("scan", "Acquire new raw signal from Satellite (L0)")
        table.add_row("ingest", "Verify, fingerprint, and stage data")
        table.add_row("process", "Run calibration and Quality Control (L1)")
        table.add_row("archive", "Apply AES-256 encryption and vault data")
        table.add_row("hack", "SIMULATION: Corrupt the primary archive disk")
        table.add_row("recover", "Trigger automated hash-audit and repair")
        table.add_row("status", "Show lifecycle checklist for active target")
        table.add_row("exit", "Close the console")

        # Output the table to the console
        console.print(table)

    def print_status_panel(self):
        """
        Displays a visual checklist of the product's progress through the pipeline.
        """
        # Create a simple status table
        table = Table(box=None)
        table.add_column("Lifecycle Stage")
        table.add_column("Status")

        # Iterate through defined stages
        stages = ["generated", "ingested", "processed", "archived", "hacked"]
        for s in stages:
            # Determine the status label based on the state dictionary
            status = "[green]COMPLETED[/green]" if self.state[s] else "[dim]PENDING[/dim]"

            # Special formatting for the 'Hacked' status (Red indicates danger)
            if s == "hacked" and self.state[s]:
                status = "[bold red]CORRUPTED[/bold red]"

            # Add the row to the table
            table.add_row(s.upper(), status)

        # Wrap the table in a panel for the final UI
        console.print(Panel(table, title="Product Verification Status"))

    def login(self):
        """
        Authenticates an operator using the Access Control component.
        """
        console.print("\n[bold underline]Mission Personnel Directory:[/bold underline]")
        # Display valid users to assist the simulation operator
        for u, r in config.USERS.items():
            console.print(f" - {u} (Role: {r})")

        # Capture user input
        user = Prompt.ask("\nEnter Username")

        # Call the Access Controller to verify credentials and retrieve role
        role = self.ac_tool.authenticate(user)

        if role:
            # Update the session state upon success
            self.current_user = user
            self.current_role = role
            console.print(f"[green]✔ Access Granted. Welcome, Operator {user}.[/green]")
        else:
            # Report failure
            console.print("[red]❌ Access Denied. Identity not recognized.[/red]")

    def check_auth(self, action):
        """
        Validates if the current operator is authorized to perform a specific action.

        RETURNS:
            bool: True if authorized, False otherwise.
        """
        # Step 1: Check if anyone is even logged in
        if not self.current_user:
            console.print("[red]❌ Error: Authentication Required. Please 'login'.[/red]")
            return False

        # Step 2: Query the Access Controller for granular permission check
        if self.ac_tool.authorize(self.current_user, action):
            # Permission granted
            return True
        else:
            # Permission denied based on RBAC policy
            console.print(f"[red]❌ Error: Unauthorized. '{self.current_user}' lacks '{action}' rights.[/red]")
            return False

    def check_prereq(self, prereq_key, step_name):
        """
        Enforces the linear flow of the data pipeline.
        Ensures users don't try to archive data that hasn't been processed yet.
        """
        # Step 1: Ensure we have a product to work on
        if not self.active_product:
             console.print("[yellow]⚠ Warning: No active target selected. Run 'scan' first.[/yellow]")
             return False

        # Step 2: Ensure the preceding step was completed successfully
        if prereq_key and not self.state[prereq_key]:
             console.print(f"[yellow]⚠ Warning: Cannot {step_name}. Prerequisites not met.[/yellow]")
             return False
        return True

    def scan(self):
        """
        COMMAND: scan
        Generates a new raw satellite product (Level-0).
        """
        # Allow scanning without auth for the demo, but show a note
        if not self.current_user:
             console.print("[italic]Operating in Anonymous Mode...[/italic]")

        # Create a semi-random ID to simulate a mission product name
        pid = f"Sentinel_2_{random.randint(1000,9999)}_Orbit{random.randint(10,99)}"

        # Display a high-tech loading spinner
        with console.status("[cyan]Listening for satellite downlink signal...[/cyan]", spinner="earth"):
            time.sleep(2) # Simulate the duration of a signal pass
            # Call the Simulator component to create files on disk
            self.source_tool.generate_product(pid)

        # Update session state
        self.active_product = pid
        self.state["generated"] = True

        # Report success
        console.print(f"[green]✔ Signal Locked.[/green] New Target: [bold]{pid}[/bold]")
        console.print("[dim italic]ℹ  Metadata validated and Level-0 binary generated.[/dim italic]")

    def ingest(self):
        """
        COMMAND: ingest
        Validates the raw data and creates the initial integrity hash.
        """
        # Step 1: Check if user has permission to 'process' data
        if not self.check_auth("process"): return
        # Step 2: Check if data was even generated
        if not self.check_prereq("generated", "Ingest"): return

        console.print("[dim italic]ℹ  Validating schema and baselining SHA-256 integrity...[/dim italic]")

        with console.status("[cyan]Performing Secure Ingestion...[/cyan]"):
            # Call the Ingestion component logic
            path = self.ingest_tool.ingest_product(self.active_product)

        if path:
            # Success: Mark state
            self.state["ingested"] = True
            console.print("[green]✔ Ingestion successful.[/green] Data fingerprinted and staged.")
        else:
            # Failure (e.g. invalid metadata)
            console.print("[red]❌ Ingestion failed validation.[/red]")

    def process(self):
        """
        COMMAND: process
        Converts raw data to scientific products and checks quality.
        """
        # Step 1: Authorization
        if not self.check_auth("process"): return
        # Step 2: Pipeline Order
        if not self.check_prereq("ingested", "Process"): return

        console.print("[dim italic]ℹ  Applying radiometric calibration and checking for sensor noise...[/dim italic]")
        with console.status("[cyan]Processing Level-0 -> Level-1...[/cyan]", spinner="dots"):
            time.sleep(1.5) # Simulate computation time
            # Call the Processing component
            path = self.processor_tool.process_product(self.active_product)

        if path:
            # Success
            self.state["processed"] = True
            console.print("[green]✔ Processing successful.[/green] Level-1C product ready.")
        else:
            # Failure (e.g. QC failure due to NaN values)
            console.print("[red]❌ Processing failed Quality Control check.[/red]")

    def archive(self):
        """
        COMMAND: archive
        Encrypts the product and stores it in the high-security vault.
        """
        # Step 1: Authorization (Requires 'write' permission)
        if not self.check_auth("write"): return
        # Step 2: Pipeline Order
        if not self.check_prereq("processed", "Archive"): return

        console.print("[dim italic]ℹ  Executing AES-256 encryption and replicating to backup...[/dim italic]")
        with console.status("[cyan]Vaulting Product...[/cyan]", spinner="dots"):
            time.sleep(1.5)
            # 1. Move to Encrypted Archive
            self.archive_tool.archive_product(self.active_product)
            # 2. Immediately create a redundant backup for resilience
            self.backup_tool.create_backup(self.active_product)

        # Update state
        self.state["archived"] = True
        console.print("[green]✔ Archiving successful.[/green] Data is encrypted-at-rest.")

    def hack(self):
        """
        COMMAND: hack
        Simulates an external attack that corrupts data on the storage disk.
        """
        # Verify there is actually an archived product to attack
        if not self.active_product or not self.state["archived"]:
            console.print("[yellow]⚠ Error: No archived data found to simulate an attack upon.[/yellow]")
            return

        console.print("[bold red]☠  INITIATING SIMULATED DATA CORRUPTION...[/bold red]")

        # Determine the physical path of the vaulted file
        target = os.path.join(config.ARCHIVE_DIR, f"{self.active_product}.enc")

        if os.path.exists(target):
            # MALICIOUS ACTION: Overwrite the encrypted bytes with garbage text
            with open(target, "wb") as f:
                f.write(b"MALICIOUS_CORRUPTION_EVENT_000")

            # Update state to reflect corruption
            self.state["hacked"] = True
            console.print(f"[red]✔ Attack successful.[/red] Primary data file has been corrupted.")
        else:
            console.print("[red]❌ Attack failed: File not located.[/red]")

    def recover(self):
        """
        COMMAND: recover
        Uses resilience mechanisms to detect and repair the corruption.
        """
        # Requires high-level 'manage_keys' permission (Admin only)
        if not self.check_auth("manage_keys"): return
        # Must be an archived product
        if not self.check_prereq("archived", "Recover"): return

        console.print("[dim italic]ℹ  Auditing storage integrity against secondary backup...[/dim italic]")

        # Define a callback to fetch the "Known Good Hash" from the backup vault
        def get_expected_hash(p):
            bk_path = os.path.join(config.BACKUP_DIR, f"{p}.enc")
            # Calculate the hash of the backup (trusted copy)
            return security.calculate_hash(bk_path)

        with console.status("[green]Healing System...[/green]", spinner="dots"):
            time.sleep(2) # Simulate audit and data transfer time
            # Trigger the Resilience Manager's recovery logic
            fixed = self.backup_tool.verify_and_restore(self.active_product, get_expected_hash)

        if fixed:
            # Success: Corruption repaired
            self.state["hacked"] = False
            console.print("[green]✔ Recovery successful.[/green] System integrity restored.")
        else:
             # Failure: Could not recover
             console.print("[red]❌ Recovery failed. Backup may also be compromised.[/red]")

    def run(self):
        """
        The main application loop that handles user input and command dispatching.
        """
        self.clear()
        console.print("System online. Type [bold cyan]help[/bold cyan] for commands.")

        # Continuous loop until 'exit' command
        while True:
            try:
                # Repaint the UI banner each time
                self.print_banner()

                # Prompt the operator for the next command
                cmd = Prompt.ask("MISSION_CONTROL> ").strip().lower()

                # --- COMMAND DISPATCHER ---
                if cmd == "exit":
                    console.print("[bold]Console Session Terminated.[/bold]")
                    break
                elif cmd == "help":
                    self.help_menu()
                elif cmd == "status":
                    self.print_status_panel()
                elif cmd == "login":
                    self.login()
                elif cmd == "logout":
                    # Reset session variables
                    self.current_user = None
                    self.current_role = None
                    console.print("Logged out successfully.")
                elif cmd == "scan":
                    self.scan()
                elif cmd == "ingest":
                    self.ingest()
                elif cmd == "process":
                    self.process()
                elif cmd == "archive":
                    self.archive()
                elif cmd == "hack":
                    self.hack()
                elif cmd == "recover":
                    self.recover()
                elif cmd == "":
                    # Do nothing for empty input
                    pass
                else:
                    # Inform the user of invalid input
                    console.print(f"[red]Error: Unknown mission command '{cmd}'.[/red]")

                # Pause the screen so the operator can review the result
                input("\n[Press Enter to return to console]")
                self.clear()

            except KeyboardInterrupt:
                # Graceful handling of Ctrl+C
                console.print("\n[bold]Emergency Stop: Session Terminated.[/bold]")
                break
            except Exception as e:
                 # Catch and report any unhandled crashes to keep the console alive
                console.print(f"[bold red]SYSTEM ERROR:[/bold red] {e}")

if __name__ == "__main__":
    # --- STARTUP ENVIRONMENT CLEANING ---
    if os.path.exists("simulation_data"):
        # Import shutil to delete old artifacts and start with a clean slate
        import shutil
        shutil.rmtree("simulation_data")

    # --- LAUNCH APPLICATION ---
    session = InteractiveSession()
    session.run()
