import sys
# Used for system-level operations like exit
import os
# Used to interact with the Operating System (files, paths)
import time
# Used for delays to simulate real-world processing time
import random
# Used to generate random product IDs
from rich.console import Console
# Rich library: Provides the main terminal output interface
from rich.panel import Panel
# Rich library: Creates styled boxes/panels
from rich.table import Table
# Rich library: Creates organized data tables
from rich.prompt import Prompt
# Rich library: Handles user input nicely
from rich.layout import Layout
from rich.live import Live

# Import our project configuration (paths, users, roles)
from secure_eo_pipeline import config
# Import the Component that simulates satellite data generation
from secure_eo_pipeline.components.data_source import EOSimulator
# Import the Component that handles secure data ingestion
from secure_eo_pipeline.components.ingestion import IngestionManager
# Import the Component that processes data (L0 -> L1)
from secure_eo_pipeline.components.processing import ProcessingEngine
# Import the Component that manages the secure archive (Encryption)
from secure_eo_pipeline.components.storage import ArchiveManager
# Import the Component that checks permissions (RBAC)
from secure_eo_pipeline.components.access_control import AccessController
# Import the Component that handles backups and recovery
from secure_eo_pipeline.resilience.backup_system import ResilienceManager
# Import security utilities (hashing, etc.)
from secure_eo_pipeline.utils import security

# Instantiate the Global Console object for printing
console = Console()

class InteractiveSession:
    """
    Manages the state and flow of the interactive CLI session.
    Acts as the 'Controller' in this MVC-like architecture.
    """
    
    def __init__(self):
        # Initialize session state variables
        self.current_user = None  # Who is logged in?
        self.current_role = None  # What permissions do they have?
        self.active_product = None  # What satellite image are we working on?
        
        # Instantiate System Components
        # We create instances of our classes to use their methods
        self.source = EOSimulator()
        self.ingest = IngestionManager()
        self.processor = ProcessingEngine()
        self.archive = ArchiveManager()
        self.ac = AccessController()
        self.backup = ResilienceManager()
        
        # System State Tracking
        # This dictionary keeps track of the 'lifecycle' of the active product
        # It's like a checklist verifying what steps have been done
        self.state = {
            "generated": False,  # Step 1: Created?
            "ingested": False,   # Step 2: Ingested?
            "processed": False,  # Step 3: Processed?
            "archived": False,   # Step 4: Encrypted?
            "hacked": False      # Status: Compromised?
        }

    def clear(self):
        """
        Clears the terminal screen and repaints the banner.
        Keeps the UI fresh and clean.
        """
        console.clear()
        self.print_banner()

    def print_banner(self):
        """
        Displays the main application header and status bar.
        """
        # Print the fixed title panel
        console.print(Panel(
            "[bold cyan]SECURE EARTH OBSERVATION PIPELINE[/bold cyan]\n"
            "[italic white]Interactive Operator Console (Level 2)[/italic white]",
            border_style="cyan",
            expand=False
        ))
        
        # Determine how to display the current user status
        # If logged in -> Green Name. If not -> Red Warning.
        user_display = f"[green]{self.current_user}[/green]" if self.current_user else "[red]Not Logged In[/red]"
        role_display = f"({self.current_role})" if self.current_role else ""
        
        # Determine how to display the active product
        # If we have one -> Blue ID. If not -> Dim None.
        product_display = f"[blue]{self.active_product}[/blue]" if self.active_product else "[dim]None[/dim]"
        
        # Create a grid (invisible table) for the Status Bar
        grid = Table.grid(expand=True)
        grid.add_column()  # Left column
        grid.add_column(justify="right")  # Right column
        
        # Add the status info to the grid
        grid.add_row(
            f"User: {user_display} {role_display}", 
            f"Active Target: {product_display}"
        )
        
        # Print the grid inside a panel
        console.print(Panel(grid, style="dim white"))

    def help_menu(self):
        """
        Prints the table of available commands to the user.
        """
        # Create a cleaner table without borders
        table = Table(title="Available Commands", box=None)
        
        # Define Columns
        table.add_column("Command", style="bold cyan")
        table.add_column("Description", style="white")
        
        # Add Rows for each capability
        table.add_row("login", "Log in to the system (e.g., as 'alice_admin' or 'bob_analyst')")
        table.add_row("logout", "Disconnect current session")
        table.add_row("scan", "Search for new satellite data (Generate)")
        table.add_row("ingest", "Securely import the detected data")
        table.add_row("process", "Run L0->L1 processing and QC")
        table.add_row("archive", "Encrypt and store data in the vault")
        table.add_row("hack", "Simulate a cyber-attack (Corruption)")
        table.add_row("recover", "Attempt disaster recovery from backup")
        table.add_row("status", "View current product lifecycle status")
        table.add_row("exit", "Quit validation tool")
        
        # Render the table to screen
        console.print(table)

    def print_status_panel(self):
        """
        Shows the lifecycle checklist (Generated, Ingested, etc.)
        """
        table = Table(box=None)
        table.add_column("Stage")
        table.add_column("Status")
        
        # Loop through the state dictionary keys
        stages = ["generated", "ingested", "processed", "archived", "hacked"]
        for s in stages:
            # Default is "NO" (dim color)
            status = "[green]YES[/green]" if self.state[s] else "[dim]NO[/dim]"
            
            # Special case for "hacked": if true, it's RED (bad)
            if s == "hacked" and self.state[s]: 
                status = "[bold red]COMPROMISED[/bold red]"
                
            table.add_row(s.upper(), status)
            
        console.print(Panel(table, title="Product Lifecycle Status"))

    def login(self):
        """
        Handles user authentication dialog.
        """
        console.print("\n[bold]Available Users:[/bold]")
        # Show the list of valid users from config so the user knows what to type
        for u, r in config.USERS.items():
            console.print(f" - {u} ({r})")
            
        # Ask for input
        user = Prompt.ask("\nUsername")
        
        # Authenticate via Access Controller
        role = self.ac.authenticate(user)
        
        if role:
            # Success: Update session state
            self.current_user = user
            self.current_role = role
            console.print(f"[green]✔ Login Successful. Welcome, {user}.[/green]")
        else:
            # Failure: Warn user
            console.print("[red]❌ Login Failed. User unknown.[/red]")

    def check_auth(self, action):
        """
        Helper to check if current user can do X.
        """
        # 1. Are they logged in?
        if not self.current_user:
            console.print("[red]❌ Access Denied: Please Login first.[/red]")
            return False
            
        # 2. Do they have permission?
        if self.ac.authorize(self.current_user, action):
            return True
        else:
            console.print(f"[red]❌ Authorization Failed: '{self.current_user}' cannot perform '{action}'.[/red]")
            return False

    def check_prereq(self, prereq_key, step_name):
        """
        Helper to enforce linear pipeline order.
        Example: Cannot 'archive' before 'process'.
        """
        # Check if we even have a product selected
        if not self.active_product:
             console.print("[yellow]⚠ No active product found. Run 'scan' first.[/yellow]")
             return False
        
        # Check if the previous step was completed successfully
        if prereq_key and not self.state[prereq_key]:
             console.print(f"[yellow]⚠ Cannot {step_name}: Previous step failed or skipped.[/yellow]")
             return False
        return True

    def scan(self):
        """
        Step 1: Generate Data.
        """
        # Allow generating without auth usually, but let's encourage login
        if not self.current_user:
             console.print("[italic]Note: You are scanning anonymously.[/italic]")
        
        # Generate a random Product ID for this session
        pid = f"Sentinel_2_{random.randint(1000,9999)}_Orbit{random.randint(10,99)}"
        
        # Show a spinner to look cool
        with console.status("[cyan]Scanning for downlink signal...[/cyan]", spinner="earth"):
            time.sleep(2) # Fake wait
            # Create the data on disk
            self.source.generate_product(pid)
        
        # Update State
        self.active_product = pid
        self.state["generated"] = True
        
        console.print(f"[green]✔ Signal Acquired.[/green] New Product ID: [bold]{pid}[/bold]")
        console.print("[dim italic]ℹ  Raw data represents digital signal from the satellite.[/dim italic]")

    def ingest(self):
        """
        Step 2: Ingest Data.
        Requires 'process' permission (analyst/admin).
        """
        # Check permissions
        if not self.check_auth("process"): return  
        # Check flow (Must be generated first)
        if not self.check_prereq("generated", "Ingest"): return
        
        console.print("[dim italic]ℹ  Validating metadata, calculating initial SHA-256 hash...[/dim italic]")
        
        with console.status("[cyan]Ingesting...[/cyan]"):
            # Call the Ingestion Component
            path = self.ingest.ingest_product(self.active_product)
        
        if path:
            self.state["ingested"] = True
            console.print("[green]✔ Ingestion Complete.[/green] Product is now in the secure boundary.")
        else:
            console.print("[red]❌ Ingestion Failed.[/red]")

    def process(self):
        """
        Step 3: Process Data (L0 -> L1).
        """
        if not self.check_auth("process"): return
        if not self.check_prereq("ingested", "Process"): return
        
        console.print("[dim italic]ℹ  Running radiometric calibration and Quality Control (finding bad pixels)...[/dim italic]")
        with console.status("[cyan]Processing L0 -> L1...[/cyan]", spinner="dots"):
            time.sleep(1.5)
            # Call the Processor Component
            path = self.processor.process_product(self.active_product)
            
        if path:
            self.state["processed"] = True
            console.print("[green]✔ Processing Complete.[/green] Data is Level-1 certified.")
        else:
            console.print("[red]❌ Processing Failed (QC Error).[/red]")

    def archive(self):
        """
        Step 4: Archive (Encrypt).
        Requires 'write' permission.
        """
        if not self.check_auth("write"): return 
        if not self.check_prereq("processed", "Archive"): return
        
        console.print("[dim italic]ℹ  Encrypting with AES-256 and moving to Vault...[/dim italic]")
        with console.status("[cyan]Encrypting...[/cyan]", spinner="lock"):
            time.sleep(1.5)
            # Call Archive Manager
            self.archive.archive_product(self.active_product)
            # Immediately back up!
            self.backup.create_backup(self.active_product)
            
        self.state["archived"] = True
        console.print("[green]✔ Archived & Backed Up.[/green] Data is safe at rest.")

    def hack(self):
        """
        Simulate an attack.
        No permissions needed - Hackers don't need permission!
        """
        # Check if there is anything to hack
        if not self.active_product or not self.state["archived"]:
            console.print("[yellow]⚠ Nothing to hack! Archive some data first.[/yellow]")
            return
            
        console.print("[bold red]☠  INITIATING CYBER ATTACK...[/bold red]")
        console.print("[dim italic]ℹ  Injecting garbage bytes into the primary storage disk...[/dim italic]")
        
        # Construct path to the target file
        target = os.path.join(config.ARCHIVE_DIR, f"{self.active_product}.enc")
        
        if os.path.exists(target):
            # Overwrite the file with junk (CORRUPTION)
            with open(target, "wb") as f:
                f.write(b"CORRUPTED_BY_USER_CMD")
                
            self.state["hacked"] = True
            console.print(f"[red]✔ Data Corrupted.[/red] Hash mismatch created.")
        else:
            console.print("[red]❌ Attack failed: File not found.[/red]")

    def recover(self):
        """
        Recover from attack.
        Requires 'manage_keys' permission (Admin only).
        """
        if not self.check_auth("manage_keys"): return
        if not self.check_prereq("archived", "Recover"): return
        
        console.print("[dim italic]ℹ  Checking integrity hashes against backup...[/dim italic]")
        
        # Define a helper to get the "Known Good Hash" from the backup
        # This simulates having a separate secure catalog
        def get_expected_hash(p):
            # Calculate hash of backup file
            bk_path = os.path.join(config.BACKUP_DIR, f"{p}.enc")
            return security.calculate_hash(bk_path)

        with console.status("[green]Healing...[/green]", spinner="material"):
            time.sleep(2) # Fake processing time
            # Trigger recovery Logic
            fixed = self.backup.verify_and_restore(self.active_product, get_expected_hash)
            
        if fixed:
            self.state["hacked"] = False
            console.print("[green]✔ System Restored.[/green] Resilience mechanisms successful.")
        else:
             console.print("[red]❌ Recovery Failed.[/red]")
             
    def run(self):
        """
        Main Event Loop.
        """
        self.clear()
        console.print("Type [bold cyan]help[/bold cyan] to see commands.")
        
        # Infinite Loop until 'exit'
        while True:
            try:
                # Refresh status UI
                self.print_banner()
                
                # Get User Input
                cmd = Prompt.ask("COMMAND").strip().lower()
                
                # Dispatcher Logic (Switch Case)
                if cmd == "exit":
                    console.print("[bold]Goodbye.[/bold]")
                    break
                elif cmd == "help":
                    self.help_menu()
                elif cmd == "status":
                    self.print_status_panel()
                elif cmd == "login":
                    self.login()
                elif cmd == "logout":
                    # Clear session info
                    self.current_user = None
                    self.current_role = None
                    console.print("Logged out.")
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
                    pass # Do nothing on empty enter
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
                
                # Pause so user can read result
                input("\nPress Enter to continue...")
                console.clear()
                
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                console.print("\n[bold]Session Terminated.[/bold]")
                break
            except Exception as e:
                 # Catch-all for crashes
                console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    # Startup Check: Clean environment?
    if os.path.exists("simulation_data"):
        # We clean the data folder to start fresh each run
        import shutil
        shutil.rmtree("simulation_data")
        
    # Launch the application
    session = InteractiveSession()
    session.run()
