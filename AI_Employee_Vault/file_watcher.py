"""
File Watcher - Bronze Tier AI Employee

This script monitors the 'Inbox' folder for new files.
When a new file is detected, it creates a corresponding task file
in the 'Needs_Action' folder for review.

Features:
- Checks for new files every 5 seconds
- Prevents duplicate task creation
- Creates structured Markdown task files
- Robust error handling with logging
"""

import os
import time
import traceback
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colors
init(autoreset=True)

# Configuration
INBOX_FOLDER = os.path.join("AI_Employee_Vault", "Inbox")
NEEDS_ACTION_FOLDER = os.path.join("AI_Employee_Vault", "Needs_Action")
NEEDS_APPROVAL_FOLDER = os.path.join("AI_Employee_Vault", "Needs_Approval")
LOGS_FOLDER = os.path.join("AI_Employee_Vault", "Logs")
ERROR_LOG_FILE = os.path.join(LOGS_FOLDER, "watcher_errors.log")
CHECK_INTERVAL_SECONDS = 5

# Track processed files to avoid duplicates
# Stores filenames that have already been processed
processed_files = set()


def initialize_processed_files():
    """
    Initialize processed_files set with existing files and tasks.
    This prevents processing files that were already in Inbox before the watcher started.
    """
    # Add existing Inbox files
    if os.path.exists(INBOX_FOLDER):
        for item in os.listdir(INBOX_FOLDER):
            item_path = os.path.join(INBOX_FOLDER, item)
            if os.path.isfile(item_path):
                processed_files.add(item)
    
    # Add files that already have tasks
    if os.path.exists(NEEDS_ACTION_FOLDER):
        for item in os.listdir(NEEDS_ACTION_FOLDER):
            if item.startswith('task_') and item.endswith('.md'):
                # Extract original filename from task filename
                original_filename = item.replace('task_', '').replace('.md', '')
                processed_files.add(original_filename)
    
    return processed_files


def print_banner():
    """Print a colorful banner for the File Watcher."""
    print(flush=True)
    print(Fore.CYAN + Style.BRIGHT + "=" * 60, flush=True)
    print(Fore.CYAN + Style.BRIGHT + "  [FILE WATCHER] - AI Employee (Bronze Tier)", flush=True)
    print(Fore.CYAN + Style.BRIGHT + "=" * 60, flush=True)
    print(flush=True)


def get_inbox_files():
    """
    Get a list of all files currently in the Inbox folder.
    
    Returns:
        set: A set of filenames (not full paths) in the Inbox folder.
    """
    if not os.path.exists(INBOX_FOLDER):
        return set()
    
    files = set()
    for item in os.listdir(INBOX_FOLDER):
        item_path = os.path.join(INBOX_FOLDER, item)
        # Only process files, not subdirectories
        if os.path.isfile(item_path):
            files.add(item)
    
    return files


def create_task_file(filename):
    """
    Create a structured Markdown task file in the Needs_Action folder.

    Uses the improved task template structure with priority, related files,
    and a clear checklist format.

    Args:
        filename (str): The name of the file that was added to Inbox.
    
    Returns:
        bool: True if task was created successfully, False otherwise.
    """
    try:
        # Generate a timestamp for the task creation
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create a safe task filename by replacing problematic characters
        # Remove or replace characters that aren't valid in filenames
        safe_name = filename.replace(":", "-").replace("/", "-").replace("\\", "-")
        task_filename = f"task_{safe_name}.md"
        task_filepath = os.path.join(NEEDS_ACTION_FOLDER, task_filename)

        # Build the task file content using the improved template structure
        task_content = f"""---
type: file_review
status: pending
priority: medium
created_at: {timestamp}
related_files:
  - AI_Employee_Vault/Inbox/{filename}
---

# Review File: {filename}

## Description
A new file was added to the Inbox folder and requires review.
Determine the file's purpose, contents, and what actions should be taken.

## Checklist
- [ ] Open and review the file contents
- [ ] Identify the file type and purpose
- [ ] Decide what action is needed (archive, process, delete, etc.)
- [ ] Update related task files or create new tasks if needed
- [ ] Move or categorize the file appropriately

## Notes
<!-- Add any reasoning, context, or observations here -->

**Source File:** AI_Employee_Vault/Inbox/{filename}

"""

        # Write the task file
        with open(task_filepath, "w", encoding="utf-8") as f:
            f.write(task_content)

        print(Fore.GREEN + Style.BRIGHT + "  [+] " + Fore.WHITE + f"[{timestamp}] " + Fore.GREEN + f"Created task for: " + Fore.YELLOW + filename, flush=True)
        return True

    except Exception as e:
        # Log the error and return False to indicate failure
        log_error(f"Failed to create task file for '{filename}': {str(e)}")
        return False


def log_activity(message):
    """
    Log an activity message to the console with a timestamp.

    Args:
        message (str): The message to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(Fore.BLUE + Style.BRIGHT + "  [*] " + Fore.WHITE + f"[{timestamp}] " + Fore.CYAN + message, flush=True)


def log_error(error_message):
    """
    Log an error message to the error log file with a timestamp.

    This function ensures errors are recorded even if the console output fails.
    It also creates the Logs folder if it doesn't exist.

    Args:
        error_message (str): The error message to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Ensure the Logs folder exists before writing
        os.makedirs(LOGS_FOLDER, exist_ok=True)

        # Format the error entry with timestamp
        error_entry = f"[{timestamp}] ERROR: {error_message}\n"

        # Append to the error log file
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_entry)

        # Also print to console so the user sees the error immediately
        print(Fore.RED + Style.BRIGHT + "  [X] " + Fore.WHITE + f"[{timestamp}] " + Fore.RED + f"ERROR logged to {ERROR_LOG_FILE}", flush=True)

    except Exception as e:
        # If we can't even write to the log file, print to console as fallback
        print(Fore.RED + Back.WHITE + Style.BRIGHT + f"  [!] [{timestamp}] CRITICAL: Could not write to error log: {e}", flush=True)


def main():
    """
    Main function that runs the file watcher loop.

    This function:
    1. Ensures required folders exist (Inbox, Needs_Action, Logs)
    2. Continuously checks the Inbox folder every 5 seconds
    3. Creates task files for new files detected
    4. Handles errors gracefully without crashing
    """
    print_banner()
    log_activity("File Watcher started")
    log_activity(f"Monitoring folder: {Fore.YELLOW}{INBOX_FOLDER}")
    log_activity(f"Check interval: {Fore.YELLOW}{CHECK_INTERVAL_SECONDS} seconds")
    print(Fore.CYAN + Style.BRIGHT + "-" * 60, flush=True)

    # Ensure required folders exist
    # exist_ok=True means no error if folder already exists
    try:
        os.makedirs(INBOX_FOLDER, exist_ok=True)
        os.makedirs(NEEDS_ACTION_FOLDER, exist_ok=True)
        os.makedirs(NEEDS_APPROVAL_FOLDER, exist_ok=True)
        os.makedirs(LOGS_FOLDER, exist_ok=True)
        print(Fore.GREEN + Style.BRIGHT + "  [*] " + Fore.WHITE + "All required folders ready", flush=True)
    except Exception as e:
        log_error(f"Failed to create required folders: {str(e)}")
        print(Fore.YELLOW + "  [!] Warning: Some folders could not be created. The script may not work correctly.", flush=True)

    # Initialize processed_files with existing files (so we only watch for NEW files)
    initialize_processed_files()
    log_activity(f"Existing files already processed: {len(processed_files)}")
    print(Fore.CYAN + Style.BRIGHT + "-" * 60, flush=True)

    # Main monitoring loop
    # Wrapped in try/except to prevent crashes
    try:
        while True:
            try:
                # Get current files in Inbox
                current_files = get_inbox_files()

                # Find new files (files that haven't been processed yet)
                new_files = current_files - processed_files

                # Process each new file
                for filename in new_files:
                    create_task_file(filename)
                    # Mark as processed to avoid creating duplicate tasks
                    processed_files.add(filename)

            except Exception as e:
                # Catch any error during file processing
                # This prevents the entire script from crashing
                log_error(f"Error during file processing: {str(e)}")
                # Print stack trace for debugging (helpful for beginners)
                print(f"Debug info: {traceback.format_exc()}", flush=True)

            # Wait before the next check
            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        # Handle graceful shutdown when user presses Ctrl+C
        print(flush=True)
        print(Fore.YELLOW + Style.BRIGHT + "\n  [STOP] " + Fore.WHITE + "File Watcher stopped by user", flush=True)
        log_activity("File Watcher stopped")
    except Exception as e:
        # Catch any unexpected errors in the main loop
        log_error(f"Unexpected error in main loop: {str(e)}")
        print(Fore.RED + Back.WHITE + Style.BRIGHT + f"\n  [ERROR] An unexpected error occurred: {e}", flush=True)
        print(Fore.RED + "The script will now exit.", flush=True)


if __name__ == "__main__":
    main()
