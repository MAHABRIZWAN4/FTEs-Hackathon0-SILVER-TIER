"""
Log Manager - Bronze Tier AI Employee

This script prevents log files from growing too large.
It checks log files and archives them if they exceed a size limit.

Features:
- Checks System_Log.md and Logs/watcher_errors.log
- Archives files larger than 1 MB with a timestamp
- Creates fresh empty log files after archiving
- Colorful terminal UI with colorama
"""

import os
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colors
init(autoreset=True)

# Configuration
# Maximum file size in bytes (1 MB = 1024 * 1024 bytes)
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024

# Log files to manage
SYSTEM_LOG = os.path.join("AI_Employee_Vault", "System_Log.md")
WATCHER_ERROR_LOG = os.path.join("AI_Employee_Vault", "Logs", "watcher_errors.log")


def print_banner():
    """Print a colorful banner for the Log Manager."""
    print()
    print(Fore.YELLOW + Style.BRIGHT + "=" * 60)
    print(Fore.YELLOW + Style.BRIGHT + "  [LOG MANAGER] - AI Employee (Bronze Tier)")
    print(Fore.YELLOW + Style.BRIGHT + "=" * 60)
    print()


def get_file_size(filepath):
    """
    Get the size of a file in bytes.

    Args:
        filepath (str): Path to the file.

    Returns:
        int: File size in bytes, or 0 if file doesn't exist.
    """
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0


def archive_log_file(filepath):
    """
    Archive a log file by renaming it with a timestamp.

    Creates a backup of the file with a timestamp in the filename,
    then creates a fresh empty file with the original name.

    Args:
        filepath (str): Path to the log file to archive.

    Returns:
        bool: True if archived successfully, False otherwise.
    """
    try:
        # Check if the file exists before trying to archive
        if not os.path.exists(filepath):
            print(Fore.YELLOW + "  [!] " + Fore.WHITE + f"File does not exist, skipping: {filepath}")
            return False

        # Generate a timestamp for the archive filename
        # Format: YYYY-MM-DD_HH-MM-SS (safe for filenames)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Split the filepath into directory, name, and extension
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        # Create the new archive filename with timestamp
        # Example: System_Log_2026-01-20_14-30-00.md
        archive_filename = f"{name}_{timestamp}{ext}"
        archive_filepath = os.path.join(directory, archive_filename) if directory else archive_filename

        # Rename the original file to the archive filename
        os.rename(filepath, archive_filepath)
        print(Fore.GREEN + Style.BRIGHT + "  [+] " + Fore.WHITE + f"Archived: " + Fore.CYAN + filepath + Fore.WHITE + " -> " + Fore.GREEN + archive_filepath)

        # Create a fresh empty file with the original name
        # For System_Log.md, we add basic structure
        if filepath == SYSTEM_LOG:
            fresh_content = """# System Log

## Activity Log

<!-- Log entries will be added here -->

| Timestamp | Action | Details |
|-----------|--------|---------|
|           |        |         |

"""
        else:
            # For error logs, start with a simple header comment
            fresh_content = f"# Error Log\n# Fresh start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(fresh_content)

        print(Fore.GREEN + "  [*] " + Fore.WHITE + f"Created fresh log file: {filepath}")
        return True

    except Exception as e:
        print(Fore.RED + Style.BRIGHT + "  [X] " + Fore.WHITE + f"Error archiving {filepath}: {e}")
        return False


def check_and_rotate_log(filepath, log_name):
    """
    Check if a log file exceeds the size limit and rotate it if needed.

    Args:
        filepath (str): Path to the log file.
        log_name (str): Friendly name for display purposes.
    """
    # Get the current file size
    size_bytes = get_file_size(filepath)

    # Convert to megabytes for easier reading (optional, for display)
    size_mb = size_bytes / (1024 * 1024)

    # Check if file exceeds the maximum size
    if size_bytes > MAX_FILE_SIZE_BYTES:
        print(Fore.RED + Style.BRIGHT + f"  [#] [{log_name}]" + Fore.WHITE + f" Size: {Fore.RED}{size_mb:.2f} MB" + Fore.WHITE + " - Exceeds limit, archiving...")
        archive_log_file(filepath)
    else:
        print(Fore.GREEN + Style.BRIGHT + f"  [*] [{log_name}]" + Fore.WHITE + f" Size: {Fore.GREEN}{size_mb:.2f} MB" + Fore.WHITE + " - OK")


def main():
    """
    Main function that checks all log files and rotates them if needed.

    This function:
    1. Checks System_Log.md
    2. Checks Logs/watcher_errors.log
    3. Archives any files that exceed the size limit
    """
    print_banner()
    print(Fore.CYAN + f"  Maximum file size: {Fore.YELLOW}{MAX_FILE_SIZE_BYTES / (1024 * 1024):.1f} MB")
    print(Fore.CYAN + "-" * 60)

    # Ensure the Logs folder exists
    os.makedirs(os.path.join("AI_Employee_Vault", "Logs"), exist_ok=True)

    # Check and rotate System_Log.md
    check_and_rotate_log(SYSTEM_LOG, "System_Log.md")

    # Check and rotate watcher_errors.log
    check_and_rotate_log(WATCHER_ERROR_LOG, "AI_Employee_Vault/Logs/watcher_errors.log")

    print(Fore.CYAN + "-" * 60)
    print(Fore.GREEN + Style.BRIGHT + "  [*] " + Fore.WHITE + "Log Manager - Check complete")
    print()


if __name__ == "__main__":
    main()
